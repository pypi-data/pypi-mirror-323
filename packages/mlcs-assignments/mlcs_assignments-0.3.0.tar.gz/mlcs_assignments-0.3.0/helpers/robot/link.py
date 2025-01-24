from dataclasses import dataclass, KW_ONLY


@dataclass(frozen=True)
class Link:
    """A link in a robot arm.

    The link is assumed to be a rigid body with a center of mass somewhere along its length. The
    center of mass is assumed to be a cube with a side length of `com_size`. The remaining part of
    the link is assumed to be a thin rod (i.e. massless).

    Attributes:
        mass: The mass of the link.
        length: The length of the link.
        distance_to_com: The distance from the base of the link to its center of mass.
        com_size: The size of the center of mass (defaults to 0.1).

    Example:
        When creating a [`PlanarRobotArm`](exercise_3.md#helpers.robot.PlanarRobotArm), you can define
        the links of the robot arm as follows:

        ```python
        robot = PlanarRobotArm(
            link_1=Link(mass=1.0, length=1.0, distance_to_com=0.75),
            link_2=Link(mass=2.0, length=0.75, distance_to_com=0.5),
            ... # Other parameters
        )

        # This will create a planar robot arm with two links.
        ```
    """

    _: KW_ONLY
    mass: float
    length: float
    distance_to_com: float
    com_size: float = 0.1

    def __post_init__(self) -> None:
        assert (
            self.mass > 0
        ), f"The mass of the link must be greater than zero. Got {self.mass}."
        assert (
            self.length > 0
        ), f"The length of the link must be greater than zero. Got {self.length}."
        assert 0 <= self.distance_to_com <= self.length, (
            f"The center of mass must be located within the link, "
            f"i.e. the value must be between 0 and {self.length}. Got {self.distance_to_com}."
        )
        assert (
            self.com_size > 0
        ), f"The size of the center of mass must be greater than zero. Got {self.com_size}."
