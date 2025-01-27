"""Image functions for shapes."""

import bezier
import cv2
import numpy as np


def bezier_polygon_to_binary_image(shape: bezier.CurvedPolygon, w: int, h: int, pts_per_edge: int = 100) -> np.ndarray:
    """Convert a bezier shape to a binary image.

    Args:
        shape (bezier.CurvedPolygon): A bezier shape.
        w (int): Width of the image.
        h (int): Height of the image.
        pts_per_edge (int, optional): Number of points per edge. Defaults to 100.

    Returns:
        np.ndarray: A binary image of the shape.

    """
    img = np.zeros((h, w), dtype=np.uint8)

    # Get all points of the shape at given resolution
    points = np.zeros((shape.num_sides * pts_per_edge, 2))
    for i, curve in enumerate(shape._edges):
        points[i * pts_per_edge : (i + 1) * pts_per_edge] = curve.evaluate_multi(np.linspace(0, 1, pts_per_edge)).T

    # Scale points to image size
    points -= points.min(axis=0)
    points /= points.max(axis=0)
    points *= [w, h]

    # Fill polygon
    points = np.round(points).astype(int)
    cv2.fillPoly(img, [points], 255)

    return img
