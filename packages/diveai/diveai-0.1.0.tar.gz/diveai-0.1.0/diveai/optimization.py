import numpy as np 

def gradient_descent(X, y, weights, bias, learning_rate):
    """
    Perform a single step of gradient descent.
    :param X: Feature matrix (numpy array of shape (m, n)).
    :param y: Target vector (numpy array of shape (m, 1)).
    :param weights: Current weights (numpy array of shape (n, 1)).
    :param bias: Current bias (scalar).
    :param learning_rate: Step size for gradient descent.
    :return: Updated weights and bias.
    """
    m = X.shape[0]  # Number of training examples
    y_pred = np.dot(X, weights) + bias  # Predicted values

    # Compute gradients
    dw = -(1 / m) * np.dot(X.T, (y - y_pred))
    db = -(1 / m) * np.sum(y - y_pred)

    # Update weights and bias
    weights -= learning_rate * dw
    bias -= learning_rate * db

    return weights, bias