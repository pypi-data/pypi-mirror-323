from typing import Protocol

from helpers.maths import Vector


class InputScaler(Protocol):
    def transform(self, data: Vector, /) -> Vector:
        """Transforms the input data."""
        ...


class OutputScaler(Protocol):
    def inverse_transform(self, data: Vector, /) -> Vector:
        """Scales the output data back to its original form."""
        ...
