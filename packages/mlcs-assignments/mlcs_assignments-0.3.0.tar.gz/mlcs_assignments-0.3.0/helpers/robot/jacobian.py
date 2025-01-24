from typing import Sequence

from helpers.maths import Matrix, Vector
from helpers.robot.arm import RobotArm

import numpy as np


class RobotJacobianMixin:
    def jacobian(self: RobotArm, q: Sequence[float] | Vector) -> Matrix:
        """Returns the Jacobian matrix of the robot arm at the given configuration.

        Args:
            q: The configuration of the robot arm joints.

        Returns:
            The Jacobian matrix of the robot arm. The matrix is of shape (2, 2).
        
        Note:
            The Jacobian matrix maps the joint velocities to the end effector velocities. We assume
            that the robot has two revolute joints and the forward kinematics are given by:

            $$
            x = l_1 cos(\\theta_1) + l_2 cos(\\theta_1 + \\theta_2) \\
            y = l_1 sin(\\theta_1) + l_2 sin(\\theta_1 + \\theta_2)
            $$
            
            The Jacobian matrix is then given by:

            $$
            J = \\begin{bmatrix}
            -l_1 sin(\\theta_1) - l_2 sin(\\theta_1 + \\theta_2) & -l_2 sin(\\theta_1 + \\theta_2) \\
            l_1 cos(\\theta_1) + l_2 cos(\\theta_1 + \\theta_2) & l_2 cos(\\theta_1 + \\theta_2)
            \\end{bmatrix}
            $$
        """

        assert (
            len(q) == 2
        ), f"The configuration must contain exactly two joint angles. Got: {len(q)}"

        q_1, q_2 = q
        return np.array(
            [
                [
                    -self.l_1 * np.sin(q_1) - self.l_2 * np.sin(q_1 + q_2),
                    -self.l_2 * np.sin(q_1 + q_2),
                ],
                [
                    self.l_1 * np.cos(q_1) + self.l_2 * np.cos(q_1 + q_2),
                    self.l_2 * np.cos(q_1 + q_2),
                ],
            ]
        )
