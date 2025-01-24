from typing import Final, override, Sequence, Any, TypeAlias, Protocol
from dataclasses import dataclass, KW_ONLY, replace
from helpers.maths import Point
from helpers.robot.animation import (
    AnimatableRobotArm,
    JointAngles,
    RobotAnimator,
    DoNothing,
)
from helpers.robot.arm import RobotArmMixin
from helpers.robot.link import Link

import numpy as np
from plotly.graph_objects import Figure, Scatter

LINK_WIDTH: Final[float] = 0.15

Styling: TypeAlias = dict[str, Any]


@dataclass(frozen=True)
class StylingOverrides:
    _: KW_ONLY
    opacity: float
    trace_color: str
    name: str | None

    @staticmethod
    def none() -> "StylingOverrides":
        return StylingOverrides(opacity=1.0, trace_color="LightBlue", name=None)

    def __post_init__(self):
        assert (
            0 <= self.opacity <= 1
        ), f"Opacity must be between 0 and 1. Got {self.opacity}."

    def fill_name(self, name: str) -> "StylingOverrides":
        return replace(self, name=name) if self.name is None else self


class AnimatablePlanarRobotArm(AnimatableRobotArm, Protocol):
    @override
    def draw(
        self,
        *,
        show: bool = True,
        trace: Sequence[Point] = (),
        overrides: StylingOverrides = StylingOverrides.none(),
    ) -> Figure:
        """Draws the robot arm in two dimensions."""
        ...

    @property
    def link_1(self) -> Link:
        """The first link of the robot arm."""
        ...

    @property
    def link_2(self) -> Link:
        """The second link of the robot arm."""
        ...

    @override
    def _draw_trace(
        self,
        trace: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides = StylingOverrides.none(),
    ) -> Figure:
        """Draws the trace of the end effector of the robot arm on the given figure."""
        ...

    @override
    def _draw_robot(
        self,
        joint_positions: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides = StylingOverrides.none(),
    ) -> Figure:
        """Draws the robot arm on the given figure."""
        ...

    def _draw_joints(
        self,
        joint_positions: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides,
    ) -> Figure:
        """Draws the joints of the robot arm on the given figure."""
        ...

    def _draw_links(
        self,
        joint_positions: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides,
    ) -> Figure:
        """Draws the links of the robot arm on the given figure."""
        ...

    def _draw_centers_of_mass(
        self,
        centers_of_mass: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides,
    ) -> Figure:
        """Draws the centers of mass of the links of the robot arm on the given figure."""
        ...

    def _trace_style(self, *, overrides: StylingOverrides) -> Styling:
        """The style of the trace of the end effector of the robot arm."""
        ...

    def _joint_style(self, *, overrides: StylingOverrides) -> Styling:
        """The style of the joints of the robot arm."""
        ...

    def _link_style(self, *, overrides: StylingOverrides) -> Styling:
        """The style of the links of the robot arm."""
        ...

    def _center_of_mass_style(self, *, overrides: StylingOverrides) -> Styling:
        """The style of the centers of mass of the robot arm."""
        ...

    @property
    def _links(self) -> list[Link]:
        """The links of the robot arm."""
        ...


class PlanarRobotAnimationMixin(RobotArmMixin):
    """This mixin overrides some details of [`RobotArmMixin`](exercise_2.md#helpers.robot.RobotArmMixin) on
    how the robot arm is visualized during animations. It also provides an `animate` method directly
    on the robot arm object, without the need to use the [`RobotAnimator`](exercise_2.md#helpers.robot.RobotAnimator)
    class.

    Example:
        ```python
        robot = ... # Some robot arm object that uses the `PlanarRobotAnimationMixin`
        joint_angles = [(0, 0), (np.pi / 2, np.pi / 2), (np.pi, np.pi)]

        robot.animate(joint_angles)
        # This will animate the robot arm moving through the given joint angles.
        ```
    """

    def animate(
        self: AnimatablePlanarRobotArm,
        joint_angles: list[JointAngles],
        *,
        predicted_joint_angles: list[JointAngles] | None = None,
        align_starting_position: bool = False,
        subtitle: str = "",
    ) -> None:
        """Animates the robot arm moving through the given joint angles. See the
        [`animate`](exercise_2.md#helpers.robot.RobotAnimator.animate) function for more details.
        """
        RobotAnimator.using(PlanarRobotAnimationFramesProvider()).animate(
            self,
            joint_angles,
            align_starting_position=align_starting_position,
            subtitle=subtitle,
            on_draw=DrawPrediction.of(
                self,
                predicted_joint_angles,
                opacity=0.35,
                trace_color="rgba(255, 183, 77, 0.5)",
            )
            if predicted_joint_angles is not None
            else DoNothing(),
        )

    @override
    def draw(
        self: AnimatablePlanarRobotArm,
        *,
        show: bool = True,
        trace: Sequence[Point] = (),
        overrides: StylingOverrides = StylingOverrides.none(),
    ) -> Figure:
        overrides = overrides.fill_name(self.name)
        joint_positions = self.joint_positions()

        figure = Figure()

        if trace:
            figure = self._draw_trace(trace, figure, overrides=overrides)

        figure = self._draw_robot(joint_positions, figure, overrides=overrides)

        self._set_layout_for(figure)

        if show:
            figure.show()

        return figure

    @override
    def _draw_trace(
        self: AnimatablePlanarRobotArm,
        trace: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides = StylingOverrides.none(),
    ) -> Figure:
        figure.add_trace(
            Scatter(
                x=[point.x for point in trace],
                y=[point.y for point in trace],
                **self._trace_style(overrides=overrides),
            ),
        )

        return figure

    @override
    def _draw_robot(
        self: AnimatablePlanarRobotArm,
        joint_positions: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides = StylingOverrides.none(),
    ) -> Figure:
        figure = self._draw_joints(joint_positions, figure, overrides=overrides)
        figure = self._draw_links(joint_positions, figure, overrides=overrides)

        return figure

    def _draw_joints(
        self: AnimatablePlanarRobotArm,
        joint_positions: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides,
    ) -> Figure:
        figure.add_trace(
            Scatter(
                x=[point.x for point in joint_positions],
                y=[point.y for point in joint_positions],
                **self._joint_style(overrides=overrides),
            ),
        )

        return figure

    def _draw_links(
        self: AnimatablePlanarRobotArm,
        joint_positions: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides,
    ) -> Figure:
        link_width = LINK_WIDTH
        centers_of_mass: list[Point] = []

        for i, (p_1, p_2, link) in enumerate(
            zip(joint_positions, joint_positions[1:], self._links)
        ):
            # Calculate positions of the rectangle corners
            angle = np.arctan2(p_2.y - p_1.y, p_2.x - p_1.x)
            dx = link_width / 2 * np.sin(angle)
            dy = -link_width / 2 * np.cos(angle)

            points = [
                Point(p_1.x - dx, p_1.y - dy),
                Point(p_1.x + dx, p_1.y + dy),
                Point(p_2.x + dx, p_2.y + dy),
                Point(p_2.x - dx, p_2.y - dy),
            ]

            # Calculate the center of mass of the link
            centers_of_mass.append(
                Point(
                    x=p_1.x + link.distance_to_com * np.cos(angle),
                    y=p_1.y + link.distance_to_com * np.sin(angle),
                )
            )

            figure.add_trace(
                Scatter(
                    # The extra point at the end closes the rectangle
                    x=[p.x for p in points] + [points[0].x],
                    y=[p.y for p in points] + [points[0].y],
                    showlegend=i == 0,
                    **self._link_style(overrides=overrides),
                ),
            )

        figure = self._draw_centers_of_mass(
            centers_of_mass, figure, overrides=overrides
        )

        return figure

    def _draw_centers_of_mass(
        self: AnimatablePlanarRobotArm,
        centers_of_mass: Sequence[Point],
        figure: Figure,
        *,
        overrides: StylingOverrides,
    ) -> Figure:
        figure.add_trace(
            Scatter(
                x=[point.x for point in centers_of_mass],
                y=[point.y for point in centers_of_mass],
                **self._center_of_mass_style(overrides=overrides),
            ),
        )

        return figure

    def _trace_style(
        self: AnimatablePlanarRobotArm, *, overrides: StylingOverrides
    ) -> Styling:
        name, trace_color = overrides.name, overrides.trace_color

        return dict(
            name=f"{name}'s trace",
            mode="lines",
            line=dict(width=2, color=trace_color, dash="dash"),
        )

    def _joint_style(
        self: AnimatablePlanarRobotArm, *, overrides: StylingOverrides
    ) -> Styling:
        opacity, name = overrides.opacity, overrides.name

        return dict(
            name="Joints",
            legendgroup=name,
            legendgrouptitle=dict(text=name),
            mode="markers",
            marker=dict(
                size=10,
                symbol="circle",
                color=f"rgba(0, 0, 255, {opacity})",
                line=dict(width=1, color=f"rgba(0, 0, 0, {opacity})"),
            ),
        )

    def _link_style(
        self: AnimatablePlanarRobotArm, *, overrides: StylingOverrides
    ) -> Styling:
        opacity, name = overrides.opacity, overrides.name

        return dict(
            name="Links",
            legendgroup=name,
            legendgrouptitle=dict(text=name),
            mode="lines",
            line=dict(color=f"rgba(0, 0, 255, {0.75 * opacity})", width=1),
            fill="toself",
            fillcolor=f"rgba(0, 0, 255, {0.15 * opacity})",
        )

    def _center_of_mass_style(
        self: AnimatablePlanarRobotArm, *, overrides: StylingOverrides
    ) -> Styling:
        opacity, name = overrides.opacity, overrides.name

        return dict(
            name="Centers of Mass",
            legendgroup=name,
            legendgrouptitle=dict(text=name),
            mode="markers",
            marker=dict(
                size=10,
                symbol="circle-cross",
                color=f"rgba(0, 0, 255, {0.15 * opacity})",
                line=dict(width=1, color=f"rgba(0, 0, 0, {0.75 * opacity})"),
            ),
        )

    @property
    def _links(self: AnimatablePlanarRobotArm) -> list[Link]:
        return [self.link_1, self.link_2]


@dataclass(frozen=True)
class PlanarRobotAnimationFramesProvider:
    _: KW_ONLY
    overrides: StylingOverrides = StylingOverrides.none()

    def __call__(
        self, robot: AnimatablePlanarRobotArm, joint_angles: list[JointAngles]
    ) -> list[Figure]:
        end_effector_positions: list[Point] = []
        frames: list[Figure] = []

        for theta_1, theta_2 in joint_angles:
            robot.rotate_to(theta_1, theta_2)

            end_effector_positions.append(robot.end_effector_position())
            frames.append(
                robot.draw(
                    show=False,
                    trace=end_effector_positions,
                    overrides=self.overrides,
                )
            )

        return frames


@dataclass
class DrawPrediction:
    prediction_frames: list[Figure]
    current_frame: int = 0

    @staticmethod
    def of(
        robot: AnimatablePlanarRobotArm,
        predicted_joint_angles: list[JointAngles],
        *,
        opacity: float,
        trace_color: str,
    ) -> "DrawPrediction":
        return DrawPrediction(
            PlanarRobotAnimationFramesProvider(
                overrides=StylingOverrides(
                    opacity=opacity,
                    trace_color=trace_color,
                    name=f"(Predicted) {robot.name}",
                )
            )(robot, predicted_joint_angles)
        )

    def __call__(self, figure: Figure) -> Figure:
        assert self.current_frame < len(
            self.prediction_frames
        ), "No more prediction frames to draw."

        figure.add_traces(self.prediction_frames[self.current_frame].data)
        self.current_frame += 1

        return figure
