from typing import Final, Sequence, Self
from dataclasses import dataclass, field, KW_ONLY, replace

from helpers.maths import Point, Matrix, Vector
from helpers.robot.arm import RobotArmMixin
from helpers.robot.link import Link
from helpers.robot.joint import Joint
from helpers.robot.jacobian import RobotJacobianMixin
from helpers.robot.planar.animation import (
    PlanarRobotAnimationMixin,
)
from helpers.robot.planar.dynamics import RigidBodyDynamics
from helpers.robot.predict import RobotDynamicsProvider, RobotArmPredictionMixin
from helpers.robot.simulate import (
    SimulationResults,
    RobotArmSimulationMixin,
    ControlSignal,
    AnimatedRobotArm,
    RobotDynamics,
)

import numpy as np


@dataclass
class PlanarRobotArm(
    PlanarRobotAnimationMixin,
    RobotArmMixin,
    RobotArmSimulationMixin,
    RobotArmPredictionMixin,
    RobotJacobianMixin,
    AnimatedRobotArm,
):
    _: KW_ONLY
    name: Final[str] = "Helpful Roboto :)"

    link_1: Link
    link_2: Link
    joint_1: Joint = Joint(theta=0.0)
    joint_2: Joint = Joint(theta=0.0)

    rotations: int = field(default=0, init=False)
    dynamics: RobotDynamicsProvider = field(default=RigidBodyDynamics)

    def using_dynamics_from(self, dynamics: RobotDynamicsProvider) -> Self:
        """Returns a new robot arm that uses the dynamics model from the given provider.

        Args:
            dynamics: The provider of the dynamics model for the robot arm.

        Returns:
            A new robot arm that uses the dynamics model from the given provider.

        Note:
            See the [`RobotDynamicsProvider`](exercise_2.md#helpers.robot.RobotDynamicsProvider)
            protocol for more information on how exactly the provider should work.
        """
        return replace(self, dynamics=dynamics)

    def joint_positions(self) -> list[Point]:
        return self.forward_kinematics((self.theta_1, self.theta_2))

    def forward_kinematics(self, q: Sequence[float] | Vector) -> list[Point]:
        assert len(q) == 2, f"Expected 2 joint angles. Got: {len(q)}"

        theta_1, theta_2 = q

        x_0, y_0 = 0, 0
        x_1, y_1 = (
            x_0 + self.l_1 * np.cos(theta_1),
            y_0 + self.l_1 * np.sin(theta_1),
        )
        x, y = (
            x_1 + self.l_2 * np.cos(theta_1 + theta_2),
            y_1 + self.l_2 * np.sin(theta_1 + theta_2),
        )

        return [Point(x_0, y_0), Point(x_1, y_1), Point(x, y)]

    def dynamics_for(self, tau: ControlSignal) -> RobotDynamics:
        return self.dynamics.create_for(self, torque=tau)

    def results_from(
        self,
        *,
        t_range: tuple[float, float],
        recorded_points: int,
        t: Vector,
        tau: list[Vector],
        solution: Matrix,
    ) -> "SimulationResults[PlanarRobotArm]":
        return self.dynamics.results_for(
            self,
            t_range=t_range,
            recorded_points=recorded_points,
            t=t,
            tau=tau,
            solution=solution,
        )

    def initial_conditions(
        self, initial_velocities: Sequence[float] | None = None
    ) -> Vector:
        initial_velocities = initial_velocities or [0, 0]

        assert (
            len(initial_velocities) == 2
        ), f"The robot has 2 joints, so 2 initial velocities must be provided. Got: {len(initial_velocities)}"

        q = np.array([self.theta_1, self.theta_2])
        q_dot = np.array(initial_velocities)

        return np.concatenate([q, q_dot])

    @property
    def l_1(self) -> float:
        return self.link_1.length

    @property
    def l_2(self) -> float:
        return self.link_2.length

    @property
    def theta_1(self) -> float:
        return self.joint_1.theta

    @theta_1.setter
    def theta_1(self, value: float) -> None:
        self.joint_1 = self.joint_1.with_angle(value)

    @property
    def theta_2(self) -> float:
        return self.joint_2.theta

    @theta_2.setter
    def theta_2(self, value: float) -> None:
        self.joint_2 = self.joint_2.with_angle(value)
