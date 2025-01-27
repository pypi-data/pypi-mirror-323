.. random-shapes documentation master file, created by
   sphinx-quickstart on Sat Jan 25 13:36:18 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#########################################
Welcome to random-shapes's documentation!
#########################################

**Version**: |version|

Generate random shapes with ease.

.. toctree::
   :maxdepth: 1

   Reference <reference/index>
   Examples <auto_examples/index>

Quick Start
===========

Installation
------------

You can install random-shapes via pip:

.. code-block:: bash

    pip install random-shapes

However, `uv` is recommended for installing python packages:

.. code-block:: bash

    uv add random-shapes

Usage
-----

Install the optional library `matplotlib` for visualization:

.. code-block:: bash

    uv add matplotlib

With random-shapes it is easy to generate a random shape (`bezier.Curve`):

.. code-block:: python

    from random_shapes import get_random_shape

    shp = get_random_shape(n=10, r=0.05, edgy=0.2)
    shp.plot(pts_per_edge=10)


.. image:: _static/shape-example.png
    :alt: Random shape example
    :align: center

This shape can then be turned into a binary image:

.. code-block:: python

    import matplotlib.pyplot as plt

    from random_shapes import bezier_polygon_to_binary_image

    binary_image = bezier_polygon_to_binary_image(shp)
    plt.imshow(binary_image, cmap="gray")

.. image:: _static/rasterize-example.png
    :alt: Binary image example
    :align: center
