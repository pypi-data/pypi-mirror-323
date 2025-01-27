"""Random generator of points."""

import bezier
import numpy as np

from random_shapes.helper import ccw_sort
from random_shapes.shape import get_shape_from_points
from random_shapes.types import Point, points_from_numpy


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


def get_random_shape(
    n: int = 5,
    r: float = 0.3,
    edgy: float = 0,
    scale: float = 0.8,
    mindst: float | None = None,
    rec: int = 0,
) -> bezier.CurvedPolygon:
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
    return get_shape_from_points(points, edgy=edgy, r=r)
