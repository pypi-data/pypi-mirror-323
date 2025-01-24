from typing import Sequence, Protocol, Iterable
from dataclasses import dataclass, field
from helpers.maths import Vector
from helpers.robot.simulate import (
    ControlSignal,
    State,
    Position,
    Jacobian,
    Gravity,
)

import numpy as np


class Trajectory(Protocol):
    def __call__(self, t: float) -> Vector:
        """Returns the target setpoint for the given time point."""
        ...


class ControlSignalProvider(Protocol):
    def __call__(self, target: Vector, /) -> ControlSignal:
        """Returns a control signal for the given target setpoint."""
        ...


class DistanceMeasure(Protocol):
    def __call__(self, *, q: State, p: Position, t: float, target: Vector) -> float:
        """Returns the distance between the current position (not necessarily in task space) and the
        target setpoint."""
        ...


class ControlSignalWithoutModel(Protocol):
    def __call__(self, *, q: State, p: Position, J: Jacobian, t: float) -> Vector:
        """Returns the control signal for the robot arm at the given time point.

        Args:
            q: The state of the robot arm joints, including the configuration and velocities.
            p: The position of the robot arm.
            J: The Jacobian matrix of the robot arm.
            t: The current time point.

        Returns:
            The control signal for the robot arm for the given time point.

        Note:
            In this case, information about the gravity force acting on the robot arm is not provided.
            This would typically be the case when none of the system parameters are known, except for
            easily measurable physical quantities like the dimensions of the robot arm, the joint angles,
            and the joint velocities.
        """
        ...


class ControlSignalWithTime(Protocol):
    def __call__(self, t: float, /) -> Vector:
        """Returns the control signal for the robot arm at the given time point.

        Args:
            t: The current time point.

        Returns:
            The control signal for the robot arm for the given time point.

        Note:
            This is useful when the control signal is time-dependent and does not require any information
            about the state of the robot arm.
        """
        ...


@dataclass
class SetpointFollower:
    setpoints: Sequence[Vector]
    control_provider: ControlSignalProvider
    distance: DistanceMeasure
    threshold: float
    current_setpoint_index: int = field(init=False, default=0)
    current_control: ControlSignal = field(init=False)

    def __post_init__(self) -> None:
        assert len(self.setpoints) > 0, "At least one setpoint must be provided."

        self.update_control_signal()

    def __call__(
        self, q: State, p: Position, J: Jacobian, g: Gravity, t: float
    ) -> Vector:
        while self.setpoints_remaining() and self.setpoint_reached(q, p, t):
            self.advance_setpoint()

        return self.current_control(q=q, p=p, J=J, g=g, t=t)

    def reset(self) -> None:
        self.current_setpoint_index = 0
        self.update_control_signal()

    def advance_setpoint(self) -> None:
        self.current_setpoint_index += 1
        self.update_control_signal()

    def update_control_signal(self) -> None:
        self.current_control = self.control_provider(self.current_setpoint)

    def setpoints_remaining(self) -> bool:
        return self.current_setpoint_index < (len(self.setpoints) - 1)

    def setpoint_reached(self, q: State, p: Position, t: float) -> bool:
        return (
            self.distance(q=q, p=p, t=t, target=self.current_setpoint) < self.threshold
        )

    @property
    def current_setpoint(self) -> Vector:
        return self.setpoints[self.current_setpoint_index]


@dataclass(frozen=True)
class TrajectoryFollower:
    trajectory: Trajectory
    control_provider: ControlSignalProvider

    def __call__(
        self, q: State, p: Position, J: Jacobian, g: Gravity, t: float
    ) -> Vector:
        return self.control_provider(self.trajectory(t))(q=q, p=p, J=J, g=g, t=t)


def without_model(tau: ControlSignalWithoutModel) -> ControlSignal:
    """Makes a control signal without model information.

    Args:
        tau: The control signal without model.

    Returns:
        The control signal with model.

    Example:
        If your control logic does not require model information, you can use this function to
        create a valid control signal as follows:

        ```python
        # Import the control module

        def signal(q: State, p: Position, J: Jacobian, t: float) -> Vector:
            # Your control logic here
            return ...

        tau = control.without_model(signal)

        # Now you can use `tau` as a regular control signal.
        results = robot.simulate(t, tau)
    """
    return lambda q, p, J, g, t: tau(q=q, p=p, J=J, t=t)


def with_time(tau: ControlSignalWithTime) -> ControlSignal:
    """Makes a time-dependent control signal.

    Args:
        tau: The time-dependent control signal.

    Returns:
        The control signal with model.

    Example:
        If your control logic depends only on the current time point, you can use this function to
        create a valid control signal as follows:

        ```python
        # Import the control module

        def signal(t: float) -> Vector:
            # Your control logic here
            return ...

        tau = control.with_time(signal)

        # Now you can use `tau` as a regular control signal.
        results = robot.simulate(t, tau)
    """
    return lambda q, p, J, g, t: tau(t)


def zero(n: int) -> ControlSignal:
    """Generates a zero control signal.

    Args:
        n: The number of joints of the robot arm.

    Returns:
        The zero control signal that can be directly used as a control signal.
    """

    return lambda q, p, J, g, t: np.zeros(n)


def constant(value: Vector | Iterable[float]) -> ControlSignal:
    """Generates a constant control signal.

    Args:
        value: The constant value of the control signal.

    Returns:
        The constant control signal that can be directly used as a control signal.
    """

    value = np.array(value)

    return lambda q, p, J, g, t: value


def step(*, amplitudes: Sequence[float], t_range: tuple[float, float]) -> ControlSignal:
    """Generates a step signal.

    Args:
        amplitudes: The amplitudes of the step signals for each joint.
        step_time: The time at which the step occurs.

    Returns:
        The step signal that can be directly used as a control signal.
    """

    amplitude = np.array(amplitudes)
    t_0, _ = t_range

    def signal(t_c: float) -> Vector:
        return (amplitude * (t_c >= t_0)).astype(float)

    return lambda q, p, J, g, t: signal(t)


def ramp(*, slopes: Sequence[float], t_range: tuple[float, float]) -> ControlSignal:
    """Generates a ramp signal.

    Args:
        slopes: The slopes of the ramp signals for each joint.
        start_time: The time at which the ramp starts (default is 0).
        end_time: The time at which the ramp ends (default is the end of the time vector).

    Returns:
        The ramp signal that can be directly used as a control signal.
    """

    slope = np.array(slopes)
    t_0, t_f = t_range

    def signal(t_c: float) -> Vector:
        if t_c < t_0:
            return np.zeros_like(slope)
        elif t_c > t_f:
            return slope * (t_f - t_0)
        else:
            return slope * (t_c - t_0)

    return lambda q, p, J, g, t: signal(t)


def chirp(
    *,
    amplitudes: Sequence[float],
    start_frequencies: Sequence[float],
    end_frequencies: Sequence[float],
    fading_factor: float = 2,
    t_range: tuple[float, float],
) -> ControlSignal:
    """Generates a chirp signal.

    Args:
        amplitudes: The amplitudes of the chirp signals for each joint.
        start_frequencies: The start frequencies of the chirp signals for each joint.
        end_frequency: The end frequency of the chirp signals for each joint.
        fading_factor: The fading factor for the chirp signal (default is 2).
        t_range: The time range of the chirp signal.

    Returns:
        The chirp signal that can be directly used as a control signal.
    """

    amplitude = np.array(amplitudes)
    start = np.array(start_frequencies)
    end = np.array(end_frequencies)

    t_0, t_f = t_range
    delta_t = t_f - t_0

    def signal(t_c: float) -> Vector:
        frequencies = start + (end - start) * (t_c - t_0) / delta_t
        return (
            amplitude
            * np.sin(2 * np.pi * frequencies * t_c)
            * (1 - np.exp(-((t_f - t_c) ** 2) * fading_factor))
        )

    return lambda q, p, J, g, t: signal(t)
