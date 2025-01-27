import matplotlib.pyplot as plt

class PlotBuilder:
    def __init__(self, x_label="X", y_label="Y", title="My Plot"):
        """
        Initializes the plot with optional labels and title.
        :param x_label: Label for the x-axis.
        :param y_label: Label for the y-axis.
        :param title: Title of the plot.
        """
        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.figure, self.ax = plt.subplots()

    def add_plot(self, x, y, plot_type="line", color="blue", label=None, **kwargs):
        """
        Adds a plot to the figure based on the specified type.
        :param x: x-coordinates of the data.
        :param y: y-coordinates of the data.
        :param plot_type: Type of plot (e.g., "line", "scatter", "bar").
        :param color: Color of the plot elements.
        :param label: Label for the plot in the legend.
        :param kwargs: Additional keyword arguments for the plot function.
        """
        if plot_type == "line":
            self.ax.plot(x, y, color=color, label=label, **kwargs)
        elif plot_type == "scatter":
            self.ax.scatter(x, y, color=color, label=label, **kwargs)
        elif plot_type == "bar":
            self.ax.bar(x, y, color=color, label=label, **kwargs)
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")

    def show(self):
        """
        Applies labels, legend, title, and displays the final plot.
        """
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_title(self.title)

        # Only show legend if labels were provided
        handles, labels = self.ax.get_legend_handles_labels()
        if labels:
            self.ax.legend()

        plt.show()
