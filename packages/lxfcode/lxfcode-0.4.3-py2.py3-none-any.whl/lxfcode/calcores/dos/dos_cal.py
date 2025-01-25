from typing import Literal
from ..abc.abmoire import ABContiMoHa
from ..abc.abcal import ABCal
from ..pubmeth import DefinedFuncs

from ..multical.multicorecal import MultiCal
import sys

import numpy as np


class DosCal(ABCal):
    def __init__(
        self,
        haInst: ABContiMoHa,
        density: int = 70,
        cal_corenum: int = 3,
        e_range=np.linspace(-2000, 200, 300),
        dos_broadening=1,
        large_scale_cal=False,
        spin_degeneracy=2,
        valley_degeneracy=2,
        dos_scale: float | Literal["eVA", "eVperunitcell", "eVperunitmoirecell"] = 1.0,
    ) -> None:
        super().__init__(haInst, density, cal_corenum)

        self.e_range = e_range
        self.broadening = dos_broadening

        self.large_scal_cal = large_scale_cal

        self.spin_degeneracy = spin_degeneracy
        self.valley_degeneracy = valley_degeneracy

        self.dos_scale = dos_scale

        if self.dos_scale == "eVA":
            self.extra_coeff = 1000
        elif self.dos_scale == "eVperunitcell":
            self.extra_coeff = 1000 * self.haInst.moInst.areaO
        elif self.dos_scale == "eVperunitmoirecell":
            self.extra_coeff = 1000 * self.haInst.moInst.areaM
        else:
            self.extra_coeff = self.dos_scale

    @property
    def renorm_const(self):
        return (
            self.spin_degeneracy
            * self.valley_degeneracy
            / (self.density**2 * self.haInst.moInst.areaM)
        )

    def energies_cal(self, k_arr):
        h = self.haInst.h(k_arr[:2])

        eig_vals = np.real(np.linalg.eig(h)[0])

        eig_vals.sort()

        return np.real(eig_vals)

    def calculate(self, zero_median=True):
        k_arrs = self.kps_in_BZ()[0]

        eig_vals = MultiCal(
            self.energies_cal,
            k_arrs,
            [],
            core=self.calcoren,
        ).calculate()

        eig_vals = np.array(eig_vals)
        if zero_median:
            eig_vals = eig_vals - np.median(eig_vals)
        # print(eig_vals)

        if not self.large_scal_cal:
            dos = (
                DefinedFuncs.deltaF_arct(eig_vals, self.e_range, a=self.broadening)
                * self.renorm_const
            )
        else:
            print("Large scale calculations...")
            dos = []
            for ele_e in self.e_range:
                ele_dos = (
                    DefinedFuncs.deltaF_arct(eig_vals, ele_e, a=self.broadening)
                    * self.renorm_const
                )
                ele_dos = np.sum(ele_dos)
                dos.append(ele_dos)
            dos = np.array(dos)

        print("Shape of the eigen energy matrix: ", dos.shape)
        print("Size of joint energy (MB): ", sys.getsizeof(dos) / 1024**2)

        return eig_vals, dos  # eigen_values_mat, dos_results
