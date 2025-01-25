from ..abc.abmoire import ABContiMoHa, ABTBMoHa
import numpy as np
from ..abc.abcal import ABCal
from ..pubmeth.consts import *
from ..vel_op.velop_cal import VelOpCal, VelLoad


class AbsorptionCal(ABCal):
    def __init__(
        self,
        haInst: ABContiMoHa | ABTBMoHa,
        density: int = 70,
        cal_corenum: int = 3,
        e_range: np.ndarray = np.linspace(10, 2500, 400),
        interval_k=0.0001,
        bds_num: int = 5,
        gamma: float = 100,
        degeneracy_factor: float = 1,
        upd_vel_files=False,
    ) -> None:
        super().__init__(haInst, density, cal_corenum)

        self.e_range = e_range

        self.bds_num = bds_num
        self.ki = interval_k
        self.gamma = gamma

        if hasattr(self.haInst.moInst, "areaM"):
            area = self.haInst.moInst.areaM
        else:
            area = self.haInst.moInst.areaO

        self.renorm_const = (
            degeneracy_factor
            * c_eV**2
            / (h_bar_eV * c_speed * epsilon_0_eV)
            / int(self.density**2)
            / area
        )

        self.velopCalInst = VelOpCal(
            self.haInst, self.density, self.calcoren, bds_num=self.bds_num
        )

        self.upd_vel_files = upd_vel_files

    def calculate(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        Mop2, ediff, k_arrs, BZ_bounds = VelLoad(self.velopCalInst).load(
            upd_vel_files=self.upd_vel_files
        )

        ab_dist_mat = []
        for ele_e in self.e_range:
            tmp_ab = Mop2 * self.gamma / ((ediff - ele_e) ** 2 + self.gamma**2)
            ab_dist_mat.append(
                np.sum(
                    tmp_ab / ele_e * self.renorm_const,
                    axis=(len(Mop2.shape) - 1, len(Mop2.shape) - 2),
                )
            )

        ab_dist_mat = np.array(ab_dist_mat)  #   (e_range, kp) shape
        ab_dist_mat = ab_dist_mat.T  #   (kp, e_range) shape

        ab_dist: np.ndarray = ab_dist_mat  #   (kpoints, e_range) array

        return ab_dist, k_arrs, BZ_bounds
