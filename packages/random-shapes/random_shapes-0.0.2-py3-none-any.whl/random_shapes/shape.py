"""A module for creating bezier-based shapes.

Code mostly inspired by: https://stackoverflow.com/a/50751932/12031297
"""

import bezier
import numpy as np

from random_shapes.helper import ccw_sort
from random_shapes.types import Node, Point, points_to_numpy


def points_to_nodes(points: list[Point], edgy: float) -> list[Node]:
    """Convert a list of points to a list of nodes.

    Args:
        points (list[Point]): A list of points.
        edgy (float, optional): A number between 0 and 1 to steer the weiredness of angles.

    Returns:
        list[Node]: A list of nodes, aranged in counter-clockwise order on a closed loop.
            Hence, the last node is equal to the first node.

    """
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
    """Calculate a bezier segment between two points.

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


def get_shape_from_points(points: list[Point], edgy: float, r: float) -> bezier.CurvedPolygon:
    """Get a bezier shape from a list of points.

    Args:
        points (list[Point]): A list of points.
        edgy (float, optional): A number between 0 and 1 to steer the edgyness / weiredness of the shape.
        r (float, optional): A number between 0 and 1 to steer the roundness of the shape-edges.

    """
    nodes = points_to_nodes(points, edgy=edgy)

    segments = []
    for i in range(len(nodes) - 1):
        segment = calculate_segment(nodes[i].point, nodes[i + 1].point, nodes[i].angle, nodes[i + 1].angle, r=r)
        segments.append(segment)

    return bezier.CurvedPolygon(*segments)
