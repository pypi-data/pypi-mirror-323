from ..filesop.fileman import FileManager
from .optcond_cal import OptCondCal
import numpy as np
from ..filesop.filesave import FilesSave
import matplotlib.pyplot as plt
from ..pubmeth import PubMethod
from ..vel_op.velop_cal import VelLoad
from tqdm import tqdm


plt.rc("font", family="Times New Roman")  # change the font of plot
plt.rcParams["mathtext.fontset"] = "stix"

__all__ = ["OptCondPlot"]


class OptCondPlot:
    fontsize = 12
    titlesize = 14

    def __init__(
        self,
        OptCondInst: OptCondCal,
        ffolder="",
        disable_elet=False,
    ) -> None:
        self.OptCondInst = OptCondInst
        self.ffolder = ffolder
        self.results_list = ["cond_dist", "kvecs", "bz_bounds"]

        self.OptFileInst = FileManager(
            self.OptCondInst,
            root_dir_name="OptCond",
            ffolder=ffolder,
            results_list=self.results_list,
        )

        self.disable_elet = disable_elet

    def _plot_ele_e_component(
        self,
        ab_dist: np.ndarray,  #   (kpoints, e_range) array
        k_arrs: np.ndarray,
        bound_vecs: np.ndarray,
        save_dir: FilesSave,
        uniform_cbar=True,
    ) -> None:

        fig, ax = plt.subplots(figsize=(7, 7))
        print("Shape: ", ab_dist.shape)

        if uniform_cbar:
            vmin_val = np.min(np.real(ab_dist))
            vmax_val = np.max(np.real(ab_dist))
        else:
            vmin_val = None
            vmax_val = None

        for ele_col in tqdm(range(ab_dist.shape[-1])):
            fname_real = (
                self.OptFileInst.ele_name.format(
                    round(self.OptCondInst.e_range[ele_col], 2)
                )
                + "_real"
            )
            fname_abs = (
                self.OptFileInst.ele_name.format(
                    round(self.OptCondInst.e_range[ele_col], 2)
                )
                + "_abs"
            )

            title = r"$\theta = {:.2f}\degree$, $E = {:.2f}$ meV".format(
                self.OptCondInst.haInst.moInst.twist_angle,
                self.OptCondInst.e_range[ele_col],
            )  #   title for each photon energy

            PubMethod.cmap_scatters(  # No need for square matrix to plot the distributions
                k_arrs[:, 0],
                k_arrs[:, 1],
                np.real(ab_dist[:, ele_col]),
                bound_vecs,
                save_dir,
                fname_real,
                title=title,
                clabel_name="(a.u.)",
                figax_in=(fig, ax),
                cmap="jet",
                vmin=vmin_val,
                vmax=vmax_val,
            )

            PubMethod.cmap_scatters(  # No need for square matrix to plot the distributions
                k_arrs[:, 0],
                k_arrs[:, 1],
                np.abs(ab_dist[:, ele_col]),
                bound_vecs,
                save_dir,
                fname_abs,
                title=title,
                clabel_name="(a.u.)",
                figax_in=(fig, ax),
                cmap="jet",
                vmin=vmin_val,
                vmax=vmax_val,
            )

        plt.close(fig)

    def _plot_overall(self, cond_intensity):
        fig, ax_ab = plt.subplots(figsize=(7, 5))
        (line,) = ax_ab.plot(self.OptCondInst.e_range, np.real(cond_intensity))
        ax_ab.set_aspect("auto")
        ax_ab.set_xlabel("E (meV)", fontsize=12)
        ax_ab.set_ylabel(r"$\sigma_{\text{mono}}$", fontsize=12)
        ax_ab.set_title(self.OptCondInst.haInst.sigs_title, fontsize=14)
        self.OptFileInst.root_dir.save_fig(
            fig,
            f"Cond_real_{self.OptCondInst.gamma}",
        )
        line.remove()
        ax_ab.plot(self.OptCondInst.e_range, np.imag(cond_intensity))
        self.OptFileInst.root_dir.save_fig(
            fig,
            f"Cond_imag_{self.OptCondInst.gamma}",
        )
        plt.close(fig)

    def _plot_ele_transitions(
        self,
        tmp_cond: np.ndarray,
        cv_pairs: list[tuple],
        energy: float,
        k_arrs,
        bound_vecs,
        uni_vmin=None,
        uni_vmax=None,
    ):
        """
        Mop2: (kp_points, bds_num, bds_num)
        """
        eles_dir: str = "/".join(["OptCond", "eles", *self.ffolder.split("/")])
        fileInst = FilesSave(eles_dir)

        fig, ax = plt.subplots(figsize=(7, 7))

        # if uniform_cbar:
        #     vmin_val = np.min(np.real(tmp_cond))
        #     vmax_val = np.max(np.real(tmp_cond))
        # else:
        #     vmin_val = None
        #     vmax_val = None

        ele_trans_sum_list = []

        for ele_pair in cv_pairs:
            vband_i = ele_pair[0] - 1
            cband_i = ele_pair[1] - 1

            fname = f"e{round(energy,2)}_v{ele_pair[0]}_c{ele_pair[1]}"

            if vband_i < 0 or vband_i > tmp_cond.shape[-1] - 1:
                raise IndexError("No such bands number.")

            ele_dist = tmp_cond[:, cband_i, vband_i]

            title = r"E=%.2f meV, $\theta = %.2f\degree$, $v_{%s} \to c_{%s}$" % (
                energy,
                self.OptCondInst.haInst.moInst.twist_angle,
                ele_pair[0],
                ele_pair[1],
            )

            PubMethod.cmap_scatters(  # No need for square matrix to plot the distributions
                k_arrs[:, 0],
                k_arrs[:, 1],
                ele_dist,
                bound_vecs,
                fileInst,
                fname,
                title=title,
                clabel_name="(a.u.)",
                figax_in=(fig, ax),
                cmap="jet",
                vmin=uni_vmin,
                vmax=uni_vmax,
            )
            ele_trans_sum_list.append(np.sum(ele_dist))

        plt.close(fig)

        fig, ax = plt.subplots(figsize=(24, 4))
        ax.plot(np.real(ele_trans_sum_list))
        ax.set_ylabel("Transition sum")
        ax.set_xticks(np.arange(0, len(ele_trans_sum_list)), cv_pairs, rotation=-90)
        # ax.set_title("Title")
        fileInst.save_fig(fig, f"e_{energy}.png", subfolder="trans_sum")
        plt.close(fig)

    def plot(
        self,
        plot_eles: bool = False,
        check_bds_upd=False,
        load_from_exist_dat=False,
        uniform_cbar_for_ele_e_component=True,
        plot_ele_trans: bool = False,
        cv_pairs=None,
    ) -> np.ndarray:
        """Calculations and plot of complex conductivity

        Args:
            update_elet: [Update the ele transitions figure or not]
            update_gamma: [update gamma or e_range or not]

        Returns:
            Complex conductivity of (kp, e_range) shape
        """
        if load_from_exist_dat:
            print(
                "Loading existing data. Excluding calculations based on broadening and incident photon energy."
            )
            cond_dist, k_arrs, bound_vecs = (
                self.OptFileInst.load()
            )  #   (kp, e_range) shape
            cond_intensity = np.sum(cond_dist, axis=0)
            self._plot_overall(cond_intensity)
            return cond_dist

        Mop2, ediff, k_arrs, bound_vecs = VelLoad(
            self.OptCondInst.velopCalInst, ffolder=self.ffolder
        ).load(check_bds_upd, upd_vel_files=self.OptCondInst.upd_vel_files)

        cond_dist_mat = []
        for ele_e in self.OptCondInst.e_range:
            tmp_cond = (
                Mop2 / (ediff * (ediff - ele_e + 1j * self.OptCondInst.gamma)) * 1j
            )

            ele_trans_result = tmp_cond * self.OptCondInst.renorm_const

            uni_vmin = np.min(np.real(ele_trans_result))
            uni_vmax = np.max(np.real(ele_trans_result))

            if plot_ele_trans:
                if cv_pairs is None:
                    cv_pairs = [(m, n) for m in range(1, 3) for n in range(1, 3)]
                    print("Using default cv pairs: ", cv_pairs)
                # elif cv_pairs

                self._plot_ele_transitions(
                    ele_trans_result,
                    cv_pairs,
                    ele_e,
                    k_arrs,
                    bound_vecs,
                    uni_vmin=uni_vmin,
                    uni_vmax=uni_vmax,
                )

            cond_dist_mat.append(
                np.sum(
                    # tmp_cond * self.OptCondInst.renorm_const,
                    ele_trans_result,
                    axis=(len(Mop2.shape) - 1, len(Mop2.shape) - 2),
                )
            )

        cond_dist_mat = np.array(cond_dist_mat)  #   (e_range, kp) shape
        cond_dist_mat = cond_dist_mat.T  #   (kp, e_range) shape

        cond_dist: np.ndarray = cond_dist_mat  #   (kp, e_range) shape

        if (not self.disable_elet) or (plot_eles):
            print("Plotting element transitions...")
            self._plot_ele_e_component(
                cond_dist,
                k_arrs,
                bound_vecs,
                self.OptFileInst.root_dir,
                uniform_cbar=uniform_cbar_for_ele_e_component,
            )

        cond_intensity = np.sum(cond_dist, axis=0)

        self._plot_overall(cond_intensity)

        self.OptFileInst.save([cond_dist, k_arrs, bound_vecs])

        return cond_intensity
