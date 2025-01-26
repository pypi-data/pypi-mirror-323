import numpy as np
from diveai.optimization import gradient_descent

class LinearRegression:
    def __init__(self, learning_rate=0.01, iterations=1000):
        """
        Initialize the Linear Regression model with hyperparameters.
        :param learning_rate: The step size for gradient descent.
        :param iterations: Number of iterations to run gradient descent.
        """
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        """
        Train the model using gradient descent.
        :param X: Feature matrix (numpy array of shape (m, n)).
        :param y: Target vector (numpy array of shape (m, 1)).
        """
        # Number of training examples and features
        m, n = X.shape

        # Initialize weights and bias
        self.weights = np.zeros((n, 1))
        self.bias = 0

        # Reshape y to ensure it's a column vector
        y = y.reshape(-1, 1)

        # Perform gradient descent for the specified number of iterations
        for _ in range(self.iterations):
            self.weights, self.bias = gradient_descent(
                X, y, self.weights, self.bias, self.learning_rate
            )

    def predict(self, X):
        """
        Predict target values for given input features.
        :param X: Feature matrix (numpy array of shape (m, n)).
        :return: Predicted values (numpy array of shape (m, 1)).
        """
        return np.dot(X, self.weights) + self.bias
