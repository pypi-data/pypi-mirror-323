import scanpy as sc
import matplotlib.pyplot as plt

def enrichment_score(adata_tmp, score_name, if_filtered=False):
    """
    Plot the spatial data, either the original or filtered based on the `if_filtered` parameter.
    
    Parameters:
    - adata_tmp: AnnData object, the spatial data.
    - score_name: str, the name of the score (e.g., Bcell_enrichment) to color the plot.
    - if_filtered: bool, whether to plot the filtered data (True) or the original data (False).
    """
    fig, axes = plt.subplots(figsize=(12, 6))

    if if_filtered:
        # Plot the filtered spatial data
        sc.pl.spatial(adata_tmp[isin_], color=score_name, ax=axes[1], show=False, spot_size=50)
        axes[1].set_title( score_name + "(Filtered)")
    else:
        # Plot the original spatial data
        sc.pl.spatial(adata_tmp, color=score_name, ax=axes[0], show=False, spot_size=50)
        axes[0].set_title( score_name + "(Original)")
    
    plt.show()
