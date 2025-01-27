"""Helper functions for random_shapes module."""

import numpy as np


def ccw_sort(p: np.ndarray) -> np.ndarray:
    """Sort points in counter-clockwise order.

    Args:
        p (np.ndarray): An array of points of shape (n, 2).

    Returns:
        np.ndarray: An array of points sorted in counter-clockwise order of shape (n, 2).

    """
    d = p - np.mean(p, axis=0)
    s = np.arctan2(d[:, 0], d[:, 1])
    return p[np.argsort(s), :]
