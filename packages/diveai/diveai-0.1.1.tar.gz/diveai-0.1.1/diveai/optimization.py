import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def gradient_descent(X, y, initial_weights, initial_bias, learning_rate, iterations, dive=False):
    """
    Perform gradient descent with optional interactive visualization and logging.

    Args:
        X (numpy.ndarray): Feature matrix of shape (m, n).
        y (numpy.ndarray): Target vector of shape (m,).
        initial_weights (numpy.ndarray): Initial weights of shape (n, 1).
        initial_bias (float): Initial bias term.
        learning_rate (float): Learning rate for gradient descent.
        iterations (int): Number of iterations.
        dive (bool): If True, display plots and print progress. If False, run silently.

    Returns:
        tuple: Optimized weights and bias.
    """
    # Initialize weights and bias
    weights = initial_weights
    bias = initial_bias

    # Logs for plotting
    weight_log = []
    bias_log = []
    cost_log = []

    m = X.shape[0]  # Number of examples

    if dive:
        # Create a Plotly Figure with 3 subplots:
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=("Cost vs Iterations", "Weights and Bias vs Iterations", "Data & Fit Line")
        )

        # Initialize traces for cost, weights, bias
        cost_trace = go.Scatter(x=[], y=[], mode='lines', name='Cost', line=dict(color='blue'))
        weight_trace = go.Scatter(x=[], y=[], mode='lines', name='Weights', line=dict(color='orange'))
        bias_trace = go.Scatter(x=[], y=[], mode='lines', name='Bias', line=dict(color='green'))

        # Trace for the original data (scatter) and for the fit line (will update each iteration)
        data_trace = go.Scatter(
            x=X[:, 0],
            y=y if y.ndim == 1 else y[:, 0],
            mode='markers',
            name='Data',
            marker=dict(color='black')
        )
        fit_line_trace = go.Scatter(
            x=[],
            y=[],
            mode='lines',
            name='Fit Line',
            line=dict(color='red')
        )

        # Add all traces to the figure
        fig.add_trace(cost_trace, row=1, col=1)
        fig.add_trace(weight_trace, row=1, col=2)
        fig.add_trace(bias_trace, row=1, col=2)
        fig.add_trace(data_trace, row=1, col=3)
        fig.add_trace(fit_line_trace, row=1, col=3)

        # Layout settings
        fig.update_layout(
            title="Gradient Descent Progress",
            xaxis1=dict(title="Iterations"),
            yaxis1=dict(title="Cost (MSE)"),
            xaxis2=dict(title="Iterations"),
            yaxis2=dict(title="Value"),
            xaxis3=dict(title="X"),
            yaxis3=dict(title="y"),
            showlegend=True,
            height=500,
            width=1200,
        )

        # Convert the figure to a FigureWidget for interactive updates
        fig_widget = go.FigureWidget(fig)

        # Display the interactive figure in Jupyter Notebook
        display(fig_widget)

    # Gradient descent loop
    for i in range(iterations):
        # Compute predictions
        y_pred = np.dot(X, weights) + bias

        # Compute gradients
        dw = -(1 / m) * np.dot(X.T, (y - y_pred))
        db = -(1 / m) * np.sum(y - y_pred)

        # Update weights and bias
        weights -= learning_rate * dw
        bias -= learning_rate * db

        # Compute cost (Mean Squared Error)
        cost = np.mean((y - y_pred) ** 2)

        # Log values for plotting
        weight_log.append(weights[0][0])  # Assuming weights is shape (1,1)
        bias_log.append(bias)
        cost_log.append(cost)

        if dive:
            # Update Plotly traces
            with fig_widget.batch_update():
                # Cost trace
                fig_widget.data[0].x = list(range(len(cost_log)))
                fig_widget.data[0].y = cost_log

                # Weight trace
                fig_widget.data[1].x = list(range(len(weight_log)))
                fig_widget.data[1].y = weight_log

                # Bias trace
                fig_widget.data[2].x = list(range(len(bias_log)))
                fig_widget.data[2].y = bias_log

                # Fit line trace (index 4) - same X each time, updated y_pred
                fig_widget.data[4].x = X[:, 0]
                fig_widget.data[4].y = y_pred if y_pred.ndim == 1 else y_pred[:, 0]

                # Optionally, adjust the ranges dynamically
                fig_widget.update_xaxes(range=[0, iterations], row=1, col=1)
                fig_widget.update_yaxes(range=[0, max(cost_log) * 1.1], row=1, col=1)
                fig_widget.update_xaxes(range=[0, iterations], row=1, col=2)
                fig_widget.update_yaxes(
                    range=[
                        min(min(weight_log, default=0), min(bias_log, default=0)) * 1.1,
                        max(max(weight_log, default=1), max(bias_log, default=1)) * 1.1,
                    ],
                    row=1, col=2,
                )
                # Let the third subplot autoscale to show the fit line properly:
                fig_widget.update_xaxes(autorange=True, row=1, col=3)
                fig_widget.update_yaxes(autorange=True, row=1, col=3)

            # Print progress (optional)
            # print(
            #     f"Iteration {i+1}/{iterations}, Cost: {cost:.6f}, Weight: {weights[0][0]:.6f}, Bias: {bias:.6f}"
            # )

    if dive:
        print("Gradient Descent Complete!")

    return weights, bias
