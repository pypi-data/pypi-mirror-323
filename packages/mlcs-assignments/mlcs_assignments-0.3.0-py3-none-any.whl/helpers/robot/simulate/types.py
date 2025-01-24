from typing import Protocol, runtime_checkable, Sequence
from helpers.maths import Matrix, Vector


class State(Protocol):
    def __call__(self, t: float) -> Vector:
        """Returns the configuration of the robot arm joints at the given time point."""
        ...

    def dot(self, t: float) -> Vector:
        """Returns the velocities of the robot arm joints at the given time point."""
        ...


class Position(Protocol):
    def __call__(self, q: State) -> Vector:
        """Returns the position of the robot arm at the given configuration."""
        ...


class Jacobian(Protocol):
    def __call__(self, q: State) -> Matrix:
        """Returns the Jacobian matrix of the robot arm at the given configuration."""
        ...


class Gravity(Protocol):
    def __call__(self, q: State) -> Vector:
        """Returns the gravity vector of the robot arm at the given configuration."""
        ...


class ControlSignal(Protocol):
    def __call__(
        self, *, q: State, p: Position, J: Jacobian, g: Gravity, t: float
    ) -> Vector:
        """Returns the control signal for the robot arm at the given time point.

        Args:
            q: The state of the robot arm joints, including the configuration and velocities.
            p: The position of the robot arm.
            J: The Jacobian matrix of the robot arm.
            g: The gravity force acting on the robot arm.
            t: The current time point.

        Returns:
            The control signal for the robot arm for the given time point.

        Note:
            The gravity force `g` would only be available if a realistic model of the robot arm is
            used. This would require the parameters of the robot arm to also be known.
        """
        ...


@runtime_checkable
class StatefulControlSignal(ControlSignal, Protocol):
    def reset(self) -> None:
        """Resets the state of the controller. This will always be called before a simulation
        starts."""
        ...


class DynamicsSolver(Protocol):
    def __call__(
        self,
        dynamics: "RobotDynamics",
        *,
        initial_conditions: Sequence[float] | Vector,
        t_range: tuple[float, float],
        t_evaluation: Vector,
    ) -> Matrix:
        """Solves the robot dynamics over the given time span. In the end, the solver should return the
        states of the system at the specified evaluation time points.

        Args:
            dynamics: The robot dynamics to solve.
            initial_conditions: The initial state of the robot arm.
            t_range: The time span over which to solve the dynamics.
            t_evaluation: The time points at which to evaluate the states of the system.

        Returns:
            The states of the system at the specified evaluation time points. The result is a matrix
            where each row corresponds to a particular state variable and each column corresponds to
            the entire state of the system at a particular time point.
        """
        ...


class DynamicsJacobian(Protocol):
    def __call__(self, t: float, state: Vector) -> Matrix:
        """The Jacobian matrix of the right-hand side of the robot dynamics.

        Args:
            t: The current time point.
            state: The current state of the robot arm.

        Returns:
            The Jacobian matrix of the right-hand side of the robot dynamics. This matrix must be
            $n \\times n$, where $n$ is the number of states in the system. Entry $(i, j)$ of the
            matrix must be the partial derivative of the $i$-th element of the right-hand side with
            respect to the $j$-th state variable.
        """
        ...


class RobotDynamics(Protocol):
    def __call__(self, t: float, state: Vector) -> Vector:
        """The dynamics of the robot arm.

        Args:
            t: The current time point.
            state: The current state of the robot arm.

        Returns:
            The derivative of the state vector.

        Note:
            What the state vector contains and looks like depends on the particular implementation of
            the robot arm dynamics, however, it typically includes the joint angles and velocities in
            some form.

            **Important**: Make sure the following implementations are consistent in how they represent
            the state vector:<br>
            - The `__call__` method of the `RobotDynamics` protocol.<br>
            - The `results_from` method of the `SimulatableRobotArm` protocol.<br>
            - The `initial_conditions` property of the `SimulatableRobotArm` protocol
        """
        ...

    def jacobian(self) -> DynamicsJacobian | None:
        """Returns a function that computes the Jacobian of the right-hand side of the robot dynamics.

        See the [`DynamicsJacobian`](exercise_2.md#helpers.robot.simulate.Jacobian) protocol for more
        details on how it should behave. If the Jacobian is not available, this method should return
        `None` and a numerical approximation will automatically be used instead.
        """
        ...

    def solver(self) -> DynamicsSolver | None:
        """Returns the solver for the robot dynamics. If the default solver should be used, this method
        should simply return `None`.
        """
        ...
