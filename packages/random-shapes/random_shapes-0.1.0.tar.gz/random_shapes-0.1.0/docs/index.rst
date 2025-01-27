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

    pip install random-shapes[viz]
    # or
    uv add random-shapes --extra viz

With random-shapes it is easy to generate a random shape (`bezier.Curve`):

.. code-block:: python

    from random_shapes import Shape

    shp = Shape.random(n=10, r=0.05, edgy=0.2)
    # Shape.curve is a bezier.CurvedPolygon, since Shape is a just wrapper
    shp.curve.plot(pts_per_edge=10)


.. image:: _static/shape-example.png
    :alt: Random shape example
    :align: center

This shape can then be turned into a binary image:

.. code-block:: python

    import matplotlib.pyplot as plt

    binary_image = shp.rasterize(h=512, w=512)
    plt.imshow(binary_image, cmap="gray")

.. image:: _static/rasterize-example.png
    :alt: Binary image example
    :align: center
