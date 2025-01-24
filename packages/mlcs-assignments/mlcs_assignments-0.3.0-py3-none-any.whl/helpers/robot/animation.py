from typing import NamedTuple, Protocol, TypeVar, Generic, Iterable, overload, Literal
from dataclasses import dataclass
from helpers.robot.arm import AnimatableRobotArm
from helpers.ui import basic_animation_configuration

import plotly.graph_objects as go


class JointAngles(NamedTuple):
    """Angles describing the configuration of a robot arm.

    Attributes:
        theta_1: The angle of the first joint.
        theta_2: The angle of the second joint.

    Example:
        This is useful for animating the robot arm at different configurations. See the
        [`animate`](helpers.robot.animation.html#helpers.robot.animation.animate) function for more details.
    """

    theta_1: float
    theta_2: float

    @staticmethod
    def combining(
        theta_1s: Iterable[float], theta_2s: Iterable[float]
    ) -> list["JointAngles"]:
        """Combines two lists of angles into a single list of `JointAngles`."

        Args:
            theta_1s: The angles of the first joint.
            theta_2s: The angles of the second joint.

        Returns:
            A list of `JointAngles` where each element is a pair of angles from the input lists.

        Example:
            ```python
            theta_1s = [pi, pi / 2, 0]
            theta_2s = [0, pi / 2, pi]
            joint_angles = JointAngles.combining(theta_1s, theta_2s)
            print(joint_angles)
            # Output: [
            #   JointAngles(theta_1=pi, theta_2=0),
            #   JointAngles(theta_1=pi / 2, theta_2=pi / 2),
            #   JointAngles(theta_1=0, theta_2=pi)
            # ]
            ```
        """
        return [
            JointAngles(theta_1, theta_2)
            for theta_1, theta_2 in zip(theta_1s, theta_2s)
        ]


RobotT = TypeVar("RobotT", infer_variance=True, bound=AnimatableRobotArm)


class AnimationFramesProvider(Protocol, Generic[RobotT]):
    def __call__(
        self, robot: RobotT, joint_angles: list[JointAngles]
    ) -> list[go.Figure]:
        """Returns the frames of the robot arm animation."""
        ...


class OnDraw(Protocol):
    def __call__(self, figure: go.Figure) -> go.Figure:
        """Modifies the given figure containing a visualization of the robot arm."""
        ...


class DoNothing:
    def __call__(self, figure: go.Figure) -> go.Figure:
        return figure


@dataclass(frozen=True)
class RobotAnimator(Generic[RobotT]):
    animation_frames_for: AnimationFramesProvider[RobotT]

    @staticmethod
    def using(
        animation_frames_for: AnimationFramesProvider[RobotT],
    ) -> "RobotAnimator[RobotT]":
        """Creates an `Animator` with the given `animation_frames_for` function."""
        return RobotAnimator(animation_frames_for)

    @overload
    def animate(
        self,
        robot: RobotT,
        joint_angles: list[JointAngles],
        *,
        align_starting_position: bool = False,
        subtitle: str = "",
        on_draw: OnDraw = DoNothing(),
    ) -> None: ...

    @overload
    def animate(
        self,
        robot: RobotT,
        joint_angles: list[JointAngles],
        *,
        align_starting_position: bool = False,
        subtitle: str = "",
        on_draw: OnDraw = DoNothing(),
        show: Literal[False],
    ) -> go.Figure: ...

    def animate(
        self,
        robot: RobotT,
        joint_angles: list[JointAngles],
        *,
        align_starting_position: bool = False,
        subtitle: str = "",
        on_draw: OnDraw = DoNothing(),
        show: bool = True,
    ) -> go.Figure | None:
        """Animates the robot arm moving through the given joint angles.

        Args:
            robot: The robot arm to animate.
            joint_angles: The joint angles to animate the robot arm through.
            align_starting_position: Whether to align the starting position of the robot arm with the first joint angle.
            subtitle: The subtitle of the animation.
            on_draw: A function that modifies the figure containing the visualization of the robot arm.
            show: Whether to show the animation.

        Returns:
            If `show` is `False`, returns the animation figure.

        Note:
            It is not guaranteed that the `on_draw` function will be called directly after the figure is drawn (e.g.
            it may be called after all frames are generated). The exact timing of the `on_draw` function being called
            depends on the implementation of this function and is not guaranteed, however, it will be called exactly
            once for each frame of the animation.

        Example:
            if you want to show the robot arm moving through the configurations:

            (0, 0) -> (pi/6, 0) -> (pi/5, 0) -> (pi/4, pi/6) -> (pi/3, pi/6) -> (pi/2, pi/6)

            You can do that with the following code:

            ```python
            robot = ... # Some robot arm
            joint_angles = [
                JointAngles(0, 0),
                JointAngles(pi/6, 0),
                JointAngles(pi/5, 0),
                JointAngles(pi/4, pi/6),
                JointAngles(pi/3, pi/6),
                JointAngles(pi/2, pi/6),
            ]

            animate(robot, joint_angles)
            # This will animate the robot arm moving through the configurations.
            ```

            This animation would look quite ugly though. To make a nice smooth animation, you should use
            much more intermediate configurations (e.g. 100).
        """
        if align_starting_position:
            robot.rotate_to(*joint_angles[0])

        frames = self.animation_frames_for(robot, joint_angles)
        start = frames[0]
        frame_count = len(frames)

        def with_progress(figure: go.Figure, index: int) -> go.Frame:
            return frame_with_progress_from(figure, index=index, total=frame_count)

        figure = animation_figure(
            frames=[
                with_progress(on_draw(figure), index=index)
                for index, figure in enumerate(frames, start=1)
            ],
            layout=start.layout,  # type: ignore
            title=f"Animated {robot.name} {subtitle}",
        )

        if show:
            figure.show()
        else:
            return figure


def animation_figure(
    frames: list[go.Frame],
    layout: go.Layout,
    title: str,
) -> go.Figure:
    figure = go.Figure(
        data=frames[0].data,
        layout=layout,
        frames=frames,
    )
    figure.update_layout(
        title=title,
        updatemenus=[basic_animation_configuration()],
    )
    return figure


def frame_with_progress_from(figure: go.Figure, *, index: int, total: int) -> go.Frame:
    return go.Frame(
        data=with_progress_information(figure, index=index, total=total).data
    )


def with_progress_information(
    figure: go.Figure, *, index: int, total: int
) -> go.Figure:
    x, y = progress_information_location_for(figure)

    figure.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="text",
            text=[f"Frame {index} of {total}"],
            textposition="middle center",
            showlegend=False,
        )
    )
    return figure


def progress_information_location_for(figure: go.Figure) -> tuple[float, float]:
    assert (
        figure.layout.yaxis.range is not None  # type: ignore
    ), "Looks like the y-axis range is not set for this robot arm drawing."

    return 0.0, figure.layout.yaxis.range[1] * 0.95  # type: ignore
