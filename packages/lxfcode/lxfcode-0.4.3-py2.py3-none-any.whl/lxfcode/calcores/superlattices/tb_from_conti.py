from typing import Any, Union

import matplotlib.pyplot as plt
import numpy as np

from ..abc.self_types import Path, SKPars

from ..abc.abmoire import ABTBMoHa
from ..filesop.filesave import FilesSave
from ..pubmeth import MoireMethod, PubMethod
from ..pubmeth.pointset import HexLats
from ..superlattices.stru_plot import StruPlot
from .twisted_gra import TightTBG, TightTBGHa


class TBGFromConti(TightTBG):
    def __init__(self, m0: int, r: int, **kwargs) -> None:
        super().__init__(m0, r, **kwargs)
        self.fInst = FilesSave("Structures")
        self.contiR1, self.contiR2, self.contiBound = self.get_contizone_pars()

    @property
    def commBound(self):

        shift_arr = (self.R1 + self.R2) / 2
        bound_vecs = (
            np.vstack(
                [
                    np.zeros((2, 2)),
                    self.R1,
                    self.R1 + self.R2,
                    self.R2,
                    np.zeros((2, 2)),
                ]
            )
            - shift_arr
        )
        return bound_vecs

    def get_contizone_pars(self):
        h: TightTBGHa = self.haClassType(self)
        # vecs = self.structure(expand_times=expand_times, noplot=True)

        ##  Get the continuum zone period and overall twist angle
        twist_angle = h.moInst.twist_angle
        super_period, overall_angle = MoireMethod.hex_conti_period(
            twist_angle, h.moInst.a0
        )

        ##  Get the Superlattice vector for the continuum zone
        conti_R1 = (
            PubMethod.r_mat(overall_angle) @ h.moInst.a1 / np.linalg.norm(h.moInst.a1)
        ) * super_period
        conti_R2 = (
            PubMethod.r_mat(overall_angle) @ h.moInst.a2 / np.linalg.norm(h.moInst.a2)
        ) * super_period

        ##  Get the angle between conti superlattice vector and Commensurate superlattice vector
        angleBetween = np.arccos(
            conti_R1
            @ h.moInst.R1
            / (np.linalg.norm(conti_R1) * np.linalg.norm(h.moInst.R1))
        )
        angleBetween = angleBetween / np.pi * 180

        shift_arr = (conti_R1 + conti_R2) / 2
        new_bound = (
            np.vstack(
                [
                    np.zeros((1, 2)),
                    conti_R1,
                    conti_R1 + conti_R2,
                    conti_R2,
                    np.zeros((1, 2)),
                ]
            )
            - shift_arr
        )

        return conti_R1, conti_R2, new_bound

    def plot_conti_zone(
        self, expand_times=0, xylim=None, new_expan=0, within_supercell=False
    ):

        h: TightTBGHa = self.haClassType(self)
        vecs = self.equal_rvecs(expand_times)
        # vecs = self.structure(expand_times=expand_times, noplot=True)
        print(
            "# of atoms per unit supercell: ",
            len(vecs) // ((2 * (expand_times + 1) + 1) ** 2),
        )

        ##  Get the continuum zone period and overall twist angle
        twist_angle = h.moInst.twist_angle
        print("Twist angle: ", twist_angle)
        super_period, overall_angle = MoireMethod.hex_conti_period(
            twist_angle, h.moInst.a0
        )
        print("Overall twist angle: {:.2f}".format(overall_angle))

        ##  Get the Superlattice vector for the continuum zone
        conti_R1 = (
            PubMethod.r_mat(overall_angle) @ h.moInst.a1 / np.linalg.norm(h.moInst.a1)
        ) * super_period
        conti_R2 = (
            PubMethod.r_mat(overall_angle) @ h.moInst.a2 / np.linalg.norm(h.moInst.a2)
        ) * super_period

        ##  Get the angle between conti superlattice vector and Commensurate superlattice vector
        angleBetween = np.arccos(
            conti_R1
            @ h.moInst.R1
            / (np.linalg.norm(conti_R1) * np.linalg.norm(h.moInst.R1))
        )
        angleBetween = angleBetween / np.pi * 180
        print("Angle Between conti and commensurate: ", angleBetween)

        shift_arr1 = (h.moInst.R1 + h.moInst.R2) / 2
        shift_arr2 = (conti_R1 + conti_R2) / 2

        ##  Get the ratio between previous zone and present zone
        ratio = np.linalg.norm(h.moInst.R1) / np.linalg.norm(conti_R1)
        print("Ratio between two zones: ", ratio)

        previous_bound = (
            np.vstack(
                [
                    np.zeros((1, 2)),
                    h.moInst.R1,
                    h.moInst.R1 + h.moInst.R2,
                    h.moInst.R2,
                    np.zeros((1, 2)),
                ]
            )
            - shift_arr1
        )

        new_bound = (
            np.vstack(
                [
                    np.zeros((1, 2)),
                    conti_R1,
                    conti_R1 + conti_R2,
                    conti_R2,
                    np.zeros((1, 2)),
                ]
            )
            - shift_arr2
        )

        fig, ax = plt.subplots()
        if not within_supercell:
            ax.scatter(vecs[:, 0], vecs[:, 1], s=1)
        else:
            remapped_vecs1 = MoireMethod.basis_change_2d(vecs, h.moInst.R1, h.moInst.R2)
            cond1 = np.logical_and(
                remapped_vecs1[:, 0] < 0.5, remapped_vecs1[:, 0] >= -0.5
            )
            cond2 = np.logical_and(
                remapped_vecs1[:, 1] < 0.5, remapped_vecs1[:, 1] >= -0.5
            )
            cond = np.logical_and(cond1, cond2)
            vecs = vecs[cond]
            ax.scatter(vecs[:, 0], vecs[:, 1], s=1)
        ##  Expand new zones to fill the previous zone
        x, y = np.meshgrid(
            np.arange(-new_expan, new_expan + 1),
            np.arange(-new_expan, new_expan + 1),
        )
        x = x.reshape((-1, 1))
        y = y.reshape((-1, 1))
        indices = np.hstack([x, y])

        for ele_i in indices:
            bound = new_bound + conti_R1 * ele_i[0] + conti_R2 * ele_i[1]
            ax.plot(bound[:, 0], bound[:, 1], "g-")

        ax.plot(previous_bound[:, 0], previous_bound[:, 1], "r--")
        if xylim is not None:
            ax.set_xlim(xylim[:2])
            ax.set_ylim(xylim[2:])
        ax.set_aspect("equal")
        ax.set_xlabel(r"X ($\AA$)")
        ax.set_ylabel(r"Y ($\AA$)")
        ax.set_title(r"$\theta={:.2f}\degree$: Zone comparison".format(twist_angle))
        self.fInst.save_fig(
            fig,
            "{}_{:.2f}_{}_conti_zone".format(
                self.__class__.__name__, twist_angle, expand_times
            ),
        )
        plt.close(fig)

        return vecs, conti_R1, conti_R2, h.moInst.R1, h, new_bound

    def atoms_num_each_conti_zone(self, xylim=None):
        vecs, conti_R1, conti_R2, comm_R1, h, new_bound = self.plot_conti_zone()

        ratio = np.linalg.norm(comm_R1) / np.linalg.norm(conti_R1)
        star_ratio = ratio // 2

        remapped_vecs = MoireMethod.basis_change_2d(vecs, conti_R1, conti_R2)

        ##  Expand new zones to fill the previous zone
        x, y = np.meshgrid(
            np.arange(-star_ratio, star_ratio + 1),
            np.arange(-star_ratio, star_ratio + 1),
        )
        x = x.reshape((-1, 1))
        y = y.reshape((-1, 1))
        indices = np.hstack([x, y])

        atoms_num_list = []
        fig, ax = plt.subplots()

        for ele_i in indices:
            bound = new_bound + conti_R1 * ele_i[0] + conti_R2 * ele_i[1]
            ax.plot(bound[:, 0], bound[:, 1], "g-", lw=0.5)
        for ele_i in indices:
            ##  determine the position of the continuum zone
            xi = ele_i[0]
            yi = ele_i[1]

            ##  determine whether the atoms are in the designated continuum zone.
            cond1 = np.logical_and(
                remapped_vecs[:, 0] < xi + 0.5, remapped_vecs[:, 0] >= xi - 0.5
            )
            cond2 = np.logical_and(
                remapped_vecs[:, 1] < yi + 0.5, remapped_vecs[:, 1] >= yi - 0.5
            )
            cond = np.logical_and(cond1, cond2)

            atoms_within_contizone = vecs[cond]
            atoms_num_list.append(len(atoms_within_contizone))

            ##  Plot the atoms with binary color and label the number of atoms within the zone
            ax.scatter(
                atoms_within_contizone[:, 0],
                atoms_within_contizone[:, 1],
                s=1,
                # c=len(atoms_within_contizone) * [len(atoms_num_list)],
                # cmap="jet",
            )
            center_of_zone = conti_R1 * xi + conti_R2 * yi
            ax.text(
                center_of_zone[0],
                center_of_zone[1],
                "{}".format(len(atoms_within_contizone)),
                color="r",
                clip_on=True,
            )
        ax.set_aspect("equal")
        ax.set_xlabel(r"X ($\AA$)")
        ax.set_ylabel(r"Y ($\AA$)")
        ax.set_title("Assign atoms to each continuum zone")
        if xylim is not None:
            ax.set_xlim(xylim[:2])
            ax.set_ylim(xylim[2:])
        self.fInst.save_fig(
            fig,
            "remapped_{}_{}_ratio{:.2f}_".format(
                self.__class__.__name__, h.moInst.twist_angle, ratio
            ),
        )

    def lats_transf(self, r_angle=0, shift_arr=np.array([0, 0])):
        return HexLats(
            self.a1,
            self.a2,
            density_tuple=(self.scale, self.scale),
            r_angle=r_angle,
            shift_arr=np.array(shift_arr),
        ).basis_change(self.contiR1, self.contiR2)

    def structure(self, expand_times=0, region_index=[0, 0], suffix=""):
        print("Plotting structure of {}. ".format(self.__class__.__name__))

        vecs = self.equal_rvecs(expand_times=expand_times, bounds_vals=region_index)

        fname = self.__class__.__name__ + "_{:.2f}_{}_remappedzone".format(
            self.twist_angle, expand_times
        )
        if suffix:
            fname = fname + f"_{suffix}"

        fig, ax_stru = plt.subplots()

        # PubMethod.connect_neighbors(vecs, ax_stru, cutoff=1.43)
        zone_shift = region_index[0] * self.contiR1 + region_index[1] * self.contiR2

        contiBound = self.contiBound #+ zone_shift
        commBound = self.commBound + zone_shift
        ax_stru.plot(contiBound[:, 0], contiBound[:, 1], "g")
        ax_stru.plot(commBound[:, 0], commBound[:, 1], "r--")
        ax_stru.scatter(vecs[:, 0], vecs[:, 1])
        ax_stru.set_aspect("equal")
        ax_stru.set_xlabel(r"x ($\AA$)", fontsize=12)
        ax_stru.set_ylabel(r"y ($\AA$)", fontsize=12)
        ax_stru.set_title(
            r"$\theta={:.2f}\degree$".format(self.twist_angle), fontsize=14
        )
        self.fInst.save_fig(fig, fname)
        plt.close(fig)

        return vecs

    def atoms_rvec(
        self,
        lat_i: Union[str, np.ndarray] = "within",
        zdefault=0,
        bounds_vals=[0, 0],
    ):
        """Function to get tht actual position vectors for each atom based on the input index or the
        actual R1 R2 coordinates.

        Args:
            zdefault (z shift for atoms): float
            lat_i: layer index. "within" means all the atoms within the supercell

        Returns:
            Atoms position vectors in the real space: np.ndarray
        """
        lats = getattr(self, "latwithin")(bounds_vals)
        z = 0

        if isinstance(lat_i, np.ndarray):
            if len(lat_i.shape) == 1:
                lats = lat_i.reshape((1, -1))
                z = zdefault * np.ones((len(lats), 1))
            elif len(lat_i.shape) > 1 and lat_i.shape[0] > 1:
                lats = lat_i
                zi = (np.array(self.lindexes) - 1).reshape((-1, 1))
                z = np.kron(zi, np.ones((len(lats) // len(self.lindexes), 1))) * self.d
        elif lat_i == "within":
            lats = getattr(self, "latwithin")(bounds_vals)
            zi = (np.array(self.lindexes) - 1).reshape((-1, 1))
            z = np.kron(zi, np.ones((len(lats) // len(self.lindexes), 1))) * self.d
        xy_pos = np.kron(lats[:, 0].reshape((-1, 1)), self.contiR1) + np.kron(
            lats[:, 1].reshape((-1, 1)), self.contiR2
        )
        return np.hstack([xy_pos, z])

    def bands(
        self,
        path: list[Path] | list[np.ndarray] = ["K_t", "K_b", "Gamma", "M"],
        suffix="contizone",
        ylim=None,
        density=100,
        ticklabelsize=10,
        titlesize=14,
        fontsize=12,
        title_name=None,
        h_pars: SKPars | None = None,
    ) -> tuple[np.ndarray, list]:
        return super().bands(
            path,
            suffix,
            ylim,
            density,
            ticklabelsize,
            titlesize,
            fontsize,
            title_name,
            h_pars,
        )

    def _getlatswithin(self, lat_i, region_index=[0, 0]):
        return super()._getlatswithin(lat_i, region_index)

    # def equal_rvecs(self, expand_times=0):
    #     ##  Expand equivalent atoms using expand basis, generally, it is assumed that nine expansion basises are used.
    #     ##  olats is the original lattices under R1-R2 coordinates but expanded by kronecker method.
    #     x, y = np.meshgrid(
    #         np.arange(-1 - expand_times, 2 + expand_times),
    #         np.arange(-1 - expand_times, 2 + expand_times),
    #     )
    #
    #     expand_basis = np.hstack([x.reshape(-1, 1), y.reshape(-1, 1)])
    #     expand_vecs = np.kron(np.ones((len(self.latwithin), 1)), expand_basis)
    #     olats = np.kron(self.latwithin, np.ones((len(expand_basis), 1)))
    #     exlats = expand_vecs + olats
    #
    #     rvecs = self.atoms_rvec(exlats)
    #     return rvecs

    #
    # def good(self):
    #     return
