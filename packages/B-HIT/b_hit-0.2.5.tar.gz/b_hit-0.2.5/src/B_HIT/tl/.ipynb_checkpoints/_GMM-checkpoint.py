import logging
import torch
from torchgmm.bayes import GaussianMixture as TorchGaussianMixture
from torchgmm.bayes.gmm.lightning_module import GaussianMixtureLightningModule
from torchgmm.bayes.gmm.model import GaussianMixtureModel
from torchgmm.base.data import (
    DataLoader,
    TensorLike,
    collate_tensor,
    dataset_from_tensors,
)

from pytorch_lightning import Trainer
from typing import List, Tuple, cast, Union
from tqdm.auto import tqdm
from scipy.sparse import spdiags
import anndata as ad
import numpy as np
import pandas as pd
import scipy.sparse as sps


AnyRandom = Union[int, np.random.RandomState, None]

class GaussianMixture(TorchGaussianMixture):

    model_: GaussianMixtureModel
    #: The average per-datapoint negative log-likelihood at the last training step.

    def __init__(
        self,
        n_clusters: int = 1,
        covariance_type: str = "full",
        init_strategy: str = "kmeans",
        init_means: torch.Tensor = None,
        convergence_tolerance: float = 0.001,
        covariance_regularization: float = 1e-06,
        batch_size: int = None,
        trainer_params: dict = None,
        random_state: AnyRandom = 0,
    ):
        super().__init__(
            num_components=n_clusters,
            covariance_type=covariance_type,
            init_strategy=init_strategy,
            init_means=init_means,
            convergence_tolerance=convergence_tolerance,
            covariance_regularization=covariance_regularization,
            batch_size=batch_size,
            trainer_params=trainer_params,
        )
        self.n_clusters = n_clusters
        self.random_state = random_state

    def score(self, data: TensorLike):
        return super().score(data) 

    
    def fit(self, data: TensorLike):
        if sps.issparse(data):
            raise ValueError(
                "Sparse data is not supported. You may have forgotten to reduce the dimensionality of the data. Otherwise, please convert the data to a dense format."
            )
        return self._fit(data)

    def _fit(self, data):
        try:
            return super().fit(data)
        except torch._C._LinAlgError as e:
            if self.covariance_regularization >= 1:
                raise ValueError(
                    "Cholesky decomposition failed even with covariance regularization = 1. The matrix may be singular."
                ) from e
            else:
                self.covariance_regularization *= 10
                logger.warning(
                    f"Cholesky decomposition failed. Retrying with covariance regularization {self.covariance_regularization}."
                )
                return self._fit(data)

    def predict(self, data: TensorLike):
        """ 
        Computes the most likely components for each of the provided datapoints.
        
        Attention
        ----------
            When calling this function in a multi-process environment, each process receives only
            a subset of the predictions. If you want to aggregate predictions, make sure to gather
            the values returned from this method.
        """
        return super().predict(data).numpy()

    def predict_proba(self, data: TensorLike):
        """
        Computes a distribution over the components for each of the provided datapoints.
        
        Attention
        ----------
            When calling this function in a multi-process environment, each process receives only
            a subset of the predictions. If you want to aggregate predictions, make sure to gather
            the values returned from this method.
        """
        loader = DataLoader(
            dataset_from_tensors(data),
            batch_size=self.batch_size or len(data),
            collate_fn=collate_tensor,
        ) 
        trainer_params = self.trainer_params.copy()
        trainer_params["logger"] = False
        result = Trainer(**trainer_params).predict(GaussianMixtureLightningModule(self.model_), loader)
        return torch.cat([x[0] for x in cast(List[Tuple[torch.Tensor, torch.Tensor]], result)])

    def score_samples(self, data: TensorLike):
        """
        Computes the negative log-likelihood (NLL) of each of the provided datapoints.
        
        Attention
        ----------
            When calling this function in a multi-process environment, each process receives only
            a subset of the predictions. If you want to aggregate predictions, make sure to gather
            the values returned from this method.
        """
        loader = DataLoader(
            dataset_from_tensors(data),
            batch_size=self.batch_size or len(data),
            collate_fn=collate_tensor,
        )
        trainer_params = self.trainer_params.copy()
        trainer_params["logger"] = False
        result = Trainer(**trainer_params).predict(GaussianMixtureLightningModule(self.model_), loader)
        return torch.stack([x[1] for x in cast(List[Tuple[torch.Tensor, torch.Tensor]], result)])

class Cluster(GaussianMixture):
    """
    Cluster cells or spots based on features          ###### neighborhood aggregated features from CellCharter.
    
    """

    def __init__(
        self,
        n_clusters: int = 1, 
        covariance_type: str = "full",
        init_strategy: str = "kmeans",
        init_means: torch.Tensor = None,
        convergence_tolerance: float = 0.001,
        covariance_regularization: float = 1e-06,
        batch_size: int = None,
        trainer_params: dict = None,
        random_state: AnyRandom = 0,
    ):
        super().__init__(                            # 这个调用将当前类的初始化参数传递给父类的构造函数（super().__init__()）
            n_clusters=n_clusters,
            covariance_type=covariance_type,
            init_strategy=init_strategy,
            init_means=init_means,
            convergence_tolerance=convergence_tolerance,
            covariance_regularization=covariance_regularization,
            batch_size=batch_size,
            trainer_params=trainer_params,
            random_state=random_state,
        )

    def fit(self, adata: ad.AnnData, use_rep: str = "X_cellcharter"): #* 前面aggragate的结果就是X_cellcharter
        """
        Fit data into ``n_clusters`` clusters.
        """ 
        logging_level = logging.root.level 
        X = adata.X if use_rep is None else adata.obsm[use_rep]
        logging_level = logging.getLogger("lightning.pytorch").getEffectiveLevel()
        
        logging.getLogger("lightning.pytorch").setLevel(logging.ERROR)
        super().fit(X)
        logging.getLogger("lightning.pytorch").setLevel(logging_level) 
        # 临时忽略低于 ERROR 级别的日志（例如，WARNING、INFO、DEBUG 等信息将不再输出）
        
        adata.uns["_cellcharter"] = {k: v for k, v in self.get_params().items() if k != "init_means"}
    
    def score(self, adata: ad.AnnData, use_rep: str = "X_cellcharter"):
        """
        Fit data into ``n_clusters`` clusters.
        """ 
        logging_level = logging.root.level 
        X =  adata.obsm[use_rep]
        logging_level = logging.getLogger("lightning.pytorch").getEffectiveLevel()
        
        logging.getLogger("lightning.pytorch").setLevel(logging.ERROR)
        super().score(X)
        
        logging.getLogger("lightning.pytorch").setLevel(logging_level) 
        # 临时忽略低于 ERROR 级别的日志（例如，WARNING、INFO、DEBUG 等信息将不再输出）
        
        adata.uns["_cellcharter"] = {k: v for k, v in self.get_params().items() if k != "init_means"}

    def predict(self,
            adata: ad.AnnData,
            use_rep: str = "X_cellcharter",
            store_labels: bool = False,  # 新增参数，用于控制是否存储标签
            store_column: str = 'predicted_labels'):  # 新增参数，用于指定存储的列名
        """
        Predict the labels for the data in ``use_rep`` using the fitted model.
        
        Parameters:
        - adata: AnnData object containing the data to predict.
        - use_rep: str, the name of the key to use from `adata.obsm` or `adata.X` (default is 'X_cellcharter').
        - store_labels: bool, whether to store the predicted labels in `adata.obs` (default is False).
        - store_column: str, the name of the column to store the predicted labels (default is 'predicted_labels').
        
        Returns:
        - A pandas Categorical object containing the predicted labels.
        """
        X = adata.X if use_rep is None else adata.obsm[use_rep]
        
        labels = pd.Categorical(super().predict(X), categories=np.arange(self.n_clusters))
        
        if store_labels:
            adata.obs[store_column] = labels 
    
        return labels

