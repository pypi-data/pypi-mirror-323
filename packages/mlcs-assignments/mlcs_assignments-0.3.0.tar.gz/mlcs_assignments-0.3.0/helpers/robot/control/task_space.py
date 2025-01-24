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


def task_space_distance(*, q: State, p: Position, t: float, target: Vector) -> float:
    return float(norm(p(q) - target))


# TODO: Untested!
@dataclass(frozen=True)
class PD:
    _: KW_ONLY
    K_x_p: float
    K_x_d: float
    gravity_compensation: bool

    @staticmethod
    def with_parameters(
        *, w_n: float, xi: float, M_x: float, gravity_compensation: bool = False
    ) -> "PD":
        assert w_n > 0, f"The natural frequency must be greater than zero. Got {w_n}."
        assert 0 < xi <= 1, f"The damping ratio must be between 0 and 1. Got {xi}."
        assert (
            M_x > 0
        ), f"The guess for the inertia of the system must be greater than zero. Got {M_x}."

        return PD(
            K_x_p=w_n**2 * M_x,
            K_x_d=2 * xi * w_n * M_x,
            gravity_compensation=gravity_compensation,
        )

    def setpoint(self, p_d: Vector) -> ControlSignal:
        if self.gravity_compensation:
            return lambda q, p, J, g, t: -J(q).T @ (
                self.K_x_p * (p(q) - p_d) + self.K_x_d * J(q) @ q.dot(t) + g(q)
            )
        else:
            return lambda q, p, J, g, t: -J(q).T @ (
                self.K_x_p * (p(q) - p_d) + self.K_x_d * J(q) @ q.dot(t)
            )

    def setpoints(
        self, p_d: Sequence[Vector], *, threshold: float = 0.1
    ) -> ControlSignal:
        return SetpointFollower(
            setpoints=p_d,
            control_provider=self.setpoint,
            distance=task_space_distance,
            threshold=threshold,
        )

    def trajectory(self, p_d: Trajectory) -> ControlSignal:
        return TrajectoryFollower(trajectory=p_d, control_provider=self.setpoint)
