from dataclasses import dataclass, KW_ONLY, replace


@dataclass(frozen=True)
class Joint:
    """A joint in a robot arm.

    A joint connects two links and allows them to rotate relative to each other. The joint is
    assumed to be massless, but it can have a certain friction that resists the movement of the
    links.

    Attributes:
        theta: The angle of the joint.
        friction: The friction of the joint.

    Example:
        When creating a [`PlanarRobotArm`](exercise_3.md#helpers.robot.PlanarRobotArm), you can define
        the joints of the robot arm as follows:

        ```python
        robot = PlanarRobotArm(
            joint_1=Joint(theta=0.0, friction=0.1),
            joint_2=Joint(theta=pi / 2, friction=0.2),
            ... # Other parameters
        )

        # This will create a planar robot arm with two joints.
        ```
    """

    _: KW_ONLY
    theta: float
    friction: float = 0.01

    def __post_init__(self) -> None:
        assert 0 <= self.friction, (
            f"The friction of the joint must be greater than or equal to zero. "
            f"Got {self.friction}."
        )

    def with_angle(self, theta: float) -> "Joint":
        """Returns a new joint with the given angle.

        Args:
            theta: The angle of the joint.

        Returns:
            A new joint with the given angle.
        """
        return replace(self, theta=theta)
