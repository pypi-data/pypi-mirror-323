from joblib import Parallel, delayed
from sklearn.neighbors import KernelDensity
from collections import defaultdict
import numpy as np
from scipy.ndimage import binary_opening
import multiprocessing
import time

def kde_filter(
    adata_tmp,
    score_name,
    high_binSize=100,
    default_thread_num=36,
    clean_mask_size=(3, 3),

):
    """
    Filter spatial coordinates based on KDE clustering.

    Args:
        adata_tmp (AnnData): Input AnnData object.
        score_name (str): Name of the score column in `.obs`.
        high_binSize (int): Grid size for KDE estimation.
        default_thread_num (int): Number of threads for parallel processing.
        clean_mask_size (Tuple[int, int]): Size of the structure for binary cleaning.

    Returns:
        adata_filtered: Filtered AnnData object.
        mask: Boolean mask of selected coordinates.

    
    """
    # Extract spatial coordinates and scores
    start_time = time.time()
    positions_original = adata_tmp.obsm['spatial']
    x = positions_original[:, 0]
    y = positions_original[:, 1]
    Z = np.array(adata_tmp.obs[score_name]).astype(np.float32)

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    bandwidth = int(high_binSize / 3)

    points = np.vstack([x, y]).T
    xy_dict = defaultdict(list)
    for i in range(len(x)):
        Bx = (x[i] - x_min) // high_binSize * high_binSize + x_min
        By = (y[i] - y_min) // high_binSize * high_binSize + y_min
        xy_dict[(Bx, By)].append([x[i], y[i]])

    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth)
    kde.fit(points, sample_weight=Z)

    x_grid, y_grid = np.meshgrid(
        np.arange(x_min, x_max, high_binSize),
        np.arange(y_min, y_max, high_binSize)
    )
    positions = np.vstack([x_grid.ravel(), y_grid.ravel()]).T
    print(f"Step 1 (Prepare): {time.time() - start_time:.2f} s")
    
    # Calculate KDE density
    start_time = time.time()
    num_cores = min(multiprocessing.cpu_count(), default_thread_num)
    density = Parallel(n_jobs=num_cores)(
        delayed(lambda pos: np.exp(kde.score_samples([pos])))(pos)
        for pos in positions
    )
    density = np.array(density).reshape(x_grid.shape)
    print(f"Step 2 (kde score): {time.time() - start_time:.2f} s")

    # Apply threshold and clean mask
    start_time = time.time()
    density_thresholded = np.percentile(density.ravel(), 65)
    binary_mask = ~np.isnan(density > density_thresholded)
    cleaned_mask = binary_opening(binary_mask, structure=np.ones(clean_mask_size))

    density_cleaned = np.where(cleaned_mask, density, np.nan)
    mask = ~np.isnan(density_cleaned)

    x_coords = x_grid[mask]
    y_coords = y_grid[mask]
    coords = np.vstack([x_coords, y_coords]).T

    # Map grid to original positions
    original_coords = []
    for coord in coords:
        original_coords += xy_dict[tuple(coord)]
    original_coords_set = {tuple(row) for row in original_coords}

    isin_ = [tuple(pos) in original_coords_set for pos in positions_original]
    print(f"Step 3 (obtain legal coords): {time.time() - start_time:.2f} s")
    
    adata_tmp.obs['filtered_coords'] = isin_


    return adata_tmp[isin_]
