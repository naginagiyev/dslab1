import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, log_loss, matthews_corrcoef, r2_score,
    mean_absolute_error, mean_squared_error, explained_variance_score,
    average_precision_score, silhouette_score, davies_bouldin_score, 
    calinski_harabasz_score
)

def computeScore(metric, true, pred):
    metric = str(metric).lower()

    if metric == "accuracy":
        return accuracy_score(true, pred.round())
    elif metric == "f1":
        return f1_score(true, pred.round(), average='weighted')
    elif metric == "precision":
        return precision_score(true, pred.round(), average='weighted')
    elif metric == "recall":
        return recall_score(true, pred.round(), average='weighted')
    elif metric == "roc-auc":
        return roc_auc_score(true, pred, multi_class='ovr')
    elif metric == "log-loss":
        return log_loss(true, pred)
    elif metric == "matthews-corrcoef":
        return matthews_corrcoef(true, pred.round())

    elif metric == "r2":
        return r2_score(true, pred)
    elif metric == "mae":
        return mean_absolute_error(true, pred)
    elif metric == "mse":
        return mean_squared_error(true, pred)
    elif metric == "rmse":
        return np.sqrt(mean_squared_error(true, pred))
    elif metric == "mape":
        return np.mean(np.abs((true - pred) / true))
    elif metric == "explained-variance":
        return explained_variance_score(true, pred)

    elif metric == "smape":
        return np.mean(2 * np.abs(pred - true) / (np.abs(true) + np.abs(pred)))

    elif metric == "average-precision":
        return average_precision_score(true, pred)

    elif metric == "silhouette":
        return silhouette_score(true, pred)
    elif metric == "davies-bouldin":
        return davies_bouldin_score(true, pred)
    elif metric == "calinski-harabasz":
        return calinski_harabasz_score(true, pred)

    else:
        raise ValueError(f"Unsupported metric: {metric}")