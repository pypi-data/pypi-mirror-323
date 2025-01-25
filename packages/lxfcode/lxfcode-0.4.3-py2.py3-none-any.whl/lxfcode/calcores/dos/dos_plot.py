from typing import Literal
from .dos_cal import DosCal, DefinedFuncs
from ..filesop.filesave import FilesSave
import matplotlib.pyplot as plt
import numpy as np

__all__ = ["DosCal", "DosPlot"]


class DosPlot:
    """
    Generally, DOS is easy to calculate. Therefore, saving the dos npy is not necessary because it might bi really large. Nevertheless, you can save the dos by letting dos_save=True
    """

    def __init__(
        self, dosCal: DosCal, ffolder="", update_npy=False, dos_save=False
    ) -> None:
        self.dosCalInst = dosCal

        self._supp_info = "../{}/{}_{}_{}".format(
            ffolder,
            self.dosCalInst.haInst.__class__.__name__,
            self.dosCalInst.haInst.sigs,
            self.dosCalInst.density,
        )

        self.dosFolderInst = FilesSave("DOS") + self._supp_info
        self.dos_info = "dos_{}".format(self.dosCalInst.broadening)
        self.e_info = "eig_e"

        self.update_npy = update_npy
        self.save_dos_npy = dos_save

    def _load(self):
        if self.dosFolderInst.exist_npy(self.dos_info) and (not self.update_npy):
            print("Loading existing npy file...")
            dos = self.dosFolderInst.load_npy(self.dos_info)
        else:
            print("Calculating...")
            if self.dosFolderInst.exist_npy(self.e_info):
                print("Using the existing npy file to calculate DOS...")
                eig_e = self.dosFolderInst.load_npy(self.e_info)
                if not self.dosCalInst.large_scal_cal:
                    dos = (
                        DefinedFuncs.deltaF_arct(
                            eig_e, self.dosCalInst.e_range, a=self.dosCalInst.broadening
                        )
                        * self.dosCalInst.renorm_const
                    )
                else:
                    print("Large scale calculations...")
                    dos = []
                    for ele_e in self.dosCalInst.e_range:
                        ele_dos = (
                            DefinedFuncs.deltaF_arct(
                                eig_e, ele_e, a=self.dosCalInst.broadening
                            )
                            * self.dosCalInst.renorm_const
                        )
                        ele_dos = np.sum(ele_dos)
                        dos.append(ele_dos)
                    dos = np.array(dos)
            else:
                print("No existing files, caculating...")
                eig_e, dos = self.dosCalInst.calculate()
            if self.save_dos_npy:
                self.dosFolderInst.save_npy(self.dos_info, dos)
            self.dosFolderInst.save_npy(self.e_info, eig_e)
        return dos * self.dosCalInst.extra_coeff

    def plot(self) -> tuple[np.ndarray, np.ndarray]:
        dos_scale: float | Literal["eVA", "eVperunitcell", "eVperunitmoirecell"] = (
            self.dosCalInst.dos_scale
        )

        ylabel = r"DOS ($\mathrm{meV}^{-1}\cdot \AA^{-2}$)"
        if dos_scale == "eVA":
            ylabel = r"DOS ($\mathrm{eV}^{-1}\cdot \AA^{-2}$)"
        elif dos_scale == "eVperunitcell":
            ylabel = r"DOS ($\mathrm{eV}^{-1}\,\text{per unit cell}$)"
        elif dos_scale == "eVperunitmoirecell":
            ylabel = r"DOS ($\mathrm{eV}^{-1}\,\text{per moir\'e unit cell}$)"

        dos = self._load()
        if not self.dosCalInst.large_scal_cal:
            dos: np.ndarray = dos.sum(axis=-1).sum(axis=-1)
        else:
            print("The array is already reduced to one dimension: ", dos.shape)
        fig, ax_dos = plt.subplots()
        if np.max(dos) < 0.01:
            ax_dos.ticklabel_format(style="sci", scilimits=(-1, 2), axis="y")
        ax_dos.plot(self.dosCalInst.e_range, dos)
        ax_dos.set_aspect("auto")
        ax_dos.set_xlabel("E (meV)", fontsize=12)
        ax_dos.set_ylabel(ylabel, fontsize=12)
        ax_dos.set_title("", fontsize=14)
        ax_dos.set_xlim(ax_dos.get_xlim())
        ax_dos.set_ylim(ax_dos.get_ylim())
        self.dosFolderInst.save_fig(
            fig, fname="dos_{}".format(self.dosCalInst.broadening)
        )

        return self.dosCalInst.e_range, dos


class JdosFiles:
    def __init__(self) -> None:
        pass
