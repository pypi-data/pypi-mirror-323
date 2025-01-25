import matplotlib.pyplot as plt
import numpy as np

from ..filesop.fileman import FileManager
from ..pubmeth import PubMethod
from ..vel_op import VelLoad
from .absorption_cal import AbsorptionCal

plt.rc("font", family="Times New Roman")  # change the font of plot
plt.rcParams["mathtext.fontset"] = "stix"


class AbsorptionPlot:
    fontsize = 12
    titlesize = 14

    def __init__(
        self,
        abCalInst: AbsorptionCal,
        ffolder="",
        disable_elet=False,
    ) -> None:
        self.abCalInst = abCalInst
        self.abFileInst = FileManager(self.abCalInst, "Absorption", ffolder=ffolder)

        self.disable_elet = disable_elet

    def _plot_ele_ab(
        self,
        ab_dist: np.ndarray,  #   (kpoints, e_range) array
        k_arrs,
        bound_vecs,
        elet_dir,
    ):
        fig, ax = plt.subplots(figsize=(7, 7))
        print("Shape: ", ab_dist.shape)

        vmin_val = np.min(np.real(ab_dist))
        vmax_val = np.max(np.real(ab_dist))

        for ele_col in range(ab_dist.shape[-1]):
            fname = self.abFileInst.ele_name.format(ele_col + 1)
            title = r"$\theta = {:.2f}\degree$, $E = {:.2f}$ meV".format(
                self.abCalInst.haInst.moInst.twist_angle,
                self.abCalInst.e_range[ele_col],
            )

            PubMethod.cmap_scatters(
                k_arrs[:, 0],
                k_arrs[:, 1],
                np.real(ab_dist[:, ele_col]),
                bound_vecs,
                elet_dir,
                fname,
                title=title,
                clabel_name="a.u.",
                figax_in=(fig, ax),
                cmap="jet",
                vmin=vmin_val,
                vmax=vmax_val,
            )
        plt.close(fig)

    def plot(self, update_elet=False)->np.ndarray:
        Mop2, ediff, k_arrs, BZ_bounds = VelLoad(
            self.abCalInst.velopCalInst, ffolder=self.abFileInst.ffolder
        ).load(upd_vel_files=self.abCalInst.upd_vel_files)

        print("Calculating absorption, gamma: ", self.abCalInst.gamma)
        ab_dist_mat = []
        for ele_e in self.abCalInst.e_range:
            tmp_ab = (
                Mop2
                * self.abCalInst.gamma
                / ((ediff - ele_e) ** 2 + self.abCalInst.gamma**2)
            )
            ab_dist_mat.append(
                np.sum(
                    tmp_ab / ele_e * self.abCalInst.renorm_const,
                    axis=(len(Mop2.shape) - 1, len(Mop2.shape) - 2),
                )
            )
        ab_dist_mat = np.array(ab_dist_mat)  #   (e_range, kp) shape
        ab_dist_mat = ab_dist_mat.T  #   (kp, e_range) shape

        ab_dist: np.ndarray = ab_dist_mat  #   (kpoints, e_range) array

        ab_intensity = np.sum(ab_dist, axis=0)  #   Sum over all k points contributions

        fig, ax_ab = plt.subplots()
        ax_ab.plot(self.abCalInst.e_range, np.real(ab_intensity))
        ax_ab.set_aspect("auto")
        ax_ab.set_xlabel("E (meV)", fontsize=12)
        ax_ab.set_ylabel("Absorption", fontsize=12)
        ax_ab.set_title(self.abCalInst.haInst.sigs_title, fontsize=14)
        ax_ab.set_xlim(ax_ab.get_xlim())
        ax_ab.set_ylim(ax_ab.get_ylim())
        self.abFileInst.root_dir.save_fig(fig, f"Absorption_{self.abCalInst.gamma}")
        plt.close(fig)

        if (not self.disable_elet) and (update_elet):
            print("Plotting element transitions...")
            self._plot_ele_ab(
                ab_dist,
                k_arrs,
                BZ_bounds,
                self.abFileInst.root_dir,
            )

        return np.real(ab_intensity)
