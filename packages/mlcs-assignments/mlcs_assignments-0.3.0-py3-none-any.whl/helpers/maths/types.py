from typing import TypeAlias, NamedTuple
from numpy.typing import NDArray
import numpy as np

Matrix: TypeAlias = NDArray[np.floating]
Vector: TypeAlias = NDArray[np.floating]


class Point(NamedTuple):
    """A point in two dimensions.

    Attributes:
        x: The x-coordinate of the point.
        y: The y-coordinate of the point.

    Example:
        You can make a point (1, 2) in 2D space, where the x coordinate is 1 and the y coordinate is 2, like this:

        ```python
        point = Point(1, 2)
        print(point)
        # Output: Point(x=1, y=2)
        ```
    """

    x: float
    y: float

    def vector(self) -> Vector:
        """Returns the point as a vector."""
        return np.array([self.x, self.y])

    def is_approximately(self, other: "Point", *, tolerance: float = 1e-10) -> bool:
        """Checks if the point is approximately equal to another point.

        Args:
            other: The other point to compare with.
            tolerance: The relative tolerance for the comparison (default is 1e-10).

        Returns:
            True if the points are approximately equal, False otherwise.
        """
        return np.allclose(self.vector(), other.vector(), rtol=tolerance)
