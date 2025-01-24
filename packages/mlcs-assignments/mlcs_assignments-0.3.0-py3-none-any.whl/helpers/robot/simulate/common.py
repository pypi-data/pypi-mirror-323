from typing import Protocol, Sequence
from dataclasses import dataclass, field, KW_ONLY

from helpers.maths import Matrix, Vector, Point
from helpers.robot.simulate.simulate import (
    State,
)


class RobotKinematics(Protocol):
    def forward_kinematics(self, q: Vector) -> Sequence[Point]:
        """Computes the forward kinematics of the robot for the given configuration."""
        ...

    def jacobian(self, q: Vector) -> Matrix:
        """Computes the Jacobian of the robot for the given configuration."""
        ...


@dataclass(frozen=True)
class PrecomputedState:
    _: KW_ONLY
    q: Vector
    q_dot: Vector

    def __call__(self, t: float) -> Vector:
        return self.q

    def dot(self, t: float) -> Vector:
        return self.q_dot


@dataclass
class LazyPosition:
    robot: RobotKinematics
    t: float
    p: Vector | None = field(default=None, init=False)

    def __call__(self, q: State) -> Vector:
        if self.p is None:
            self.p = self.robot.forward_kinematics(q(self.t))[-1].vector()

        return self.p


@dataclass
class LazyJacobian:
    robot: RobotKinematics
    t: float
    J: Matrix | None = field(default=None, init=False)

    def __call__(self, q: State) -> Matrix:
        if self.J is None:
            self.J = self.robot.jacobian(q(self.t))

        return self.J


@dataclass(frozen=True)
class PrecomputedGravity:
    _: KW_ONLY
    g: Vector

    def __call__(self, q: State) -> Vector:
        return self.g


class UnknownGravity:
    def __call__(self, q: State) -> Vector:
        raise ValueError("Gravity vector is unknown.")
