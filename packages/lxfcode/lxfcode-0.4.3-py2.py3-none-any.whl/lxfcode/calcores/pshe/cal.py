from typing import Callable, Literal, Union

import numpy as np
from scipy import interpolate

from ..abc.aboptics import (
    FresnelCoeff,
    Layer,
    Light,
    Permittivity,
    ReducedConductivity,
    WaveLengthRange,
    WspInst,
)

from ..abc.abpshe import MediumObj
from ..abc.self_types import DatFiles
from ..filesop.fileread import FilesRead
from .shift import IFShift, GHShift, ShiftObj

__all__ = ["IFCalculation", "GHCalculation", "BGIF", "BGGH"]


class IFCalculation:
    def __init__(
        self,
        wls_range=None,
        e_range=None,
        light: Literal["lcp", "rcp"] | Light = "lcp",
        incident_angle: float = 45,
    ) -> None:
        wls_start, wls_end, wls_points = self._set_range(wls_range, e_range)

        self.wls_rangeInst = WaveLengthRange(wls_start, wls_end, wls_points)

        if isinstance(light, str):
            self.light = eval("{}Light()".format(light.upper()))
        elif isinstance(light, Light):
            self.light = light

        incident_theta = incident_angle / 180 * np.pi
        self.theta0 = incident_theta

        ##  Default substrate and out medium refractive index
        self.subObj = MediumObj(
            self.wls_rangeInst.wls_arr, np.array([1] * len(self.wls_rangeInst.wls_arr))
        )
        self.outObj = MediumObj(
            self.wls_rangeInst.wls_arr, np.array([1] * len(self.wls_rangeInst.wls_arr))
        )

    @staticmethod
    def _set_range(wls_range, e_range):
        wls_start = 500
        wls_end = 700
        wls_points = 300
        if wls_range is not None and e_range is None:
            wls_start = wls_range[0]
            wls_end = wls_range[-1]
            wls_points = len(wls_range)
        elif wls_range is None and e_range is not None:
            wls_start = 1240 / e_range[-1] * 1000
            wls_end = 1240 / e_range[0] * 1000
            wls_points = len(e_range)
        return wls_start, wls_end, wls_points

    def load_imported_sub_out_dat(
        self, dat_filename_dict: DatFiles | None = None, dirname="PSHE"
    ):
        if dat_filename_dict is None:
            print(
                "No substrate and out refractive index files found. Using the default refractive index 1 (air)"
            )
            return
        else:
            keys = list(dat_filename_dict.keys())
            if "subFname" in keys and dat_filename_dict["subFname"] is not None:
                freadInst = FilesRead(dirname)
                var_list = freadInst.load(dat_filename_dict["subFname"])
                wls = np.array(var_list[0])
                n = np.array(var_list[1])
                self.subObj = MediumObj(wls, n)
            else:
                print(
                    "No assigned \033[32mSUBSTRATE\033[0m dat file, using default '1' refractive index"
                )
            if "outFname" in keys and dat_filename_dict["outFname"] is not None:
                freadInst = FilesRead(dirname)
                var_list = freadInst.load(dat_filename_dict["outFname"])
                wls = np.array(var_list[0])
                n = np.array(var_list[1])
                self.outObj = MediumObj(wls, n)
            else:
                print(
                    "No assigned \033[32mOUT\033[0m dat file, using default '1' refractive index"
                )

    def _reset_medium(self):
        self.subObj = MediumObj(
            self.wls_rangeInst.wls_arr, np.array([1] * len(self.wls_rangeInst.wls_arr))
        )
        self.outObj = MediumObj(
            self.wls_rangeInst.wls_arr, np.array([1] * len(self.wls_rangeInst.wls_arr))
        )

    def _rs_rp_cal(
        self,
        MatInst: Union[Permittivity, list[Permittivity], ReducedConductivity, None],
        theta_in,
    ):
        if (self.subObj.wls.min() > self.wls_rangeInst.wls_arr.min()) or (
            self.subObj.wls.max() < self.wls_rangeInst.wls_arr.max()
        ):
            raise ValueError(
                f"The wavelength range of substrate refractive index is inside the investigated range. Please reset the investigated range. The minimum: {self.subObj.wls.min()}. The Maximum: {self.subObj.wls.max()}"
            )

        f = FresnelCoeff(
            theta_in,
            Layer(
                0,
                self.wls_rangeInst.wls_arr,
                self.subObj.nfunc(self.wls_rangeInst.wls_arr),
            ),
            Layer(
                0,
                self.wls_rangeInst.wls_arr,
                self.outObj.nfunc(self.wls_rangeInst.wls_arr),
            ),
        )
        r_s, r_p = 1, 1
        if isinstance(MatInst, Permittivity):
            layers = [
                Layer(
                    MatInst.thickness, self.wls_rangeInst.wls_arr, MatInst.RefractiveN
                )
            ]
            r_s = f.thin_film_model(layers, direction="s")
            r_p = f.thin_film_model(layers, direction="p")
        elif isinstance(MatInst, list) and isinstance(MatInst[0], Permittivity):
            layers = [
                Layer(ele.thickness, ele.wls_range, ele.RefractiveN) for ele in MatInst
            ]
            r_s = f.thin_film_model(layers, direction="s")
            r_p = f.thin_film_model(layers, direction="p")
        elif isinstance(MatInst, ReducedConductivity):
            r_s = f.conductivity_model(
                MatInst.nfunc()(self.wls_rangeInst.wls_arr), direction="s"
            )
            r_p = f.conductivity_model(
                MatInst.nfunc()(self.wls_rangeInst.wls_arr), direction="p"
            )
        elif MatInst is None:
            r_s = f.conductivity_model(0, direction="s")
            r_p = f.conductivity_model(0, direction="p")
        return r_s, r_p

    def calculate(
        self,
        MatInst: Union[Permittivity, list[Permittivity], ReducedConductivity, None],
    ) -> ShiftObj:
        r_s, r_p = self._rs_rp_cal(MatInst, theta_in=self.theta0)

        k0 = (
            2
            * np.pi
            * self.subObj.nfunc(self.wls_rangeInst.wls_arr)
            / self.wls_rangeInst.wls_arr
        )

        R_s = np.abs(r_s)  # Amplitude of rs and rp
        R_p = np.abs(r_p)  # Amplitude of rs and rp
        phi_s = np.angle(r_s)  # Angle of rs and rp
        phi_p = np.angle(r_p)  # Angle of rs and rp

        wspInst = WspInst(self.light, R_s, R_p)

        Delta_IF = (
            -1
            / (k0 * np.tan(self.theta0))
            * (
                (wspInst.Wp * self.light.a_s**2 + wspInst.Ws * self.light.a_p**2)
                / (self.light.a_p * self.light.a_s)
                * np.sin(self.light.eta)
                + 2
                * np.sqrt(wspInst.Ws * wspInst.Wp)
                * np.sin(self.light.eta - phi_p + phi_s)
            )
        )
        return IFShift(self.wls_rangeInst.wls_arr, Delta_IF, "IF_shift")

    def relative_shifts(
        self,
        MatInst: Union[Permittivity, list[Permittivity], ReducedConductivity],
    ) -> IFShift:
        r_s, r_p = self._rs_rp_cal(MatInst, theta_in=self.theta0)

        k0 = (
            2
            * np.pi
            * self.subObj.nfunc(self.wls_rangeInst.wls_arr)
            / self.wls_rangeInst.wls_arr
        )

        R_s = np.abs(r_s)  # Amplitude of rs and rp
        R_p = np.abs(r_p)  # Amplitude of rs and rp
        phi_s = np.angle(r_s)  # Angle of rs and rp
        phi_p = np.angle(r_p)  # Angle of rs and rp

        wspInst = WspInst(self.light, R_s, R_p)

        Delta_IF = (
            -1
            / (k0 * np.tan(self.theta0))
            * (
                1
                + np.sqrt(wspInst.Ws * wspInst.Wp)
                / (self.light.a_s * self.light.a_p)
                * np.cos(phi_p + phi_s)
            )
        )
        return IFShift(self.wls_rangeInst.wls_arr, Delta_IF, label="IF")

    def bg_shift(self, medium_name: DatFiles):
        self.load_imported_sub_out_dat(medium_name)
        shift_out = self.calculate(None)
        return shift_out


class GHCalculation(IFCalculation):
    def __init__(
        self,
        wls_range=None,
        e_range=None,
        light: Literal["s", "p"] | Light = "s",
        incident_angle: float = 45,
    ) -> None:
        super().__init__(wls_range, e_range, incident_angle=incident_angle)

        if isinstance(light, str):
            self.light = eval("{}Light()".format(light.upper()))
        elif isinstance(light, Light):
            self.light = light

    @property
    def theta_arr(self):
        delta_theta = 0.2 / 180 * np.pi
        theta_arr = np.linspace(
            self.theta0 - delta_theta, self.theta0 + delta_theta, 50
        )
        return theta_arr

    def calculate(
        self,
        MatInst: Permittivity | list[Permittivity] | ReducedConductivity,
    ) -> ShiftObj:
        r_s0, r_p0 = self._rs_rp_cal(MatInst, theta_in=self.theta0)

        angle_s = []
        angle_p = []

        for ele_theta in self.theta_arr:
            r_s, r_p = self._rs_rp_cal(MatInst, theta_in=ele_theta)

            angle_s.append(np.angle(r_s))
            angle_p.append(np.angle(r_p))

        angle_s = np.array(angle_s)
        angle_p = np.array(angle_p)

        f_s_list: list[Callable] = [
            interpolate.interp1d(
                self.theta_arr[:-1], np.diff(angle_s[:, i]) / np.diff(self.theta_arr)
            )
            for i in range(angle_s.shape[-1])
        ]
        f_p_list: list[Callable] = [
            interpolate.interp1d(
                self.theta_arr[:-1], np.diff(angle_p[:, i]) / np.diff(self.theta_arr)
            )
            for i in range(angle_p.shape[-1])
        ]

        par_phis = np.array([ele_f(self.theta0) for ele_f in f_s_list])
        par_phip = np.array([ele_f(self.theta0) for ele_f in f_p_list])

        R_s = np.abs(r_s0)  # Amplitude of rs and rp
        R_p = np.abs(r_p0)  # Amplitude of rs and rp

        wspInst = WspInst(self.light, R_s, R_p)

        k0 = (
            2
            * np.pi
            * self.subObj.nfunc(self.wls_rangeInst.wls_arr)
            / self.wls_rangeInst.wls_arr
        )

        Delta_GH = 1 / k0 * (wspInst.Ws * par_phis + wspInst.Wp * par_phip)

        return GHShift(self.wls_rangeInst.wls_arr, Delta_GH, label="GH")


class BGIF(IFCalculation):
    def __init__(
        self,
        wls_range=None,
        e_range=None,
        light: Literal["lcp", "rcp"] | Light = "lcp",
        incident_angle: float = 45,
    ) -> None:
        super().__init__(wls_range, e_range, light, incident_angle)
        self.MatInst = MatInst

    @property
    def _bg_mat(self) -> Permittivity | ReducedConductivity:
        mat_in = Permittivity(
            self.wls_rangeInst.wls_arr,
            np.ones((len(self.wls_rangeInst.wls_arr))),
            0,
        )

        if isinstance(self.MatInst, Permittivity):
            mat_in = Permittivity(
                self.wls_rangeInst.wls_arr,
                self.MatInst.perm_infty * np.ones((len(self.wls_rangeInst.wls_arr),)),
                self.MatInst.thickness,
            )
        elif isinstance(self.MatInst, ReducedConductivity):
            mat_in = ReducedConductivity(
                self.wls_rangeInst.wls_arr, np.zeros((len(self.wls_rangeInst.wls_arr),))
            )
        return mat_in

    @property
    def wls(self):
        return self.wls_rangeInst.wls_arr

    @property
    def bg_shift(self) -> IFShift:
        return self.calculate(self._bg_mat)

    @property
    def bg_if_center_y(self):
        return self.bg_shift.center_y

    @property
    def bg_if_kb(self):
        return self.bg_shift.kb


class BGIF(IFCalculation):
    def __init__(
        self,
        MatInst: Permittivity | ReducedConductivity,
        wls_start: float = 500,
        wls_end: float = 700,
        wls_points: float = 300,
        light: Literal["lcp", "rcp"] | Light = "lcp",
        incident_angle: float = 45,
    ) -> None:
        super().__init__(wls_start, wls_end, wls_points, light, incident_angle)
        self.MatInst = MatInst

    @property
    def _bg_mat(self) -> Permittivity | ReducedConductivity:
        mat_in = Permittivity(
            self.wls_rangeInst.wls_arr,
            np.ones((len(self.wls_rangeInst.wls_arr))),
            0,
        )

        if isinstance(self.MatInst, Permittivity):
            mat_in = Permittivity(
                self.wls_rangeInst.wls_arr,
                self.MatInst.perm_infty * np.ones((len(self.wls_rangeInst.wls_arr),)),
                self.MatInst.thickness,
            )
        elif isinstance(self.MatInst, ReducedConductivity):
            mat_in = ReducedConductivity(
                self.wls_rangeInst.wls_arr, np.zeros((len(self.wls_rangeInst.wls_arr),))
            )
        return mat_in

    @property
    def wls(self):
        return self.wls_rangeInst.wls_arr

    @property
    def bg_shift(self) -> IFShift:
        return self.calculate(self._bg_mat)

    @property
    def bg_if_center_y(self):
        return self.bg_shift.center_y

    @property
    def bg_if_kb(self):
        return self.bg_shift.kb


class BGGH(BGIF, GHCalculation):
    def __init__(
        self,
        MatInst: Permittivity | ReducedConductivity,
        wls_start: float = 500,
        wls_end: float = 700,
        wls_points: float = 300,
        light: Literal["lcp", "rcp"] | Light = "lcp",
        incident_angle: float = 45,
    ) -> None:
        super().__init__(MatInst, wls_start, wls_end, wls_points, light, incident_angle)

    @property
    def bg_shift(self) -> GHShift:
        return super(BGIF, self).calculate(self._bg_mat)
