from typing import Protocol, TypeVar, Generic, Self, Sequence
from dataclasses import dataclass, KW_ONLY  #

from helpers.maths import Matrix, Vector
from helpers.robot.animation import JointAngles
from helpers.robot.simulate.types import (
    ControlSignal,
    RobotDynamics,
    State,
    Position,
    Jacobian,
    Gravity,
)

import os
import numpy as np
import pandas as pd

RobotT = TypeVar("RobotT", bound="SimulatableRobotArm", covariant=True)
InvariantRobotT = TypeVar("InvariantRobotT", bound="SimulatableRobotArm")


@dataclass(frozen=True)
class SimulationResultsExporter:
    results: list["SimulationResults"]

    def to(self, directory: str) -> None:
        """Exports the simulation results to a CSV file.

        Args:
            directory: The directory to save the simulation results to.

        Example:
            ```python
            results_1 = ... # Some simulation results
            results_2 = ... # Some other simulation results

            SimulationResults.export(results_1, results_2).to("path/to/directory")
            # The simulation results will be saved under the specified directory.
            ```
        """
        os.makedirs(directory, exist_ok=True)

        for i, results in enumerate(self.results):
            results.save_to(f"{directory}/results_{i + 1}.csv")


@dataclass(frozen=True)
class SimulationResults(Generic[RobotT]):
    """The results of a robot arm simulation.

    Attributes:
        t: The time points of the simulation.
        tau: The torques applied to the robot arm. Each vector corresponds to a joint.
        q: The joint angles of the robot arm. Each vector corresponds to a joint.
        q_dot: The joint velocities of the robot arm. Each vector corresponds to a joint.
        robot: The robot arm for which the simulation results were generated.

    Example:
        ```python
        results = robot.simulate(t, tau)

        # You can animate the results of the simulation like this:
        results.animate()

        # You can save the results to a file like this:
        results.save_to("path/to/file.csv")
        ```
    """

    _: KW_ONLY
    t: Vector
    tau: list[Vector]
    q: list[Vector]
    q_dot: list[Vector]

    robot: RobotT

    _recorded_points: int
    _t_range: tuple[float, float]
    _final_state: Vector

    @staticmethod
    def of(
        robot: InvariantRobotT,
        *,
        t_range: tuple[float, float],
        recorded_points: int,
        t: Vector,
        tau: list[Vector],
        q: list[Vector],
        q_dot: list[Vector],
        final_state: Vector,
    ) -> "SimulationResults[InvariantRobotT]":
        return SimulationResults(
            t=t,
            tau=tau,
            q=q,
            q_dot=q_dot,
            robot=robot,
            _t_range=t_range,
            _recorded_points=recorded_points,
            _final_state=final_state,
        )

    @staticmethod
    def export(*results: "SimulationResults") -> SimulationResultsExporter:
        """Creates an exporter for the simulation results.

        Args:
            results: The simulation results to be exported.

        Returns:
            The exporter for the simulation results.

        Note:
            See [`SimulationResultsExporter`](exercise_2.md#helpers.robot.simulate.SimulationResultsExporter) for
            more details on how to export the simulation results.
        """
        return SimulationResultsExporter(list(results))

    def animate(
        self: "SimulationResults[AnimatedRobotArm]",
        *,
        take: int = 1,
    ) -> "SimulationResults[AnimatedRobotArm]":
        """Animates the results of the robot arm simulation.

        Args:
            take: The stride to take when animating the simulation results. A stride of `1` will animate every
                recorded point, a stride of `2` will animate every other recorded point, and so on.

        Note:
            This will only work if the robot for which the simulation results were generated is an
            [`AnimatedRobotArm`](exercise_2.md#helpers.robot.simulate.AnimatedRobotArm).
        """

        self.robot.animate(JointAngles.combining(self.q[0], self.q[1])[::take])
        return self

    def save_to(self, file: str) -> None:
        """Saves the simulation results to a file as a CSV.

        Args:
            file: The file path to save the simulation results to.
        """
        pd.DataFrame(
            {
                "Time (s)": self.t,
                **{f"Joint {i + 1} Torque (Nm)": tau for i, tau in enumerate(self.tau)},
                **{f"Joint {i + 1} Angle (rad)": q for i, q in enumerate(self.q)},
                **{
                    f"Joint {i + 1} Velocity (rad/s)": q_dot
                    for i, q_dot in enumerate(self.q_dot)
                },
            }
        ).to_csv(file, index=False, header=True)

    def continue_with(
        self,
        tau: ControlSignal,
        *,
        t_range: tuple[float, float] | None = None,
        recorded_points: int | None = None,
    ) -> "SimulationResults[RobotT]":
        """Continues the simulation with the given control signal.

        Args:
            tau: The control signal to continue the simulation with.
            t: The time span to evaluate the simulation over.

        Returns:
            The simulation results of the continued simulation with the given control signal.

        Note:
            The simulation will continue from the final time point of the current simulation results. If a
            new time span is provided, the simulation will continue over that time span. If no time span is
            provided, the simulation will continue for the same amount of time as the span of the original
            simulation results.

            It does not matter if the specified time span starts at 0 or at the final time point of the
            current simulation results. The simulation will always continue from the final time point of the
            current simulation results.
        """
        recorded_points = recorded_points or self._recorded_points
        t_0, t_f = t_range or self._t_range

        t_span = t_f - t_0
        delta_t = t_span / (recorded_points - 1)
        start_time = self._final_time + delta_t
        start_tau = self._final_tau

        def combined_tau(
            q: State, p: Position, J: Jacobian, g: Gravity, t: float
        ) -> Vector:
            return start_tau if t < start_time else tau(q=q, p=p, J=J, g=g, t=t)

        return self._extend(
            self.robot.simulate(
                combined_tau,
                t_range=(self._final_time, start_time + t_span),
                recorded_points=recorded_points + 1,
                initial_conditions=self._final_state,
                skip_first=True,
            )
        )

    def _extend(
        self, other: "SimulationResults[RobotT]"
    ) -> "SimulationResults[RobotT]":
        """Extends the simulation results with another set of simulation results."""
        return SimulationResults.of(
            self.robot,
            t_range=self._t_range,
            recorded_points=self._recorded_points,
            t=np.concat([self.t, other.t]),
            tau=[
                np.concat([self_tau, other_tau])
                for self_tau, other_tau in zip(self.tau, other.tau)
            ],
            q=[
                np.concat([self_q, other_q]) for self_q, other_q in zip(self.q, other.q)
            ],
            q_dot=[
                np.concat([self_q_dot, other_q_dot])
                for self_q_dot, other_q_dot in zip(self.q_dot, other.q_dot)
            ],
            final_state=other._final_state,
        )

    @property
    def _final_time(self) -> float:
        """Returns the final time of the simulation."""
        return self.t[-1]

    @property
    def _final_tau(self) -> Vector:
        """Returns the final torques of the simulation."""
        return np.array([tau[-1] for tau in self.tau])


class SimulatableRobotArm(Protocol):
    def simulate(
        self,
        tau: ControlSignal,
        *,
        t_range: tuple[float, float],
        recorded_points: int | None = None,
        initial_velocities: Sequence[float] | None = None,
        initial_conditions: Sequence[float] | Vector | None = None,
        skip_first: bool = False,
    ) -> SimulationResults[Self]:
        """Simulates the robot arm dynamics."""
        ...

    def dynamics_for(self, tau: ControlSignal) -> RobotDynamics:
        """Returns the dynamics of the robot arm for the given input torques."""
        ...

    def results_from(
        self,
        *,
        t_range: tuple[float, float],
        recorded_points: int,
        t: Vector,
        tau: list[Vector],
        solution: Matrix,
    ) -> SimulationResults[Self]:
        """Returns the simulation results of the robot arm."""
        ...

    def initial_conditions(self, initial_velocities: Sequence[float] | None) -> Vector:
        """The initial conditions of the robot arm."""
        ...


class AnimatedRobotArm(SimulatableRobotArm, Protocol):
    def animate(self, joint_angles: list[JointAngles]) -> None:
        """Animates the robot arm moving through the given joint angles. See the
        [`animate`](exercise_2.md#helpers.robot.RobotAnimator.animate) function for more details."""
        ...
