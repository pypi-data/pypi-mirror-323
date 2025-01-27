"""A module for creating bezier-based shapes.

Code mostly inspired by: https://stackoverflow.com/a/50751932/12031297
"""

from typing import Self

import bezier
import cv2
import numpy as np

from random_shapes.helper import ccw_sort
from random_shapes.points import Node, Point, points_from_numpy, points_to_numpy


def get_random_points(n: int = 5, scale: float = 0.8, mindst: float | None = None, rec: int = 0) -> list[Point]:
    """Create n random points in the unit square, which are *mindst* apart, then scale them.

    Args:
        n (int, optional): Number of points. Defaults to 5.
        scale (float, optional): Scaling factor. Defaults to 0.8.
        mindst (float, optional): Minimum distance between points. Defaults to None.
        rec (int, optional): Recursion counter. Defaults to 0.

    Returns:
        list[Point]: A list of points of length n.

    """
    mindst = mindst or 0.7 / n
    gen = np.random.default_rng()
    a = gen.random((n, 2))
    d = np.sqrt(np.sum(np.diff(ccw_sort(a), axis=0), axis=1) ** 2)
    if np.all(d >= mindst) or rec >= 200:
        return points_from_numpy(a * scale)
    else:
        return get_random_points(n=n, scale=scale, mindst=mindst, rec=rec + 1)


def estimate_angles(points: list[Point] | np.ndarray, edgy: float) -> list[Node]:
    """Convert a list of points to a list of nodes by calculating angles between them.

    Args:
        points (list[Point]): A list of points.
        edgy (float, optional): A number between 0 and 1 to steer the weiredness of angles.

    Returns:
        list[Node]: A list of nodes, aranged in counter-clockwise order on a closed loop.
            Hence, the last node is equal to the first node.

    """
    if isinstance(points, list):
        points = points_to_numpy(points)
    p = np.arctan(edgy) / np.pi + 0.5
    points = ccw_sort(points)

    # Add the starting point to the end, to create a closed loop
    points = np.append(points, [points[0]], axis=0)

    # Calculate angles
    d = np.diff(points, axis=0)
    ang = np.arctan2(d[:, 1], d[:, 0])
    ang = (ang >= 0) * ang + (ang < 0) * (ang + 2 * np.pi)
    rolled_ang = np.roll(ang, 1)
    ang = p * ang + (1 - p) * rolled_ang + (np.abs(rolled_ang - ang) > np.pi) * np.pi
    ang = np.append(ang, [ang[0]])

    # Create nodes
    nodes = [Node(Point(x, y), a) for (x, y), a in zip(points, ang)]
    return nodes


def calculate_segment(p1: Point, p2: Point, angle1: float, angle2: float, r: float) -> bezier.Curve:
    """Calculate a bezier segment between two points and their angles.

    This function does this by creating two control points for each point.

    Args:
        p1 (Point): First point.
        p2 (Point): Second point.
        angle1 (float): First angle.
        angle2 (float): Second angle.
        r (float, optional): A number between 0 and 1 to steer the roundness of control points.

    Returns:
        bezier.Curve: A bezier curve segment.

    """
    d = np.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
    r = r * d
    p = np.zeros((4, 2))
    p[0, :] = [p1.x, p1.y]
    p[3, :] = [p2.x, p2.y]
    p[1, :] = [p1.x + r * np.cos(angle1), p1.y + r * np.sin(angle1)]
    p[2, :] = [p2.x + r * np.cos(angle2 + np.pi), p2.y + r * np.sin(angle2 + np.pi)]
    nodes = np.asfortranarray(p.T)
    return bezier.Curve(nodes, degree=3)


class Shape:
    """A wrapper class of bezier.CurvedPolygon for creating random bezier shapes and convertion to other formats."""

    def __init__(self, curve: bezier.CurvedPolygon):
        """Create a new shape.

        Args:
            curve (bezier.CurvedPolygon): A bezier shape.

        """
        self.curve = curve

    @classmethod
    def from_points(cls: type[Self], points: list[Point], edgy: float, r: float) -> Self:
        """Get a bezier shape from a list of points.

        Args:
            points (list[Point]): A list of points.
            edgy (float, optional): A number between 0 and 1 to steer the edgyness / weiredness of the shape.
            r (float, optional): A number between 0 and 1 to steer the roundness of the shape-edges.

        """
        nodes = estimate_angles(points, edgy=edgy)

        segments = []
        for i in range(len(nodes) - 1):
            segment = calculate_segment(nodes[i].point, nodes[i + 1].point, nodes[i].angle, nodes[i + 1].angle, r=r)
            segments.append(segment)

        curve = bezier.CurvedPolygon(*segments)
        return cls(curve)

    @classmethod
    def random(
        cls: type[Self],
        n: int = 5,
        r: float = 0.3,
        edgy: float = 0,
        scale: float = 0.8,
        mindst: float | None = None,
        rec: int = 0,
    ) -> Self:
        """Create a random shape.

        Args:
            n (int, optional): Number of points. Defaults to 5.
            edgy (float, optional): Steers the edgyness / weiredness of the shape. Defaults to 0.
            r (float, optional): Steers the roundness of the shape-edges. Defaults to 0.3.
            scale (float, optional): Scaling factor. Defaults to 0.8.
            mindst (float, optional): Minimum distance between points. Defaults to None.
            rec (int, optional): Recursion counter for the random generation of points. Defaults to 0.

        Returns:
            bezier.CurvedPolygon: A random shape.

        """
        points = get_random_points(n=n, scale=scale, mindst=mindst, rec=rec)
        return cls.from_points(points, edgy=edgy, r=r)

    def rasterize(self, w: int, h: int, pts_per_edge: int = 20) -> np.ndarray:
        """Convert a bezier shape to a binary image.

        Args:
            shape (bezier.CurvedPolygon): A bezier shape.
            w (int): Width of the image.
            h (int): Height of the image.
            pts_per_edge (int, optional): Number of points per edge. Defaults to 20.

        Returns:
            np.ndarray: A binary image of the shape.

        """
        img = np.zeros((h, w), dtype=np.uint8)

        # Get all points of the shape at given resolution
        points = np.zeros((self.curve.num_sides * pts_per_edge, 2))
        for i, curve in enumerate(self.curve._edges):
            points[i * pts_per_edge : (i + 1) * pts_per_edge] = curve.evaluate_multi(np.linspace(0, 1, pts_per_edge)).T

        # Scale points to image size
        points -= points.min(axis=0)
        points /= points.max(axis=0)
        points *= [w, h]

        # Fill polygon
        points = np.round(points).astype(int)
        cv2.fillPoly(img, [points], 255)  # type: ignore

        return img
