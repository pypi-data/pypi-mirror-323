from ..abc.abmoire import ABContiMoHa
import numpy as np
from ..multical.multicorecal import MultiCal
from ..abc.abcal import ABCal
from ..pubmeth.consts import *
from ..filesop.filesave import FilesSave
from ..filesop.fileman import FileManager

__all__ = ["VelLoad", "VelOpCal"]


class VelOpCal(ABCal):
    def __init__(
        self,
        hInst: ABContiMoHa,
        density: int = 70,
        cal_corenum: int = 3,
        e_range=np.linspace(10, 2500, 400),
        interval_k=0.0001,
        bds_num: int = 5,
        gamma=100,
        renorm_const=1,
    ) -> None:
        super().__init__(hInst, density, cal_corenum)

        self.e_range = e_range

        self.bds_num = bds_num
        self.ki = interval_k
        self.gamma = gamma

        self.renorm_const = renorm_const

    def vel_cal(self, k_arr):
        hc = self.haInst.h(k_arr)

        hxd = (self.haInst.h(k_arr + np.array([self.ki, 0])) - hc) / (
            self.ki * self.haInst.moInst.renormed_BZ_K_side
        )
        hyd = (self.haInst.h(k_arr + np.array([0, self.ki])) - hc) / (
            self.ki * self.haInst.moInst.renormed_BZ_K_side
        )

        eig_vals, eig_vecs = np.linalg.eig(hc)

        mid_i = len(eig_vals) // 2

        if self.bds_num > mid_i:
            print(
                f"\033[31mYou are requiring bands way more than the system really has!\033[0m. The system only has {mid_i} bands. Please reset the bands you require!!!"
            )
            raise ValueError("Please reset the bands!!!")

        v_slice = (
            slice(mid_i - 1, mid_i - 1 - self.bds_num, -1)
            if mid_i - 1 - self.bds_num >= 0
            else slice(mid_i - 1, -(len(eig_vals) + 1), -1)
        )
        c_slice = (
            slice(mid_i, mid_i + self.bds_num)
            if mid_i + self.bds_num <= len(eig_vals)
            else slice(mid_i, len(eig_vals))
        )

        ##  Obtain the eigen energies and vectors of corresponding sliced bands
        v_energy_arr: np.ndarray = eig_vals[np.argsort(np.real(eig_vals))[v_slice]]
        v_states_arr: np.ndarray = eig_vecs.T[np.argsort(np.real(eig_vals))[v_slice]]

        c_energy_arr: np.ndarray = eig_vals[np.argsort(np.real(eig_vals))[c_slice]]
        c_states_arr: np.ndarray = eig_vecs.T[np.argsort(np.real(eig_vals))[c_slice]]

        bds_num = len(v_energy_arr)

        hx = np.conj(c_states_arr) @ hxd @ v_states_arr.T
        hy = np.conj(c_states_arr) @ hyd @ v_states_arr.T

        Mop2: np.ndarray = abs(hx) ** 2 + abs(hy) ** 2  #   n by n matrix

        ediff: np.ndarray = np.kron(
            c_energy_arr.reshape((-1, 1)), np.ones((1, bds_num))
        ) - np.kron(
            np.ones((bds_num, 1)), v_energy_arr.reshape((1, -1))
        )  #   n by n matrix

        return Mop2, ediff

    def calculate(
        self,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        print("Calculating velocity operators")
        k_arrs, BZ_bounds = self.kps_in_BZ()

        out_list = MultiCal(
            self.vel_cal, k_arrs, core=self.calcoren, disable_progress_bar=True
        ).calculate()  #   velop: (e_range) length

        out_arr = np.array(out_list)

        if (
            len(out_arr.shape) == 2
        ):  ## Corresponding to single transitions like monolayer graphene, shape of (kp * 1)
            Mop2: np.ndarray = out_arr[:, 0]  #   (kp * out_i) shape
            ediff: np.ndarray = out_arr[:, 1]  #   (kp * out_i) shape
            return Mop2, ediff, k_arrs, BZ_bounds

        Mop2: np.ndarray = out_arr[:, 0, :]  #   (kp * out_i * n) shape
        ediff: np.ndarray = out_arr[:, 1, :]  #   (kp * out_i * n) shape

        return Mop2, ediff, k_arrs, BZ_bounds


class VelLoad:
    def __init__(self, velopInst: VelOpCal, ffolder="") -> None:
        self.velopInst = velopInst

        self.velFileInst = FileManager(
            self.velopInst,
            "Vel",
            results_list=["Mop2", "ediff", "karrs", "BZ_bounds"],
            dir_extra_suffix=[f"{self.velopInst.bds_num}"],
            ffolder=ffolder,
        )

    def load(self, check_bds_upd=False, upd_vel_files=False) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
    ]:
        Mop2: np.ndarray
        Mop2, ediff, k_arrs, BZ_bounds = self.velFileInst.load(enable_message=False)
        if self.velopInst.bds_num > Mop2.shape[-1] and check_bds_upd:
            print(
                "Requiring more bands than the npy files have. Updating Mop2 and etc npy files"
            )
            Mop2, ediff, k_arrs, BZ_bounds = self.velFileInst.load(
                update_sourcenpy=True
            )
        elif upd_vel_files:
            print("\033[32mUpdating velocity files\033[0m")
            Mop2, ediff, k_arrs, BZ_bounds = self.velFileInst.load(
                update_sourcenpy=True
            )
        else:
            print(f"Using Mop2 data with shape: {Mop2.shape}")
            print(f"Existing data shape: ({Mop2.shape[-1]}, {Mop2.shape[-1]})")
        return Mop2, ediff, k_arrs, BZ_bounds
