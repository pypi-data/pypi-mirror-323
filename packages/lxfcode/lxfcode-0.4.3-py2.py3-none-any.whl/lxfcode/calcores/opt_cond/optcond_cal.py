from ..absorption.absorption_cal import AbsorptionCal
from ..vel_op import VelLoad
from ..abc.abmoire import ABContiMoHa, ABTBMoHa
import numpy as np
from ..pubmeth.consts import sigma_xx_mono, c_speed, epsilon_0_eV

__all__ = ["OptCondCal"]


class OptCondCal(AbsorptionCal):
    def __init__(
        self,
        haInst: ABContiMoHa | ABTBMoHa,
        density: int = 70,
        cal_corenum: int = 3,
        e_range: np.ndarray = ...,
        interval_k=0.0001,
        bds_num: int = 5,
        gamma: float = 100,
        degeneracy_factor: float = 1,
        upd_vel_files: bool = False,
    ) -> None:
        super().__init__(
            haInst,
            density,
            cal_corenum,
            e_range,
            interval_k,
            bds_num,
            gamma,
            degeneracy_factor,
            upd_vel_files,
        )

        self.renorm_const = self.renorm_const / sigma_xx_mono * c_speed * epsilon_0_eV

    # def calculate(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    #     Mop2, ediff, k_arrs, BZ_bounds = VelLoad(self.velopCalInst).load(
    #         upd_vel_files=self.upd_vel_files
    #     )
    #
    #     cond_dist_mat = []
    #     for ele_e in self.e_range:
    #         tmp_cond = Mop2 / (ediff * (ediff + ele_e + 1j * self.gamma)) * 1j
    #         cond_dist_mat.append(
    #             np.sum(
    #                 tmp_cond * self.renorm_const,
    #                 axis=(len(Mop2.shape) - 1, len(Mop2.shape) - 2),
    #             )
    #         )
    #
    #     cond_dist_mat = np.array(cond_dist_mat)  #   (e_range, kp) shape
    #     cond_dist_mat = cond_dist_mat.T  #   (kp, e_range) shape
    #
    #     cond_dist: np.ndarray = cond_dist_mat  #   (kp, e_range) shape
    #
    #     return cond_dist, k_arrs, BZ_bounds
