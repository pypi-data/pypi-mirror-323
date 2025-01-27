"""Type definitions for random_shapes module."""

from dataclasses import dataclass

import numpy as np


@dataclass
class Point:
    """A point in 2D space."""

    x: float
    y: float


@dataclass
class Node:
    """A node point in 2D space."""

    point: Point
    angle: float


def points_to_numpy(points: list[Point]) -> np.ndarray:
    """Convert a list of points to a numpy array.

    Args:
        points (list[Point]): A list of points.

    Returns:
        np.ndarray: A numpy array of shape (n, 2).

    """
    return np.array([[point.x, point.y] for point in points])


def points_from_numpy(points: np.ndarray) -> list[Point]:
    """Convert a numpy array to a list of points.

    Args:
        points (np.ndarray): A numpy array of shape (n, 2).

    Returns:
        list[Point]: A list of points.

    """
    return [Point(x, y) for x, y in points]
