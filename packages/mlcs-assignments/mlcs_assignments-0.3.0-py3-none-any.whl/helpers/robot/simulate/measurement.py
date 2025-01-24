from dataclasses import dataclass, KW_ONLY
from helpers.network import DataMapper

from numpy import gradient
from pandas import DataFrame
from plotly.subplots import make_subplots
from plotly.graph_objects import Scatter


class infer:
    @staticmethod
    def joint_accelerations(
        *, time: str, accelerations_from: dict[str, str]
    ) -> DataMapper:
        def mapping(data: DataFrame) -> DataFrame:
            return data.assign(
                **{
                    acceleration: gradient(data[velocity], data[time])
                    for acceleration, velocity in accelerations_from.items()
                }
            )

        return mapping


@dataclass(frozen=True)
class MeasurementColumns:
    _: KW_ONLY
    angle: str
    velocity: str
    acceleration: str


def visualize(
    dynamics_data: DataFrame,
    *,
    time: str,
    measurements: list[MeasurementColumns],
    title: str,
) -> None:
    time_data = dynamics_data[time]

    figure = make_subplots(
        rows=len(measurements),
        cols=3,
        shared_xaxes=True,
        subplot_titles=[
            subplot
            for measurement in measurements
            for subplot in (
                measurement.angle,
                measurement.velocity,
                measurement.acceleration,
            )
        ],
        vertical_spacing=0.1,
    )

    for joint, measurement in enumerate(measurements, start=1):
        figure.add_trace(
            Scatter(
                x=time_data,
                y=dynamics_data[measurement.angle],
                mode="lines",
                name=measurement.angle,
                legendgroup=f"Joint {joint}",
            ),
            row=joint,
            col=1,
        )
        figure.add_trace(
            Scatter(
                x=time_data,
                y=dynamics_data[measurement.velocity],
                mode="lines",
                name=measurement.velocity,
                legendgroup=f"Joint {joint}",
            ),
            row=joint,
            col=2,
        )
        figure.add_trace(
            Scatter(
                x=time_data,
                y=dynamics_data[measurement.acceleration],
                mode="lines",
                name=measurement.acceleration,
                legendgroup=f"Joint {joint}",
            ),
            row=joint,
            col=3,
        )

    figure.update_layout(title_text=title, legend_tracegroupgap=90)
    figure.update_xaxes(title_text="Time (s)", row=len(measurements), col=1)

    figure.show()
