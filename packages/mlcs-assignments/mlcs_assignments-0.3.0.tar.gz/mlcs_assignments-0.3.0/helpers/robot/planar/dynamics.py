from typing import Protocol, Sequence, TypeVar, Generic, Callable, cast
from dataclasses import dataclass, field, KW_ONLY
from functools import cached_property
from helpers.maths import Matrix, Vector, Point
from helpers.robot.link import Link
from helpers.robot.joint import Joint
from helpers.robot.simulate import (
    SimulatableRobotArm,
    SimulationResults,
    ControlSignal,
    State,
    PrecomputedState,
    LazyPosition,
    LazyJacobian,
    PrecomputedGravity,
)

import numpy as np
from scipy.optimize import approx_fprime

PlanarRobotArmT = TypeVar("PlanarRobotArmT", bound="PlanarRobotArm")
SimulatableRobotT = TypeVar("SimulatableRobotT", bound="SimulatableRobotArm")


class PlanarRobotArm(SimulatableRobotArm, Protocol):
    def forward_kinematics(self, q: Sequence[float] | Vector) -> list[Point]:
        """Calculates the forward kinematics of the robot arm for the given joint angles."""
        ...

    def jacobian(self, q: Sequence[float] | Vector) -> Matrix:
        """Returns the Jacobian matrix of the robot arm at the given configuration."""
        ...

    @property
    def link_1(self) -> Link:
        """The first link of the robot arm."""
        ...

    @property
    def link_2(self) -> Link:
        """The second link of the robot arm."""
        ...

    @property
    def joint_1(self) -> Joint:
        """The first joint of the robot arm."""
        ...

    @property
    def joint_2(self) -> Joint:
        """The second joint of the robot arm."""
        ...


@dataclass(frozen=True)
class DynamicsContext:
    """This class contains all precomputed values that are needed to calculate the dynamics of the
    planar robot arm.

    Attributes:
        c_1: $cos(q_1)$
        c_1_2: $cos(q_1 + q_2)$
        c_2: $cos(q_2)$
        s_2: $sin(q_2)$
        q_dot_1: $\\dot{q}_1$
        q_dot_2: $\\dot{q}_2$
        m_1: The mass of the first link.
        m_2: The mass of the second link.
        l_1: The length of the first link.
        l_2: The length of the second link.
        l_c1: The distance from the base of the first link to its center of mass.
        l_c2: The distance from the base of the second link to its center of mass.
        mu_1: The friction of the first joint.
        mu_2: The friction of the second joint.
        I_c1: The moment of inertia of the first link.
        I_c2: The moment of inertia of the second link.
        g: The acceleration due to gravity.

    Note:
        $q_1$ and $q_2$ are the first and second joint angles of the robot arm, respectively.
    """

    _: KW_ONLY
    c_1: float
    c_1_2: float
    c_2: float
    s_2: float
    q_dot_1: float
    q_dot_2: float
    m_1: float
    m_2: float
    l_1: float
    l_2: float
    l_c1: float
    l_c2: float
    mu_1: float
    mu_2: float
    I_c1: float
    I_c2: float
    g: float


@dataclass(frozen=True)
class DynamicsJacobianContext:
    """This class contains all precomputed values that are needed to calculate the Jacobian matrix of
    the right-hand side of the dynamics equation of the planar robot arm.

    Attributes:
        alpha: $\\alpha = m_2 * l_1 * l_c2$
        beta: $\\beta = m_2 * g * l_c2$
        c_2: $cos(q_2)$
        s_1: $sin(q_1)$
        s_1_2: $sin(q_1 + q_2)$
        s_2: $sin(q_2)$
        q_dot_1: $\\dot{q}_1$
        q_dot_2: $\\dot{q}_2$
        m_1: The mass of the first link.
        m_2: The mass of the second link.
        l_1: The length of the first link.
        l_c1: The distance from the base of the first link to its center of mass.
        l_c2: The distance from the base of the second link to its center of mass.
        mu_1: The friction of the first joint.
        mu_2: The friction of the second joint.
        g: The acceleration due to gravity.

    Note:
        $q_1$ and $q_2$ are the first and second joint angles of the robot arm, respectively.
    """

    _: KW_ONLY
    alpha: float
    beta: float
    c_2: float
    s_1: float
    s_1_2: float
    s_2: float
    q_dot_1: float
    q_dot_2: float
    m_1: float
    m_2: float
    l_1: float
    l_c1: float
    l_c2: float
    mu_1: float
    mu_2: float
    g: float


@dataclass(frozen=True)
class DynamicsContextProvider:
    _: KW_ONLY
    robot: PlanarRobotArm
    I_c1: float
    I_c2: float
    g: float = 9.81

    @staticmethod
    def create_for(robot: PlanarRobotArm) -> "DynamicsContextProvider":
        m_1, delta_1 = robot.link_1.mass, robot.link_1.com_size
        m_2, delta_2 = robot.link_2.mass, robot.link_2.com_size

        return DynamicsContextProvider(
            robot=robot,
            I_c1=m_1 * delta_1**2,
            I_c2=m_2 * delta_2**2,
        )

    def __call__(self, q: Vector, q_dot: Vector) -> DynamicsContext:
        q_1, q_2 = q
        q_dot_1, q_dot_2 = q_dot

        return DynamicsContext(
            c_1=np.cos(q_1),
            c_1_2=np.cos(q_1 + q_2),
            c_2=np.cos(q_2),
            s_2=np.sin(q_2),
            q_dot_1=q_dot_1,
            q_dot_2=q_dot_2,
            m_1=self.robot.link_1.mass,
            m_2=self.robot.link_2.mass,
            l_1=self.robot.link_1.length,
            l_2=self.robot.link_2.length,
            l_c1=self.robot.link_1.distance_to_com,
            l_c2=self.robot.link_2.distance_to_com,
            mu_1=self.robot.joint_1.friction,
            mu_2=self.robot.joint_2.friction,
            I_c1=self.I_c1,
            I_c2=self.I_c2,
            g=self.g,
        )

    def jacobian(self, q: Vector, q_dot: Vector) -> DynamicsJacobianContext:
        q_1, q_2 = q
        q_dot_1, q_dot_2 = q_dot
        m_2 = self.robot.link_2.mass
        l_1, l_c2 = self.robot.link_1.length, self.robot.link_2.distance_to_com

        return DynamicsJacobianContext(
            alpha=m_2 * l_1 * l_c2,
            beta=m_2 * self.g * l_c2,
            c_2=np.cos(q_2),
            s_1=np.sin(q_1),
            s_1_2=np.sin(q_1 + q_2),
            s_2=np.sin(q_2),
            q_dot_1=q_dot_1,
            q_dot_2=q_dot_2,
            m_1=self.robot.link_1.mass,
            m_2=m_2,
            l_1=l_1,
            l_c1=self.robot.link_1.distance_to_com,
            l_c2=l_c2,
            mu_1=self.robot.joint_1.friction,
            mu_2=self.robot.joint_2.friction,
            g=self.g,
        )


@dataclass
class LazyGravity:
    context: DynamicsContextProvider
    gravity_provider: Callable[[DynamicsContext], Vector]
    t: float
    g: Vector | None = field(default=None, init=False)

    def __call__(self, q: State) -> Vector:
        if self.g is None:
            self.g = self.gravity_provider(self.context(q(self.t), q.dot(self.t)))

        return self.g


# TODO: Document how the Jacobian is calculated.
@dataclass(frozen=True)
class RigidBodyDynamicsJacobian(Generic[PlanarRobotArmT]):
    dynamics: "RigidBodyDynamics[PlanarRobotArmT]"

    def __call__(self, t: float, state: Vector) -> Matrix:
        q, q_dot = state[:2], state[2:]
        J = self.jacobian_matrix(q, q_dot, t)
        return J

    def jacobian_matrix(self, q: Vector, q_dot: Vector, t: float) -> Matrix:
        context = self.dynamics.context(q, q_dot)
        D_inv = self.dynamics.D_inv(context)
        C = self.dynamics.C(context)
        g = self.dynamics.g(context)
        mu = self.dynamics.mu(context)

        jacobian_context = self.dynamics.context.jacobian(q, q_dot)
        J_D_inv = self.J_D_inv(jacobian_context)
        J_C = self.J_C(jacobian_context)
        J_g = self.J_g(jacobian_context)
        J_tau = self.J_tau(q, q_dot, t)
        J_tau_mu = self.J_tau_mu(jacobian_context)
        J_q_dot = self.J_q_dot

        tau = self.dynamics.tau(
            q=PrecomputedState(q=q, q_dot=q_dot),
            p=LazyPosition(robot=self.dynamics.robot, t=t),
            J=LazyJacobian(robot=self.dynamics.robot, t=t),
            g=PrecomputedGravity(g=g),
            t=t,
        )
        tau_mu = -mu @ q_dot

        return np.vstack(
            [
                np.array(
                    [
                        [0, 0, 1, 0],
                        [0, 0, 0, 1],
                    ]
                ),
                np.vstack(
                    [
                        -D_inv @ D_inv_x @ D_inv @ (tau + tau_mu - C @ q_dot - g)
                        + (D_inv @ (tau_x + tau_mu_x - C_x @ q_dot - C @ q_dot_x - g_x))
                        for D_inv_x, C_x, g_x, tau_x, tau_mu_x, q_dot_x in zip(
                            J_D_inv, J_C, J_g, J_tau, J_tau_mu, J_q_dot
                        )
                    ]
                ).T,
            ]
        )

    def J_tau(self, q: Vector, q_dot: Vector, t: float) -> Sequence[Vector]:
        return cast(
            Sequence[Vector],
            approx_fprime(np.concat([q, q_dot]), self.tau_for, 1e-7, t).T.tolist(),
        )

    def J_tau_mu(self, context: DynamicsJacobianContext) -> Sequence[Vector]:
        mu_1, mu_2 = context.mu_1, context.mu_2

        J_tau_mu_1 = J_tau_mu_2 = np.zeros(2)
        J_tau_mu_3 = np.array([-mu_1, 0])
        J_tau_mu_4 = np.array([0, -mu_2])

        return [J_tau_mu_1, J_tau_mu_2, J_tau_mu_3, J_tau_mu_4]

    def J_D_inv(self, context: DynamicsJacobianContext) -> Sequence[Matrix]:
        alpha = context.alpha
        s_2 = context.s_2

        D_x_1 = D_x_3 = D_x_4 = np.zeros((2, 2))
        D_x_2 = alpha * (-s_2) * np.array([[2, 1], [1, 0]])

        return [D_x_1, D_x_2, D_x_3, D_x_4]

    def J_C(self, context: DynamicsJacobianContext) -> Sequence[Matrix]:
        alpha = context.alpha
        c_2 = context.c_2
        s_2 = context.s_2
        q_dot_1, q_dot_2 = context.q_dot_1, context.q_dot_2

        C_x_1 = np.zeros((2, 2))
        C_x_2 = alpha * c_2 * np.array([[-q_dot_2, -(q_dot_1 + q_dot_2)], [q_dot_1, 0]])
        C_x_3 = alpha * s_2 * np.array([[0, -1], [1, 0]])
        C_x_4 = alpha * s_2 * np.array([[-1, -1], [0, 0]])

        return [C_x_1, C_x_2, C_x_3, C_x_4]

    def J_g(self, context: DynamicsJacobianContext) -> Sequence[Vector]:
        beta = context.beta
        s_1, s_1_2 = context.s_1, context.s_1_2
        m_1, m_2 = context.m_1, context.m_2
        l_1 = context.l_1
        l_c1, l_c2 = context.l_c1, context.l_c2
        g = context.g

        g_x_1 = -g * np.array(
            [m_1 * l_c1 * s_1 + m_2 * (l_1 * s_1 + l_c2 * s_1_2), m_2 * l_c2 * s_1_2]
        )
        g_x_2 = -beta * s_1_2 * np.array([1, 1])
        g_x_3 = g_x_4 = np.zeros(2)

        return [g_x_1, g_x_2, g_x_3, g_x_4]

    @cached_property
    def J_q_dot(self) -> Sequence[Vector]:
        q_dot_x_1 = q_dot_x_2 = np.zeros(2)
        q_dot_x_3 = np.array([1, 0])
        q_dot_x_4 = np.array([0, 1])

        return [q_dot_x_1, q_dot_x_2, q_dot_x_3, q_dot_x_4]

    def tau_for(self, x: Vector, t: float, /) -> Vector:
        q, q_dot = x[:2], x[2:]

        return self.dynamics.tau(
            q=PrecomputedState(q=q, q_dot=q_dot),
            p=LazyPosition(robot=self.dynamics.robot, t=t),
            J=LazyJacobian(robot=self.dynamics.robot, t=t),
            g=LazyGravity(
                context=self.dynamics.context, gravity_provider=self.dynamics.g, t=t
            ),
            t=t,
        )


# TODO: Document how the dynamics are calculated.
@dataclass(frozen=True)
class RigidBodyDynamics(Generic[PlanarRobotArmT]):
    tau: ControlSignal
    robot: PlanarRobotArmT
    context: DynamicsContextProvider

    @staticmethod
    def create_for(
        robot: PlanarRobotArmT, *, torque: ControlSignal
    ) -> "RigidBodyDynamics[PlanarRobotArmT]":
        return RigidBodyDynamics(
            tau=torque,
            robot=robot,
            context=DynamicsContextProvider.create_for(robot),
        )

    @staticmethod
    def results_for(
        robot: SimulatableRobotT,
        *,
        t_range: tuple[float, float],
        recorded_points: int,
        t: Vector,
        tau: list[Vector],
        solution: Matrix,
    ) -> SimulationResults[SimulatableRobotT]:
        q = [row % (2 * np.pi) for row in solution[:2]]
        q_dot = [row for row in solution[2:]]
        return SimulationResults.of(
            robot,
            t_range=t_range,
            recorded_points=recorded_points,
            t=t,
            tau=tau,
            q=q,
            q_dot=q_dot,
            final_state=solution[:, -1],
        )

    def __call__(self, t: float, state: Vector) -> Vector:
        q, q_dot = state[:2], state[2:]
        q_dot_dot = self.dynamics(q, q_dot, t)
        return np.concatenate([q_dot, q_dot_dot])

    def dynamics(self, q: Vector, q_dot: Vector, t: float) -> Vector:
        context = self.context(q, q_dot)
        D_inv, C, g, mu = (
            self.D_inv(context),
            self.C(context),
            self.g(context),
            self.mu(context),
        )

        tau = self.tau(
            q=PrecomputedState(q=q, q_dot=q_dot),
            p=LazyPosition(robot=self.robot, t=t),
            J=LazyJacobian(robot=self.robot, t=t),
            g=PrecomputedGravity(g=g),
            t=t,
        )
        tau_mu = -mu @ q_dot

        q_dot_dot = D_inv @ (tau + tau_mu - C @ q_dot - g).flatten()
        return q_dot_dot

    def jacobian(self) -> "RigidBodyDynamicsJacobian[PlanarRobotArmT]":
        return RigidBodyDynamicsJacobian(self)

    def solver(self) -> None:
        # The default solver is just fine.
        return None

    def D_inv(self, context: DynamicsContext) -> Matrix:
        c_2 = context.c_2
        m_1, m_2 = context.m_1, context.m_2
        l_1 = context.l_1
        l_c1, l_c2 = context.l_c1, context.l_c2
        I_c1, I_c2 = context.I_c1, context.I_c2

        d_11 = (
            m_1 * l_c1**2
            + m_2 * (l_1**2 + l_c2**2 + 2 * l_1 * l_c2 * c_2)
            + I_c1
            + I_c2
        )
        d_12 = m_2 * (l_c2**2 + l_1 * l_c2 * c_2) + I_c2
        d_22 = m_2 * l_c2**2 + I_c2
        det_D = d_11 * d_22 - d_12**2

        return (
            np.array(
                [
                    [d_22, -d_12],
                    [-d_12, d_11],
                ]
            )
            / det_D
        )

    def C(self, context: DynamicsContext) -> Matrix:
        q_dot_1, q_dot_2 = context.q_dot_1, context.q_dot_2
        s_2 = context.s_2
        m_2 = context.m_2
        l_1 = context.l_1
        l_c2 = context.l_c2

        return np.array(
            [
                [
                    -m_2 * l_1 * l_c2 * s_2 * q_dot_2,
                    (-m_2 * l_1 * l_c2 * s_2 * (q_dot_1 + q_dot_2)),
                ],
                [m_2 * l_1 * l_c2 * s_2 * q_dot_1, 0],
            ]
        )

    def g(self, context: DynamicsContext) -> Vector:
        c_1 = context.c_1
        c_1_2 = context.c_1_2
        m_1, m_2 = context.m_1, context.m_2
        l_1 = context.l_1
        l_c1, l_c2 = context.l_c1, context.l_c2
        g = context.g

        return np.array(
            [
                m_1 * g * l_c1 * c_1 + m_2 * g * (l_1 * c_1 + l_c2 * c_1_2),
                m_2 * g * l_c2 * c_1_2,
            ]
        )

    def mu(self, context: DynamicsContext) -> Matrix:
        mu_1, mu_2 = context.mu_1, context.mu_2

        return np.array([[mu_1, 0], [0, mu_2]])
