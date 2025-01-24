from typing import Sequence

from helpers.maths import Vector, Matrix
from helpers.robot.simulate.types import (
    RobotDynamics,
)

from scipy.integrate import solve_ivp

import numpy as np


class LsodaSolver:
    def __call__(
        self,
        dynamics: RobotDynamics,
        *,
        initial_conditions: Sequence[float] | Vector,
        t_range: tuple[float, float],
        t_evaluation: Vector,
    ) -> Matrix:
        return solve_ivp(
            fun=dynamics,
            jac=dynamics.jacobian(),
            y0=initial_conditions,
            t_span=t_range,
            t_eval=t_evaluation,
            method="LSODA",
        ).y


class EulerSolver:
    def __call__(
        self,
        dynamics: RobotDynamics,
        *,
        initial_conditions: Sequence[float] | Vector,
        t_range: tuple[float, float],
        t_evaluation: Vector,
    ) -> Matrix:
        states = []
        last_state = np.array(initial_conditions)
        last_t = t_range[0]

        for t in t_evaluation:
            delta_t = t - last_t
            derivative = dynamics(last_t, last_state)
            last_state = last_state + delta_t * derivative

            states.append(last_state)

        return np.array(states).T
