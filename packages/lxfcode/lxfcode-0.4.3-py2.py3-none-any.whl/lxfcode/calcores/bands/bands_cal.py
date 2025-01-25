import numpy as np
from ..hamiltonians.tb_h import TightTBGHa
from ..multical.multicorecal import MultiCal
from ..abc.abmoire import ABContiMoHa
from typing import Union
from ..abc.self_types import Path


class BandsCal:
    def __init__(
        self,
        haInst: Union[ABContiMoHa, TightTBGHa],
        p_density=100,
        path: list[Path] | list[np.ndarray] = ["K_b", "M", "Gamma", "K_t"],
        suffix="",
        disable_progress_bar: bool = False,
    ) -> None:
        self.haInst: Union[ABContiMoHa, TightTBGHa] = haInst
        self.p_density = p_density
        self.path: list[Path] | list[np.ndarray] = path

        self.fname = self.haInst.__class__.__name__ + "_{}".format(self.haInst.sigs)
        if suffix:
            self.fname += f"_{suffix}"

        self.disable_progress_bar = disable_progress_bar

    def _set_points(self):
        path_arr_list = []
        last_p = None
        p_num_list = [0]
        for ele_point_i in range(len(self.path) - 1):
            if isinstance(self.path[ele_point_i + 1], str):
                path_point2: str = self.path[ele_point_i + 1]
                path_point1: str = self.path[ele_point_i]
                p2: np.ndarray = getattr(self.haInst, path_point2)
                p1: np.ndarray = getattr(self.haInst, path_point1)
            else:
                p2: np.ndarray = self.path[ele_point_i + 1]
                p1: np.ndarray = self.path[ele_point_i]

            dist = np.linalg.norm(p2 - p1)
            p_num = int(self.p_density * dist)
            p_num_list.append(p_num + p_num_list[-1])
            for ele_i in np.linspace(0, 1, p_num, endpoint=False):
                path_arr_list.append(p1 + ele_i * (p2 - p1))
            last_p = p2

        ### Include the last k point
        path_arr_list.append(last_p)
        return path_arr_list, p_num_list

    def eigenvalues(self, k_arr):
        eig_values = np.linalg.eig(self.haInst.h(k_arr))[0]
        eig_values.sort()
        return eig_values

    def calculate(self) -> tuple[np.ndarray, list[int]]:
        arr_list, xlabel_x = self._set_points()
        cal = MultiCal(
            self.eigenvalues,
            arr_list,
            [],
            disable_progress_bar=self.disable_progress_bar,
        )
        path_energies = cal.calculate()
        return np.real(path_energies), xlabel_x
