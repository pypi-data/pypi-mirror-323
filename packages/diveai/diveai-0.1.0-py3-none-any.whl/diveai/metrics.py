import numpy as np

def mean_squared_error(y_true, y_pred):
    """
    Calculate Mean Squared Error (MSE).
    :param y_true: True target values.
    :param y_pred: Predicted target values.
    :return: MSE value.
    """
    return np.mean((y_true - y_pred) ** 2)

def r2_score(y_true, y_pred):
    """
    Calculate R-squared score.
    :param y_true: True target values.
    :param y_pred: Predicted target values.
    :return: R-squared score.
    """
    ss_total = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_residual = np.sum((y_true - y_pred) ** 2)
    return 1 - (ss_residual / ss_total)