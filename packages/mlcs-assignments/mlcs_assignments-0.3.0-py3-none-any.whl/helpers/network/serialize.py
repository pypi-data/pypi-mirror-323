from typing import Protocol, Any, TypeVar, Generic, TypeAlias
from helpers.network.scaler import InputScaler, OutputScaler

import os
import torch
import msgspec.json as json
import joblib


ConfigurationT = TypeVar("ConfigurationT")
NetworkT = TypeVar("NetworkT", covariant=True)


StateDict: TypeAlias = dict[str, Any]


class NeuralNetwork(Protocol):
    def configuration(self) -> Any:
        """Returns the parameters of the network."""
        ...

    def state(self) -> StateDict:
        """Returns the state of the network."""
        ...

    def input_scaler(self) -> InputScaler:
        """Returns the input scaler of the network."""
        ...

    def output_scaler(self) -> OutputScaler:
        """Returns the output scaler of the network."""
        ...


class NeuralNetworkCreator(Protocol, Generic[ConfigurationT, NetworkT]):
    def create(
        self,
        configuration: ConfigurationT,
        state: StateDict,
        *,
        input_scaler: InputScaler,
        output_scaler: OutputScaler,
    ) -> NetworkT:
        """Creates a new network with the given configuration and state."""
        ...

    def configuration_type(self) -> type[ConfigurationT]:
        """Returns the type of the configuration."""
        ...


def save(network: NeuralNetwork, *, to: str) -> None:
    os.makedirs(to, exist_ok=True)
    remove_check_file(to)

    torch.save(network.state(), f"{to}/state.pth")
    joblib.dump(network.input_scaler(), f"{to}/input-scaler.joblib")
    joblib.dump(network.output_scaler(), f"{to}/output-scaler.joblib")

    with open(f"{to}/configuration.json", "wb") as file:
        file.write(json.encode(network.configuration()))

    create_check_file(to)


def load(
    path: str, *, using: NeuralNetworkCreator[ConfigurationT, NetworkT]
) -> NetworkT:
    assert os.path.exists(
        path
    ), f"The directory {path} containing the network does not exist."

    check_check_file(path)

    state = torch.load(f"{path}/state.pth", weights_only=True)
    input_scaler = joblib.load(f"{path}/input-scaler.joblib")
    output_scaler = joblib.load(f"{path}/output-scaler.joblib")

    with open(f"{path}/configuration.json", "rb") as file:
        parameters = json.decode(file.read(), type=using.configuration_type())

    return using.create(
        parameters, state, input_scaler=input_scaler, output_scaler=output_scaler
    )


def remove_check_file(path: str) -> None:
    try:
        os.remove(f"{path}/serialization.complete")
    except FileNotFoundError:
        pass


def create_check_file(path: str) -> None:
    with open(f"{path}/serialization.complete", "w") as file:
        file.write(
            "This file is used to check if the serialization completed successfully."
        )


def check_check_file(path: str) -> None:
    if not os.path.exists(f"{path}/serialization.complete"):
        raise RuntimeError(
            "Looks like the model was not serialized properly. "
            "Unfortunately, you can't reliably load it."
        )
