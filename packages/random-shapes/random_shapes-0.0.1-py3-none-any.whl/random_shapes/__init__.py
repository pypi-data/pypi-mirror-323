"""Random shape generator."""

from importlib.metadata import version

from random_shapes.helper import ccw_sort as ccw_sort
from random_shapes.image import bezier_polygon_to_binary_image as bezier_polygon_to_binary_image
from random_shapes.rnd import get_random_points as get_random_points
from random_shapes.rnd import get_random_shape as get_random_shape
from random_shapes.shape import calculate_segment as calculate_segment
from random_shapes.shape import points_to_nodes as points_to_nodes
from random_shapes.types import Node as Node
from random_shapes.types import Point as Point
from random_shapes.types import points_from_numpy as points_from_numpy
from random_shapes.types import points_to_numpy as points_to_numpy

__version__ = version("random_shapes")
