import scanpy as sc
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def kde_masks(adata_tmp, score_name, plot_original=True, figsize=(15, 5), spot_size=50):
    """
    Plot binary_mask and mask, with an optional plot of the original image.

    Parameters
        adata_tmp: AnnData
            AnnData object containing the data and masks.
        score_name: str 
            The gene or feature name used for plotting the original image.
        plot_original: 
            bool Whether to plot the original image. Defaults to True.
        figsize: 
            tuple Size of the figure. Defaults to: (15, 5).
        spot_size: 
            int Size of the points. Defaults to 50.
    """

    if "binary_mask" not in adata_tmp.obsm or "mask" not in adata_tmp.obsm:
        raise ValueError("binary_mask or mask isn's stored in adata_tmp.obsm!")

    binary_mask = adata_tmp.obsm["binary_mask"]
    mask = adata_tmp.obsm["mask"]

    ncols = 3 if plot_original else 2
    fig, axes = plt.subplots(1, ncols, figsize=figsize)

    if plot_original:
        sc.pl.spatial(adata_tmp, color=score_name, ax=axes[0], show=False, spot_size=spot_size)
        axes[0].set_title("Original Data")

    ax_idx = 1 if plot_original else 0
    axes[ax_idx].matshow(binary_mask, cmap=ListedColormap(['silver', 'indianred']))
    axes[ax_idx].set_title("Binary Mask")
 
    ax_idx = 2 if plot_original else 1
    axes[ax_idx].matshow(mask, cmap=ListedColormap(['silver', 'indianred']))
    axes[ax_idx].set_title("Mask")

    plt.tight_layout()
    plt.show()