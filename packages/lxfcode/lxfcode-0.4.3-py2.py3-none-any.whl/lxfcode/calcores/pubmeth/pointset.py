from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from ..filesop.filesave import FilesSave
from ..pubmeth import PubMethod

if TYPE_CHECKING:
    from ..abc import axPars

    pass

__all__ = ["TriLats", "HexLats"]


class TriLats:
    def __init__(
        self,
        a1: np.ndarray,
        a2: np.ndarray,
        density_tuple: tuple = (15, 15),
        shift_arr: np.ndarray = np.array([0, 0]),
    ) -> None:
        self.a1 = a1
        self.a2 = a2
        self.shift_arr = shift_arr

        self.density_tuple = density_tuple

    @property
    def points(self) -> np.ndarray:
        xm, ym = np.meshgrid(
            np.arange(-self.density_tuple[0], self.density_tuple[0]),
            np.arange(-self.density_tuple[1], self.density_tuple[1]),
        )
        xm = xm.reshape((-1, 1))
        ym = ym.reshape((-1, 1))
        return xm * self.a1 + ym * self.a2 + self.shift_arr

    def __getitem__(self, key):
        return self.points[key]


class HexLats:
    def __init__(
        self,
        a1: np.ndarray,
        a2: np.ndarray,
        density_tuple: tuple = (15, 15),
        r_angle=0,
        shift_arr: np.ndarray | tuple[float, float] = np.array([0, 0]),
        z_shift: float | None = 0,
    ) -> None:
        """init function for hexagonal lattices

        Args:
            r_angle (rotation angle, unit of degree): float
            a1: lattices
            a2: lattice vectors
            density_tuple: density of the dots along two basis vectors.
            shift_arr: in-plane shifts
            z_shift: z-direction shift
        """
        self.a1 = a1
        self.a2 = a2
        self.density_tuple = density_tuple

        self.r_angle = r_angle
        self.shift_arr = shift_arr

        self.z_shift = z_shift

        if a1 @ a2 < 0:
            self.d_arr = (a1 - a2) / 3
        elif a1 @ a2 > 0:
            self.d_arr = (a1 + a2) / 3

    @property
    def lat1(self):
        return TriLats(self.a1, self.a2, self.density_tuple)

    @property
    def lat2(self):
        return TriLats(self.a1, self.a2, self.density_tuple, shift_arr=self.d_arr)

    @property
    def fInst(self):
        return FilesSave("Plot/HexLats")

    @property
    def _all_lats(self) -> np.ndarray:
        all_lats = (
            np.transpose(
                PubMethod.r_mat(self.r_angle)
                @ np.vstack([self.lat1[:], self.lat2[:]]).T
            )
            + self.shift_arr
        )
        if self.z_shift is not None:
            z_arr = np.ones((len(all_lats), 1)) * self.z_shift
            all_lats = np.hstack([all_lats, z_arr])

        return all_lats

    @_all_lats.setter
    def _all_lats(self, condition) -> np.ndarray:
        return self._all_lats[condition]

    def __getitem__(self, key):
        return self._all_lats[key]

    def __repr__(self) -> str:
        return str(self[:])

    def __add__(self, arrs: np.ndarray):
        if len(arrs.shape) < 2:
            if arrs.shape[0] == self[:].shape[1]:
                return self[:] + np.kron(np.ones((len(self[:]), 1)), arrs)
            else:
                raise TypeError(
                    "Two arrs must at least have the same columns. The Shape of two array is ",
                    arrs.shape,
                    self[:].shape,
                )

        elif len(arrs.shape) == 2:
            if arrs.shape == self[:].shape:
                return self[:] + arrs
            else:
                raise TypeError(
                    "Two arrs must have the same shape. The Shape of two array is ",
                    arrs.shape,
                    self[:].shape,
                )

    def __sub__(self, arrs: np.ndarray):
        return self.__add__(-arrs)

    def basis_change(self, r1: np.ndarray, r2: np.ndarray):
        """Change the coordinates of points based on the given r1, r2

        Args:
            r1: vectors of new basis
            r2: vectors of new basis

        Returns:
            arrays of the points in the new basis: np.ndarray
        """
        inv_mat = np.linalg.inv(
            np.array(
                [
                    [np.linalg.norm(r1) ** 2, r1 @ r2],
                    [r1 @ r2, np.linalg.norm(r1) ** 2],
                ]
            )
        )

        lats: np.ndarray = self[:][:, :2] @ np.hstack(
            [r1.reshape((-1, 1)), r2.reshape((-1, 1))]
        )

        return np.transpose(inv_mat @ lats.T)

    def plot(
        self,
        fig_name="hex_lattices",
        splitAB=False,
        reveal_hex_zone=False,
        pars_forax: axPars = None,
    ) -> tuple[Figure, Axes]:
        """
        Plot points distributions
        """

        points = self[:]
        fig, ax = plt.subplots()
        if splitAB:
            ax.scatter(
                points[: len(points) // 2, 0],
                points[: len(points) // 2, 1],
                marker=pars_forax.scatterType,
                s=pars_forax.scatterSize,
                c="r",
            )
            ax.scatter(
                points[len(points) // 2 :, 0],
                points[len(points) // 2 :, 1],
                marker=pars_forax.scatterType,
                s=pars_forax.scatterSize,
                c="b",
            )
        else:
            ax.scatter(
                points[:, 0],
                points[:, 1],
                marker=pars_forax.scatterType,
                s=pars_forax.scatterSize,
                c="r",
            )
        ax.set_aspect(pars_forax.aspect)
        ax.set_xlabel(pars_forax.xlabel)
        ax.set_ylabel(pars_forax.ylabel)
        ax.set_xlim(pars_forax.xlim)
        ax.set_ylim(pars_forax.ylim)

        if reveal_hex_zone:
            pass

        ax.set_title(pars_forax.title)
        self.fInst.save_fig(fig, fig_name)
        if pars_forax.return_ax:
            return fig, ax
        else:
            plt.close(fig)
