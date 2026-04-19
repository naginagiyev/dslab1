import numpy as np
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, log_loss, matthews_corrcoef, r2_score,
    mean_absolute_error, mean_squared_error, explained_variance_score,
    average_precision_score, silhouette_score, davies_bouldin_score, 
    calinski_harabasz_score
)

def computeScore(metric, yTrue, yPred):
    metric = str(metric).lower()

    if metric == "accuracy":
        return accuracy_score(yTrue, yPred.round())
    elif metric == "f1":
        return f1_score(yTrue, yPred.round(), average='weighted')
    elif metric == "precision":
        return precision_score(yTrue, yPred.round(), average='weighted')
    elif metric == "recall":
        return recall_score(yTrue, yPred.round(), average='weighted')
    elif metric == "roc-auc":
        return roc_auc_score(yTrue, yPred, multi_class='ovr')
    elif metric == "log-loss":
        return log_loss(yTrue, yPred)
    elif metric == "matthews-corrcoef":
        return matthews_corrcoef(yTrue, yPred.round())

    elif metric == "r2":
        return r2_score(yTrue, yPred)
    elif metric == "mae":
        return mean_absolute_error(yTrue, yPred)
    elif metric == "mse":
        return mean_squared_error(yTrue, yPred)
    elif metric == "rmse":
        return np.sqrt(mean_squared_error(yTrue, yPred))
    elif metric == "mape":
        return np.mean(np.abs((yTrue - yPred) / yTrue))
    elif metric == "explained-variance":
        return explained_variance_score(yTrue, yPred)

    elif metric == "smape":
        return np.mean(2 * np.abs(yPred - yTrue) / (np.abs(yTrue) + np.abs(yPred)))

    elif metric == "average-precision":
        return average_precision_score(yTrue, yPred)

    elif metric == "silhouette":
        return silhouette_score(yTrue, yPred)
    elif metric == "davies-bouldin":
        return davies_bouldin_score(yTrue, yPred)
    elif metric == "calinski-harabasz":
        return calinski_harabasz_score(yTrue, yPred)

    else:
        raise ValueError(f"Unsupported metric: {metric}")