from ..pubmeth.methods import MoireMethod
from ..abc.abmoire import ABCommGraMoires
import numpy as np
import matplotlib.pyplot as plt
from ..filesop.filesave import FilesSave
from ..pubmeth import PubMethod


class StruPlot:
    def __init__(self, moInst: ABCommGraMoires) -> None:
        self.moInst = moInst

        self.space = self.moInst.a0 / np.sqrt(3)
        self.filrInst = FilesSave("Structures")

    def vecs(self, expand_times=0):
        return self.moInst.equal_rvecs(expand_times)

    def _get_contizone(self):

        h = self.moInst.haClassType(self.moInst)

        twist_angle = h.moInst.twist_angle
        super_period, overall_angle = MoireMethod.hex_conti_period(
            twist_angle, h.moInst.a0
        )

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

        shift_arr2 = (conti_R1 + conti_R2) / 2

        ##  Get the ratio between previous zone and present zone
        ratio = np.linalg.norm(h.moInst.R1) / np.linalg.norm(conti_R1)

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
        return new_bound

    def plot_stru(self, expand_times=0, plot_contizone=False):
        ##  Obtain all atom positions "vecs", vecs are composed of all atoms within one supercell.
        ##  "vecs" is ordered by the atoms from each layer, e.x., layer1, layer2 ...
        print("Plotting structure of {}. ".format(self.moInst.__class__.__name__))

        vecs = self.moInst.equal_rvecs(expand_times=expand_times)

        shift_arr = (self.moInst.R1 + self.moInst.R2) / 2
        bound_vecs = (
            np.vstack(
                [
                    np.zeros((2, 2)),
                    self.moInst.R1,
                    self.moInst.R1 + self.moInst.R2,
                    self.moInst.R2,
                    np.zeros((2, 2)),
                ]
            )
            - shift_arr
        )

        fname = self.moInst.__class__.__name__ + "_{:.2f}_{}".format(
            self.moInst.twist_angle, expand_times
        )
        fig, ax_stru = plt.subplots()

        PubMethod.connect_neighbors(vecs, ax_stru, cutoff=1.43)

        ax_stru.plot(bound_vecs[:, 0], bound_vecs[:, 1], "r")
        if plot_contizone:
            contizone = self._get_contizone()
            ax_stru.plot(contizone[:, 0], contizone[:, 1], color="yellow", ls="--")
            fname += "_with_contizone"

        ax_stru.scatter(vecs[:, 0], vecs[:, 1], s=1)
        ax_stru.set_aspect("equal")
        ax_stru.set_xlabel(r"x ($\AA$)", fontsize=12)
        ax_stru.set_ylabel(r"y ($\AA$)", fontsize=12)
        ax_stru.set_title(
            r" $(m_0, r)=({}, {}),\theta={:.2f}\degree$".format(
                self.moInst.m0, self.moInst.r, self.moInst.twist_angle
            ),
            fontsize=14,
        )
        self.filrInst.save_fig(fig, fname)
        plt.close(fig)
        return vecs
