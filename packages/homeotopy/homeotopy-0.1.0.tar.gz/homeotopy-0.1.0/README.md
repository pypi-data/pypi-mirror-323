# Homotopy

A python library for computing homeomorphisms between some common continuous
spaces.

## Installation

```sh
pip install homeotopy
```

## Usage

```py
import homeotopy

points = ...
# create a mapping from the simplex to the surface of the sphere
mapping = homeotopy.homeomorphism(homeotopy.simplex(), homeotopy.sphere())
sphere_points = mapping(points)

rev_mapping = reversed(mapping)
duplicate_points = rev_mapping(sphere_points)
```
