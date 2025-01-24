from typing import Sequence
from dataclasses import dataclass, KW_ONLY
from helpers.maths import Vector
from helpers.robot.control.control import (
    SetpointFollower,
    TrajectoryFollower,
    Trajectory,
)
from helpers.robot.simulate import (
    ControlSignal,
    State,
    Position,
)

from numpy.linalg import norm
import numpy as np


def joint_space_distance(*, q: State, p: Position, t: float, target: Vector) -> float:
    return float(norm(q(t) - target))


# TODO: Untested!
@dataclass(frozen=True)
class PD:
    _: KW_ONLY
    K_x_p: float
    K_x_d: float

    @staticmethod
    def with_parameters(*, w_n: float, xi: float, M_x: float) -> "PD":
        assert w_n > 0, f"The natural frequency must be greater than zero. Got {w_n}."
        assert 0 < xi <= 1, f"The damping ratio must be between 0 and 1. Got {xi}."
        assert (
            M_x > 0
        ), f"The guess for the inertia of the system must be greater than zero. Got {M_x}."

        return PD(
            K_x_p=w_n**2 * M_x,
            K_x_d=2 * xi * w_n * M_x,
        )

    def setpoint(self, q_d: Vector) -> ControlSignal:
        return lambda q, p, J, g, t: -self.K_x_p * (
            self.wrap(q(t) - q_d)
        ) - self.K_x_d * q.dot(t)

    def setpoints(
        self, q_d: Sequence[Vector], *, threshold: float = 0.05
    ) -> ControlSignal:
        return SetpointFollower(
            setpoints=q_d,
            control_provider=self.setpoint,
            distance=joint_space_distance,
            threshold=threshold,
        )

    def wrap(self, q: Vector) -> Vector:
        return (q + np.pi) % (2 * np.pi) - np.pi

    def trajectory(self, q_d: Trajectory) -> ControlSignal:
        return TrajectoryFollower(trajectory=q_d, control_provider=self.setpoint)
