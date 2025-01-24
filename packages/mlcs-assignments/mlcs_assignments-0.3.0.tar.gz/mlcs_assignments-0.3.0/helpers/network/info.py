from typing import Protocol

from torch.nn import Module
from torchinfo import summary


class DescribableModel(Protocol):
    @property
    def model(self) -> Module:
        """Returns the underlying PyTorch model."""
        ...

    @property
    def input_size(self) -> int:
        """Returns the size of the input."""
        ...


def describe(model: DescribableModel) -> None:
    print(summary(model.model, input_size=(1, model.input_size)))
