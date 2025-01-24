from typing import Sequence, Generic, Protocol, TypeVar, Self
from dataclasses import dataclass, KW_ONLY

from helpers.maths import Vector, Matrix
from helpers.robot.animation import JointAngles
from helpers.robot.simulate import (
    SimulatableRobotArm,
    ControlSignal,
    StatefulControlSignal,
    SimulationResults,
    RobotDynamics,
)


SimulatableRobotT = TypeVar(
    "SimulatableRobotT", bound="SimulatableRobotArm", infer_variance=True
)
PredictableRobotT = TypeVar(
    "PredictableRobotT", bound="PredictableRobotArm", covariant=True
)


class PredictableRobotArm(SimulatableRobotArm, Protocol):
    def using_dynamics_from(self, provider: "RobotDynamicsProvider") -> Self:
        """Returns a new robot arm that uses the dynamics model from the given provider."""
        ...


class AnimatedRobotArm(SimulatableRobotArm, Protocol):
    def animate(
        self,
        joint_angles: list[JointAngles],
        *,
        predicted_joint_angles: list[JointAngles] | None = None,
    ) -> None:
        """Animates the robot arm moving through the given joint angles. See the
        [`animate`](exercise_2.md#helpers.robot.RobotAnimator.animate) function for more details.

        Note:
            If `predicted_joint_angles` is provided, the animation should show both the actual and predicted
            joint angles overlaid on top of each other.
        """
        ...


class RobotDynamicsProvider(Protocol, Generic[SimulatableRobotT]):
    def create_for(
        self, robot: SimulatableRobotT, *, torque: ControlSignal
    ) -> RobotDynamics:
        """Creates an object that can simulate the dynamics of the robot for the given torque."""
        ...

    def results_for(
        self,
        robot: SimulatableRobotT,
        *,
        t_range: tuple[float, float],
        recorded_points: int,
        t: Vector,
        tau: list[Vector],
        solution: Matrix,
    ) -> SimulationResults[SimulatableRobotT]:
        """Extracts the simulation results from the specified state matrix."""
        ...


@dataclass(frozen=True)
class PredictionResults(Generic[SimulatableRobotT]):
    _: KW_ONLY
    actual: SimulationResults[SimulatableRobotT]
    predicted: SimulationResults[SimulatableRobotT]

    def animate(
        self: "PredictionResults[AnimatedRobotArm]", *, take: int = 1
    ) -> "PredictionResults[AnimatedRobotArm]":
        actual_angles = angles_from(self.actual)[::take]
        predicted_angles = angles_from(self.predicted)[::take]

        self.actual.robot.animate(
            actual_angles, predicted_joint_angles=predicted_angles
        )

        return self


class RobotArmPredictionMixin:
    def predict(
        self: PredictableRobotT,
        tau: ControlSignal | StatefulControlSignal,
        *,
        model: RobotDynamicsProvider,
        t_range: tuple[float, float],
        recorded_points: int | None = None,
        initial_velocities: Sequence[float] | None = None,
        initial_conditions: Sequence[float] | Vector | None = None,
    ) -> PredictionResults[PredictableRobotT]:
        predictor = self.using_dynamics_from(model)

        predicted_results = predictor.simulate(
            tau,
            t_range=t_range,
            recorded_points=recorded_points,
            initial_velocities=initial_velocities,
            initial_conditions=initial_conditions,
        )

        actual_results = self.simulate(
            tau,
            t_range=t_range,
            recorded_points=recorded_points,
            initial_velocities=initial_velocities,
            initial_conditions=initial_conditions,
        )

        return PredictionResults(actual=actual_results, predicted=predicted_results)


def angles_from(results: SimulationResults) -> list[JointAngles]:
    return JointAngles.combining(results.q[0], results.q[1])
