from dataclasses import dataclass
from functools import cache

import numpy as np
from numpy.typing import NDArray

from ._homeomorphism import Topology


@dataclass(frozen=True, slots=True)
class Plane(Topology):
    """The topology of the euclidian plane.

    This represents all points in R^n, but boundary points map to inf.

    Remarks
    -------
    While translations will keep all points valid, this will try to keep points
    at the "center" of the space mapped to (0, 0, ..., 0).
    """

    def to_inf_ball(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.tanh(points)

    def from_inf_ball(self, points: NDArray[np.float64]) -> NDArray[np.float64]:
        # -1 and 1 raise this warning but produce the correct result, we clip in case things are a little outside
        with np.errstate(divide="ignore"):
            return np.arctanh(np.clip(points, -1, 1))


@cache
def plane() -> Plane:
    """Create a topology of the euclidian plane."""
    return Plane()
