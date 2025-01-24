from typing import Sequence, Final
from dataclasses import dataclass, KW_ONLY, field

from helpers.maths import Vector
from helpers.robot.simulate.results import SimulationResults, RobotT
from helpers.robot.simulate.solver import LsodaSolver
from helpers.robot.simulate.types import (
    ControlSignal,
    StatefulControlSignal,
    State,
    Position,
    Jacobian,
    Gravity,
)

from scipy.interpolate import interp1d

import numpy as np


GOOD_STEP_SIZE: Final[float] = 0.001


@dataclass
class ControlSignalRecorder:
    _: KW_ONLY
    target_t: float
    delta_t: float

    tau: Final[ControlSignal]
    tolerance: Final[float]

    recorded_t: list[float] = field(default_factory=list)
    recorded_tau: list[Vector] = field(default_factory=list)

    @staticmethod
    def recording(
        tau: ControlSignal,
        *,
        t: Vector,
        tolerance: float = 1e-10,
    ) -> "ControlSignalRecorder":
        delta_t = t[1] - t[0]

        return ControlSignalRecorder(
            target_t=t[0],
            delta_t=delta_t,
            tau=tau,
            tolerance=tolerance,
        )

    def __call__(
        self, *, q: State, p: Position, J: Jacobian, g: Gravity, t: float
    ) -> Vector:
        tau = self.tau(q=q, p=p, J=J, g=g, t=t)

        if self.target_t - self.tolerance < t:
            self._record(t, tau)

        return tau

    def torques(self, t: Vector, *, skip_first: bool) -> list[Vector]:
        # We may have not gotten every time point, due to how the ODE solver works, so
        # we will now linearly interpolate the missing values. Each element of the recorded_tau
        # list corresponds to full control signal for a given time point.
        if skip_first:
            recorded_t = self.recorded_t[1:]
            recorded_tau = self.recorded_tau[1:]
        else:
            recorded_t = self.recorded_t
            recorded_tau = self.recorded_tau

        recorded_t = np.array(recorded_t)
        recorded_tau = np.array(recorded_tau)

        # TODO: interp1d is deprecated, so it should be replaced with something else.
        interpolator = interp1d(
            recorded_t,
            recorded_tau,
            bounds_error=False,
            fill_value=(recorded_tau[0], recorded_tau[-1]),  # type: ignore
            axis=0,
            kind="linear" if len(recorded_t) > 1 else "zero",
            assume_sorted=True,
            copy=False,
        )

        return [row for row in interpolator(t).T]

    def _record(self, t: float, tau: Vector) -> None:
        self.recorded_t.append(t)
        self.recorded_tau.append(tau)
        self.target_t += self.delta_t


class RobotArmSimulationMixin:
    def simulate(
        self: RobotT,
        tau: ControlSignal | StatefulControlSignal,
        *,
        t_range: tuple[float, float],
        recorded_points: int | None = None,
        initial_velocities: Sequence[float] | None = None,
        initial_conditions: Sequence[float] | Vector | None = None,
        skip_first: bool = False,
    ) -> SimulationResults[RobotT]:
        """Simulates the robot arm dynamics.

        Args:
            tau: The input torques to the robot arm.
            t_range: The time range to simulate the robot arm dynamics over.
            recorded_points: The number of points to record the simulation results at (determined automatically by default).
            initial_velocities: The initial velocities of the robot arm joints (defaults to all zeros).
            initial_conditions: The initial conditions of the robot arm as a state vector (optional).
            skip_first: Whether to skip the first recorded point (default is `False`). This is useful
                when combining multiple simulations together, but it's mostly used internally.

        Returns:
            The simulation results for the robot arm dynamics.

        Note:
            If the initial conditions are not provided, the ones provided by the robot arm will be used. Also,
            if you are specifying the initial conditions, specifying the initial velocities is no longer necessary
            or possible. These should be included in the initial conditions vector.
        """
        assert (
            recorded_points is None or recorded_points > 1
        ), f"The number of recorded points must be greater than 1. Got: {recorded_points}"

        assert (
            t_range[0] < t_range[1]
        ), f"The time range is incorrectly ordered. Got: {t_range}"

        if isinstance(tau, StatefulControlSignal):
            tau.reset()

        time_span = t_range[1] - t_range[0]
        recorded_points = recorded_points or int(time_span / GOOD_STEP_SIZE)
        t = np.linspace(*t_range, recorded_points)

        recorder = ControlSignalRecorder.recording(tau, t=t)
        dynamics = self.dynamics_for(recorder)
        solver = dynamics.solver() or LsodaSolver()

        solution = solver(
            dynamics=dynamics,
            initial_conditions=(
                initial_conditions
                if initial_conditions is not None
                else self.initial_conditions(initial_velocities=initial_velocities)
            ),
            t_range=t_range,
            t_evaluation=t,
        )

        if skip_first:
            t = t[1:]
            solution = solution[:, 1:]
            recorded_points -= 1

        return self.results_from(
            t_range=t_range,
            recorded_points=recorded_points,
            t=t,
            tau=recorder.torques(t, skip_first=skip_first),
            solution=solution,
        )
