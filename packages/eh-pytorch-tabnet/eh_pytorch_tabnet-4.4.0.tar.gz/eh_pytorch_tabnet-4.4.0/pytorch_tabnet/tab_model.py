from dataclasses import dataclass, field
from functools import partial
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import scipy
import torch

# from torch.utils.data import DataLoader
from pytorch_tabnet.abstract_model import TabModel
from pytorch_tabnet.data_handlers import PredictDataset, SparsePredictDataset, TBDataLoader
from pytorch_tabnet.multiclass_utils import check_output_dim, infer_output_dim
from pytorch_tabnet.utils import filter_weights


@dataclass
class TabNetClassifier(TabModel):
    output_dim: int = None
    weight: Any = field(init=False, default=0)

    def __post_init__(self) -> None:
        super(TabNetClassifier, self).__post_init__()
        self._task: str = "classification"
        self._default_loss: Any = partial(
            torch.nn.functional.cross_entropy,
            reduction="none",
        )
        self._default_metric: str = "accuracy"

    def weight_updater(self, weights: Union[bool, Dict[Union[str, int], Any], Any]) -> Union[bool, Dict[Union[str, int], Any]]:
        if isinstance(weights, int):
            return weights  # type: ignore
        elif isinstance(weights, dict):
            return {self.target_mapper[key]: value for key, value in weights.items()}
        else:
            return weights

    def prepare_target(self, y: np.ndarray) -> np.ndarray:
        return np.vectorize(self.target_mapper.get)(y)

    def compute_loss(
        self,
        y_pred: torch.Tensor,
        y_true: torch.Tensor,
        w: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        class_count = None
        if isinstance(self.weight, int) and self.weight == 1:
            _class_num, class_count = y_true.long().unique(return_counts=True)
            class_count[class_count == 0] = 1

        loss = self.loss_fn(y_pred, y_true.long(), weight=1 / class_count if class_count is not None else None)
        if w is not None:
            loss = loss * w
        return loss.mean()

    def update_fit_params(  # type: ignore[override]
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        eval_set: List[Tuple[np.ndarray, np.ndarray]],
        weights: Union[bool, Dict[str, Any]],
    ) -> None:
        output_dim: int
        train_labels: List[Any]
        output_dim, train_labels = infer_output_dim(y_train)
        for _X, y in eval_set:
            check_output_dim(train_labels, y)
        self.output_dim: int = output_dim
        self._default_metric = "auc" if self.output_dim == 2 else "accuracy"
        self.classes_: List[Any] = train_labels
        self.target_mapper: Dict[Any, int] = {class_label: index for index, class_label in enumerate(self.classes_)}
        self.preds_mapper: Dict[str, Any] = {str(index): class_label for index, class_label in enumerate(self.classes_)}
        # self.updated_weights: Union[bool, Dict[Union[str, int], Any]] = self.weight_updater(weights)

    def stack_batches(
        self,
        # list_y_true: List[np.ndarray],
        # list_y_score: List[np.ndarray],
        # ) -> Tuple[np.ndarray, np.ndarray]:
        #     y_true: np.ndarray = np.hstack(list_y_true)
        #     y_score: np.ndarray = np.vstack(list_y_score)
        #     y_score = softmax(y_score, axis=1)
        #     return y_true, y_score
        list_y_true: List[torch.Tensor],
        list_y_score: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        y_true: torch.Tensor = torch.hstack(list_y_true)
        y_score: torch.Tensor = torch.vstack(list_y_score)
        y_score = torch.nn.Softmax(dim=1)(y_score)
        return y_true, y_score

    def predict_func(self, outputs: np.ndarray) -> np.ndarray:
        outputs = np.argmax(outputs, axis=1)
        return np.vectorize(self.preds_mapper.get)(outputs.astype(str))

    def predict_proba(self, X: Union[torch.Tensor, np.ndarray]) -> np.ndarray:
        self.network.eval()

        if scipy.sparse.issparse(X):
            dataloader: TBDataLoader = TBDataLoader(
                name="predict",
                dataset=SparsePredictDataset(X),
                batch_size=self.batch_size,
                # shuffle=False,
                predict=True,
            )
        else:
            dataloader = TBDataLoader(
                name="predict",
                dataset=PredictDataset(X),
                batch_size=self.batch_size,
                # shuffle=False,
                predict=True,
            )

        results: List[np.ndarray] = []
        with torch.no_grad():
            for _batch_nb, (data, _, _) in enumerate(dataloader):  # type: ignore
                data = data.to(self.device).float()  # type: ignore

                output: torch.Tensor
                _M_loss: torch.Tensor
                output, _M_loss = self.network(data)
                predictions: np.ndarray = (
                    torch.nn.Softmax(dim=1)(output).cpu().detach().numpy()
                )  # todo: replace with pytorch's torch.vstack
                results.append(predictions)
            res: np.ndarray = np.vstack(results)  # todo: replace with pytorch's torch.vstack
        return res


@dataclass
class TabNetRegressor(TabModel):
    output_dim: int = None

    def __post_init__(self) -> None:
        super(TabNetRegressor, self).__post_init__()
        self._task: str = "regression"
        # self._default_loss: Any = torch.nn.functional.mse_loss
        self._default_loss: Any = partial(
            torch.nn.functional.mse_loss,
            reduction="none",
        )
        self._default_metric: str = "mse"

    def prepare_target(self, y: np.ndarray) -> np.ndarray:
        return y

    def compute_loss(
        self,
        y_pred: torch.Tensor,
        y_true: torch.Tensor,
        w: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        loss = self.loss_fn(
            y_pred,
            y_true,
        )
        if len(loss.shape) != 1:
            loss = torch.mean(loss, dim=1)
        if w is not None:
            loss = loss * w
        return loss.mean()

    def update_fit_params(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        eval_set: List[Tuple[np.ndarray, np.ndarray]],
        weights: Union[bool, np.ndarray],
    ) -> None:
        if len(y_train.shape) != 2:
            msg: str = (
                "Targets should be 2D : (n_samples, n_regression) "
                + f"but y_train.shape={y_train.shape} given.\n"
                + "Use reshape(-1, 1) for single regression."
            )
            raise ValueError(msg)
        self.output_dim: int = y_train.shape[1]
        self.preds_mapper: None = None

        self.updated_weights: Union[bool, np.ndarray] = weights
        filter_weights(self.updated_weights)

    def predict_func(self, outputs: np.ndarray) -> np.ndarray:
        return outputs

    def stack_batches(
        self,
        list_y_true: List[torch.Tensor],
        list_y_score: List[torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        y_true: torch.Tensor = torch.vstack(list_y_true)
        y_score: torch.Tensor = torch.vstack(list_y_score)
        return y_true, y_score


MultiTabNetRegressor = TabNetRegressor
