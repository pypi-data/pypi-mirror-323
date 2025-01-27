# random-shapes

Generate random shapes with ease.

![Logo](docs/_static/random-shape-logo.png)

## Installation

You can install random-shapes via pip:

```sh
    pip install random-shapes
```

However, `uv` is recommended for installing python packages:

```sh
    uv add random-shapes
```

## Usage

Install the optional library `matplotlib` for visualization:

```sh
    pip install random-shapes[viz]
    # or
    uv add random-shapes --extra viz
```

With random-shapes it is easy to generate a random shape (`bezier.Curve`):

```python

    from random_shapes import get_random_shape

    shp = get_random_shape(n=10, r=0.05, edgy=0.2)
    shp.plot(pts_per_edge=10)
```

![Random shape example](docs/_static/shape-example.png)

This shape can then be turned into a binary image:

```python
    import matplotlib.pyplot as plt

    from random_shapes import bezier_polygon_to_binary_image

    binary_image = bezier_polygon_to_binary_image(shp)
    plt.imshow(binary_image, cmap="gray")
```

![Binary image example](docs/_static/rasterize-example.png)
