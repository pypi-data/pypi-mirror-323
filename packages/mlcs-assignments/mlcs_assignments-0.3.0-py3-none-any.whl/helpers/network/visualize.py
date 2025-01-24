from typing import Protocol, Sequence
from helpers.maths import Vector
from plotly.graph_objects import Figure, Scatter, Scatter3d


import numpy as np


class ActivationLayer(Protocol):
    def forward(self, sigma: Vector, /) -> Vector:
        """Compute the forward pass of the activation layer."""
        ...


class LossFunction(Protocol):
    def loss(self, *, y_true: Vector, y_predicted: Vector) -> float:
        """Compute the loss of the loss function."""
        ...


class ActivationLayerVisualizerMixin:
    def visualize(
        self: ActivationLayer,
        *,
        sigma_range: tuple[float, float] = (-5, 5),
        points: int = 100,
    ) -> None:
        """Visualize the activation layer for a one-dimensional input.

        Args:
            sigma_range: The range of sigma values to visualize.
            points: The number of points to visualize.

        Example:
            ```python
            layer = SigmoidLayer()
            layer.visualize()
            # Output: A plot of the sigmoid function.
            ```
        """
        sigma = np.linspace(*sigma_range, points)
        a = self.forward(sigma)

        figure = Figure(data=[Scatter(x=sigma, y=a, name="Activation")])
        figure.update_layout(title=f"{self.__class__.__name__} Activation Layer")
        figure.show()


class LossFunctionVisualizerMixin:
    def visualize(
        self: LossFunction,
        *,
        y_range: tuple[float, float] = (-5, 5),
        points: int = 10,
        classification: bool = False,
    ) -> None:
        """Visualize the loss function for a one-dimensional input in two dimensions.

        Args:
            y_range: The range of y values to visualize.
            points: The number of points to visualize.
            classification: Whether the loss function is for classification.

        Example:
            ```python
            loss = MeanSquaredError()
            loss.visualize()
            # Output: A plot of the mean squared error.
            ```
        """

        if classification:
            _visualize_classification(loss=self, points=points)
        else:
            _visualize_regression(loss=self, y_range=y_range, points=points)


def visualize_loss(losses: Sequence[float]) -> None:
    """Visualize a sequence of computed losses.

    Args:
        losses: A sequence of computed losses.

    Example:
        ```python
        losses = [0.5, 0.4, 0.3, 0.2, 0.1]
        visualize_loss(losses)
        # Output: A plot of the losses.
        ```
    """

    figure = Figure(data=[Scatter(y=losses, name="Loss")])
    figure.update_layout(title="Losses")
    figure.show()


def _visualize_regression(
    loss: LossFunction, *, y_range: tuple[float, float], points: int
) -> None:
    # Create a grid of y values
    y_true = np.linspace(*y_range, points)
    y_predicted = np.linspace(*y_range, points)
    Y_true, Y_predicted = np.meshgrid(y_true, y_predicted)

    # Compute the loss for each pair of y values
    Z = np.zeros_like(Y_true)
    for i, y_t in enumerate(y_true):
        for j, y_p in enumerate(y_predicted):
            Z[i, j] = loss.loss(y_true=y_t, y_predicted=y_p)

    # Create a 3D surface plot
    figure = Figure(
        data=[
            Scatter3d(
                x=Y_true.flatten(),
                y=Y_predicted.flatten(),
                z=Z.flatten(),
                mode="markers",
            )
        ]
    )
    figure.update_layout(
        title=f"{loss.__class__.__name__} Loss Function",
        scene=dict(xaxis_title="y_true", yaxis_title="y_predicted", zaxis_title="Loss"),
    )
    figure.show()


def _visualize_classification(loss: LossFunction, *, points: int) -> None:
    figure = Figure()
    p_1 = np.linspace(0.01, 0.99, points)
    p_2 = 1 - p_1

    y_true_options = [np.array([1, 0]), np.array([0, 1])]

    for y_true in y_true_options:
        Z = np.zeros(points)
        for i in range(points):
            y_predicted = np.array([p_1[i], p_2[i]])
            Z[i] = loss.loss(y_true=y_true, y_predicted=y_predicted)

        figure.add_trace(
            Scatter3d(
                x=p_1,
                y=p_2,
                z=Z,
                mode="lines+markers",
                name=f"y_true = {y_true}",
                marker=dict(size=3),
            )
        )

    figure.update_layout(
        title=f"{loss.__class__.__name__} Loss Function for 2 Classes",
        scene=dict(
            xaxis_title="Probability of Class 1",
            yaxis_title="Probability of Class 2",
            zaxis_title="Loss",
        ),
        legend_title="True Class",
    )

    figure.show()
