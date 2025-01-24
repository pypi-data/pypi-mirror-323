import sys
# module_2.py
sys.path.append(os.path.join(os.path.dirname(__file__), '../B_HIT'))
from tl import calculate_high_density_regions
from pl import enrichment_score
import scanpy as sc


# 读取原始数据
adata = sc.read('/home/yuanrh/cancerdata/onesample.h5ad')
signature = ["CD79A", "CD79B", "MS4A1", "CD79A", 'CD79B', "MZB1", "JCHAIN", "IGHA1", 'IGHG1', 'IGHG3']
score_name = 'Bcell_enrichment'
high_binSize = 100
sc.tl.score_genes(adata, gene_list=signature, score_name=score_name)
adata = adata[adata.obs[score_name]>0] 
calculate_high_density_regions(adata, score_name)
enrichment_score(adata, score_name=score_name, if_filtered=True)