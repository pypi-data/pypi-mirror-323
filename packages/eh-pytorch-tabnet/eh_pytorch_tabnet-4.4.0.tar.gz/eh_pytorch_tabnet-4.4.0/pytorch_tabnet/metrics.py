from dataclasses import dataclass
from typing import Any, List, Union

import torch
from torch.nn import CrossEntropyLoss
from torcheval.metrics.functional import (
    multiclass_accuracy,
    multiclass_auroc,
)


def UnsupervisedLoss(
    y_pred: torch.Tensor,
    embedded_x: torch.Tensor,
    obf_vars: torch.Tensor,
    eps: float = 1e-9,
    weights: torch.Tensor = None,
) -> torch.Tensor:
    """
    Implements unsupervised loss function with optional sample weights.
    """
    errors = y_pred - embedded_x
    reconstruction_errors = torch.mul(errors, obf_vars) ** 2
    batch_means = torch.mean(embedded_x, dim=0)
    batch_means[batch_means == 0] = 1

    batch_stds = torch.std(embedded_x, dim=0) ** 2
    batch_stds[batch_stds == 0] = batch_means[batch_stds == 0]
    features_loss = torch.matmul(reconstruction_errors, 1 / batch_stds)
    nb_reconstructed_variables = torch.sum(obf_vars, dim=1)
    features_loss = features_loss / (nb_reconstructed_variables + eps)

    if weights is not None:
        features_loss = features_loss * weights

    loss = torch.mean(features_loss)
    return loss


@dataclass
class UnsupMetricContainer:
    """Updated to support weights."""

    metric_names: List[str]
    prefix: str = ""

    def __post_init__(self) -> None:
        self.metrics = Metric.get_metrics_by_names(self.metric_names)
        self.names = [self.prefix + name for name in self.metric_names]

    def __call__(
        self,
        y_pred: torch.Tensor,
        embedded_x: torch.Tensor,
        obf_vars: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> dict:
        logs = {}
        for metric in self.metrics:
            res = metric(y_pred, embedded_x, obf_vars, weights)
            logs[self.prefix + metric._name] = res
        return logs


@dataclass
class MetricContainer:
    """Updated to support weights."""

    metric_names: List[str]
    prefix: str = ""

    def __post_init__(self) -> None:
        self.metrics = Metric.get_metrics_by_names(self.metric_names)
        self.names = [self.prefix + name for name in self.metric_names]

    def __call__(
        self,
        y_true: torch.Tensor,
        y_pred: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> dict:
        logs = {}
        for metric in self.metrics:
            if isinstance(y_pred, list):
                res = torch.mean(torch.tensor([metric(y_true[:, i], y_pred[i], weights) for i in range(len(y_pred))]))
            else:
                res = metric(y_true, y_pred, weights)
            logs[self.prefix + metric._name] = res
        return logs


class Metric:
    _name: str
    _maximize: bool

    def __call__(
        self,
        y_true: torch.Tensor,
        y_pred: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        raise NotImplementedError("Custom Metrics must implement this function")

    @classmethod
    def get_metrics_by_names(cls, names: List[str]) -> List:
        """Get list of metric classes.

        Parameters
        ----------
        cls : Metric
            Metric class.
        names : list
            List of metric names.

        Returns
        -------
        metrics : list
            List of metric classes.

        """
        available_metrics = cls.__subclasses__()
        available_names = [metric()._name for metric in available_metrics]
        metrics = []
        for name in names:
            assert name in available_names, f"{name} is not available, choose in {available_names}"
            idx = available_names.index(name)
            metric = available_metrics[idx]()
            metrics.append(metric)
        return metrics


class AUC(Metric):
    """
    AUC.
    """

    _name: str = "auc"
    _maximize: bool = True

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        num_of_classes = y_score.shape[1]
        # if weights is not None:
        #     weights = weights.to(y_true.device)
        #     return multiclass_auroc(y_score, y_true, num_classes=num_of_classes, weights=weights).cpu().item()
        return multiclass_auroc(y_score, y_true, num_classes=num_of_classes, average="macro").cpu().item()


class Accuracy(Metric):
    """
    Accuracy.
    """

    _name: str = "accuracy"
    _maximize: bool = True

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        res = multiclass_accuracy(
            y_score,
            y_true,
        )
        # if weights is not None:
        #     weights = weights.to(y_true.device)
        #     res *= weights
        return res.cpu().item()


class BalancedAccuracy(Metric):
    """
    Balanced Accuracy.
    """

    _name: str = "balanced_accuracy"
    _maximize: bool = True

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        num_of_classes = y_score.shape[1]
        # if weights is not None:
        #     weights = weights.to(y_true.device)
        #     return multiclass_accuracy(y_score, y_true, average="macro", num_classes=num_of_classes, weights=weights).cpu().item()
        return multiclass_accuracy(y_score, y_true, average="macro", num_classes=num_of_classes).cpu().item()


class LogLoss(Metric):
    """
    LogLoss.
    """

    _name: str = "logloss"
    _maximize: bool = False

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        loss = CrossEntropyLoss(reduction="none")(y_score.float(), y_true.long())
        if weights is not None:
            loss *= weights.to(y_true.device)
        return loss.mean().item()


class MAE(Metric):
    """
    Mean Absolute Error.
    """

    _name: str = "mae"
    _maximize: bool = False

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        errors = torch.abs(y_true - y_score)
        if weights is not None:
            errors *= weights.to(y_true.device)
        return torch.mean(errors).cpu().item()


class MSE(Metric):
    """
    Mean Squared Error.
    """

    _name: str = "mse"
    _maximize: bool = False

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        errors = (y_true - y_score) ** 2
        if weights is not None:
            errors *= weights.to(y_true.device)
        return torch.mean(errors).cpu().item()


class RMSLE(Metric):
    """
    Root Mean squared logarithmic error regression loss.
    Scikit-implementation:
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_log_error.html
    Note: In order to avoid error, negative predictions are clipped to 0.
    This means that you should clip negative predictions manually after calling predict.
    """

    _name: str = "rmsle"
    _maximize: bool = False

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        logerror = torch.log(y_score + 1) - torch.log(y_true + 1)
        squared_logerror = logerror**2
        if weights is not None:
            squared_logerror *= weights.to(y_true.device)
        return torch.sqrt(torch.mean(squared_logerror)).cpu().item()


class UnsupervisedMetric(Metric):
    """
    Unsupervised metric
    """

    _name: str = "unsup_loss"
    _maximize: bool = False

    def __call__(  # type: ignore
        self,
        y_pred: torch.Tensor,
        embedded_x: torch.Tensor,
        obf_vars: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        loss = UnsupervisedLoss(y_pred, embedded_x, obf_vars, weights=weights)
        return loss.cpu().item()


class UnsupervisedNumpyMetric(Metric):
    """
    Unsupervised metric
    """

    _name: str = "unsup_loss_numpy"
    _maximize: bool = False

    def __call__(  # type: ignore[override]
        # self, y_pred: np.ndarray, embedded_x: np.ndarray, obf_vars: np.ndarray
        self,
        y_pred: torch.Tensor,
        embedded_x: torch.Tensor,
        obf_vars: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        return UnsupervisedLoss(y_pred, embedded_x, obf_vars).cpu().item()


class RMSE(Metric):
    """
    Root Mean Squared Error.
    """

    _name: str = "rmse"
    _maximize: bool = False

    def __call__(
        self,
        y_true: torch.Tensor,
        y_score: torch.Tensor,
        weights: torch.Tensor = None,
    ) -> float:
        mse_errors = (y_true - y_score) ** 2
        if weights is not None:
            mse_errors *= weights.to(y_true.device)
        return torch.sqrt(torch.mean(mse_errors)).cpu().item()


def check_metrics(metrics: List[Union[str, Any]]) -> List[str]:
    """Check if custom metrics are provided.

    Parameters
    ----------
    metrics : list of str or classes
        List with built-in metrics (str) or custom metrics (classes).

    Returns
    -------
    val_metrics : list of str
        List of metric names.

    """
    val_metrics = []
    for metric in metrics:
        if isinstance(metric, str):
            val_metrics.append(metric)
        elif issubclass(metric, Metric):
            val_metrics.append(metric()._name)
        else:
            raise TypeError("You need to provide a valid metric format")
    return val_metrics
