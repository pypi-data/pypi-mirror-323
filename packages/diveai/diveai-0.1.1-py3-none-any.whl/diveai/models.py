import numpy as np
from diveai.optimization import gradient_descent

class LinearRegression:
    def __init__(self, learning_rate=0.01, iterations=1000, dive=False):
        """
        Initialize the Linear Regression model with hyperparameters.
        :param learning_rate: The step size for gradient descent.
        :param iterations: Number of iterations to run gradient descent.
        :param dive: If True, logs detailed information about the model derivation.
        """
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.dive = dive  # Add dive parameter to the class
        self.weights = None
        self.bias = None

        if self.dive:
            print("Initializing Linear Regression Model with Dive Mode Enabled\n")
            print("Step 1: Understanding the Cost Function")
            print("The cost function used is Mean Squared Error (MSE):")
            print("J(w, b) = (1/m) * Σ(y - y_pred)^2")
            print("This measures how far our predictions are from the actual values.\n")

            print("Step 2: Deriving Gradients for Optimization")
            print("To minimize the cost function J(w, b), we compute its partial derivatives:")
            print("∂J/∂w = -(1/m) * Σ(X.T * (y - y_pred))")
            print("∂J/∂b = -(1/m) * Σ(y - y_pred)")
            print("These gradients tell us how to adjust weights and bias to reduce the error.\n")

            print("Step 3: Gradient Descent Update Rule")
            print("Using the gradients, we update weights and bias as follows:")
            print("weights = weights - learning_rate * ∂J/∂w")
            print("bias = bias - learning_rate * ∂J/∂b\n")

    def fit(self, X, y):
        """
        Train the model using gradient descent.
        :param X: Feature matrix (numpy array of shape (m, n)).
        :param y: Target vector (numpy array of shape (m, 1)).
        """
        # Number of training examples and features
        m, n = X.shape

        if self.dive:
            print("\nStep 4: Training Process Begins")
            print(f"Number of Training Examples: {m}, Features: {n}")
            print(f"Learning Rate: {self.learning_rate}, Iterations: {self.iterations}")
            print("Starting Gradient Descent...\n")

        # Initialize weights and bias
        self.weights = np.zeros((n, 1))
        self.bias = 0

        # Reshape y to ensure it's a column vector
        y = y.reshape(-1, 1)

        # Perform gradient descent with optional logging
        self.weights, self.bias = gradient_descent(
            X,
            y,
            self.weights,
            self.bias,
            self.learning_rate,
            self.iterations,
            self.dive,
        )

        if self.dive:
            print("\nTraining Complete")
            print(f"Final Weights: {self.weights.flatten()}, Final Bias: {self.bias:.6f}")

    def predict(self, X):
        """
        Predict target values for given input features.
        :param X: Feature matrix (numpy array of shape (m, n)).
        :return: Predicted values (numpy array of shape (m, 1)).
        """
        return np.dot(X, self.weights) + self.bias
