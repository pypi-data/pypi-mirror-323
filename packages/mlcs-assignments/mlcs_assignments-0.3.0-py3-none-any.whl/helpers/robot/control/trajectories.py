import numpy as np
from helpers.maths import Vector
from helpers.robot.control.control import Trajectory


def square(
    t_range: tuple[float, float],
    *,
    side_length: float = 1.0,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range
    x_0, y_0 = offset

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 4.0
        segment = int(normalized_t)
        remainder = normalized_t - segment

        match segment:
            case 0:
                return np.array([x_0 + remainder * side_length, y_0])
            case 1:
                return np.array([x_0 + side_length, y_0 + remainder * side_length])
            case 2:
                return np.array(
                    [x_0 + side_length - remainder * side_length, y_0 + side_length]
                )
            case 3:
                return np.array([x_0, y_0 + side_length - remainder * side_length])
            case _:
                return np.array([x_0, y_0])

    return trajectory


def circle(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0)
        angle = normalized_t * 2 * np.pi

        return radius * np.array([np.cos(angle), np.sin(angle)]) + offset + radius

    return trajectory


def figure_eight(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 2.0 * np.pi
        x = radius * np.sin(normalized_t)
        y = radius * np.sin(2 * normalized_t)

        return np.array([x, y]) + offset + radius

    return trajectory


def spiral(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 2.0 * np.pi
        x = radius * np.sin(normalized_t) * normalized_t
        y = radius * np.cos(normalized_t) * normalized_t

        return np.array([x, y]) + offset + radius

    return trajectory


def heart(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 2.0 * np.pi
        x = radius * np.sin(normalized_t) * np.sqrt(np.abs(np.cos(normalized_t)))
        y = radius * np.cos(normalized_t) * np.sqrt(np.abs(np.cos(normalized_t)))

        return np.array([x, y]) + offset + radius

    return trajectory


def infinity(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 2.0 * np.pi
        x = radius * np.sin(normalized_t)
        y = radius * np.sin(normalized_t) * np.cos(normalized_t)

        return np.array([x, y]) + offset + radius

    return trajectory


def lemniscate(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 2.0 * np.pi
        x = radius * np.sin(normalized_t)
        y = radius * np.sin(2 * normalized_t)

        return np.array([x, y]) + offset + radius

    return trajectory


def clover(
    t_range: tuple[float, float],
    *,
    radius: float = 0.5,
    offset: Vector = np.array([0.0, 0.5]),
) -> Trajectory:
    t_0, t_f = t_range

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / (t_f - t_0) * 2.0 * np.pi
        x = radius * np.cos(normalized_t) * np.cos(2 * normalized_t)
        y = radius * np.sin(normalized_t) * np.cos(2 * normalized_t)

        return np.array([x, y]) + offset + radius

    return trajectory


def line(
    t_range: tuple[float, float],
    *,
    start: tuple[float, float],
    end: tuple[float, float],
) -> Trajectory:
    t_0, t_f = t_range
    delta_t = t_f - t_0
    x_0, y_0 = start
    x_f, y_f = end

    def trajectory(t: float) -> Vector:
        normalized_t = (t - t_0) / delta_t
        x = x_0 + normalized_t * (x_f - x_0)
        y = y_0 + normalized_t * (y_f - y_0)

        return np.array([x, y])

    return trajectory
