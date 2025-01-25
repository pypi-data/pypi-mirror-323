from typing import Callable, Literal, Union

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from ..abc.aboptics import (
    ExpTransferElement,
    FresnelCoeff,
    Layer,
    LCPLight,
    Light,
    LorentzOscillator,
    LorentzParameters,
    Permittivity,
    PLight,
    RCPLight,
    ReducedConductivity,
    SLight,
    TransferElement,
    WaveLengthRange,
    WspInst,
)
from ..abc.abpshe import MediumObj, OutDat
from ..abc.self_types import DatFiles
from ..filesop.fileread import FilesRead
from ..pubmeth import Line

__all__ = ["IFShift", "GHShift", "IFCalculation", "GHCalculation", "BGIF", "BGGH"]


class ShiftObj:
    def __init__(
        self,
        wls: np.ndarray | None = None,
        shift: np.ndarray | None = None,
        label: str | None = None,
    ) -> None:
        if wls is None or shift is None:
            raise ValueError("Wavelength and shift should be initialized.")

        self.wls = wls
        self.shift: np.ndarray = np.array(shift)

        self.label = label

    def __neg__(self) -> "ShiftObj":
        return ShiftObj(self.wls, -self.shift, "NegShift")

    def __repr__(self) -> str:
        print("Printing the shift of a ShiftObj")
        return np.array2string(self.shift)

    def __add__(self, shift2: Union["ShiftObj", float, int, np.ndarray]) -> "ShiftObj":
        if isinstance(shift2, ShiftObj):
            shift_x = shift2.shift
        else:
            shift_x = shift2
        return ShiftObj(self.wls, self.shift + shift_x, "PlusedShift")

    def __radd__(self, shift2: Union["ShiftObj", float, int, np.ndarray]) -> "ShiftObj":
        return self.__add__(shift2)

    def __sub__(self, shift2: Union["ShiftObj", float, int, np.ndarray]) -> "ShiftObj":
        if isinstance(shift2, ShiftObj):
            shift_x = shift2.shift
        else:
            shift_x = shift2
        return ShiftObj(self.wls, self.shift - shift_x, "DiffLight")

    def __rsub__(self, shift2: Union["ShiftObj", float, int, np.ndarray]) -> "ShiftObj":
        if isinstance(shift2, ShiftObj):
            shift_x = shift2.shift
        else:
            shift_x = shift2
        return ShiftObj(self.wls, shift_x - self.shift, "DiffScalar")

    def __len__(self):
        return len(self.shift)

    def plot(
        self,
        fname: str,
        title: str = "Shift",
        xlim: list[float] | None = None,
        xlabel: str = r"$\lambda$ (nm)",
        ylabel: str = r"Shift",
    ):
        if xlim is None:
            tmp_wls = self.wls
            tmp_shift = self.shift
        else:
            tmp_wls = self.wls[np.logical_and(self.wls > xlim[0], self.wls < xlim[1])]
            tmp_shift = self.shift[
                np.logical_and(self.wls > xlim[0], self.wls < xlim[1])
            ]
        Line(tmp_wls, tmp_shift, fdirname="PSHE/Shifts").plot(
            fname,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            xlim=xlim,
        )

    @property
    def center_y(self) -> float | int:
        return Line(self.wls, self.shift).center_of_curve()[1]

    @property
    def kb(self):
        return Line(self.wls, self.shift).kb_of_curve()


class IFShift(ShiftObj):
    def __init__(
        self,
        wls: np.ndarray | None = None,
        shift: np.ndarray | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(wls, shift, label)

    def plot(
        self, fname: str, title: str = "IF Shift", xlim: list[float] | None = None
    ):
        return super().plot(fname, title, xlim)


class GHShift(ShiftObj):
    def __init__(
        self,
        wls: np.ndarray | None = None,
        shift: np.ndarray | None = None,
        label: str | None = None,
    ) -> None:
        super().__init__(wls, shift, label)

    def plot(
        self, fname: str, title: str = "GH Shift", xlim: list[float] | None = None
    ):
        return super().plot(fname, title, xlim)


class IFCalculation:
    def __init__(
        self,
        e_range=None,
        wls_range=None,
        light: Literal["lcp", "rcp"] | Light = "lcp",
        incident_angle: float = 45,
    ) -> None:
        self.wls_range = self._set_range(e_range, wls_range)

        if isinstance(light, str):
            self.light = eval("{}Light()".format(light.upper()))
        elif isinstance(light, Light):
            self.light = light

        self.incident_angle = incident_angle

        ##  Default substrate and out medium refractive index
        self.subObj = MediumObj(self.wls_range, np.array([1] * len(self.wls_range)))
        self.outObj = MediumObj(self.wls_range, np.array([1] * len(self.wls_range)))

    @property
    def theta0(self):
        incident_theta = self.incident_angle / 180 * np.pi
        return incident_theta

    @staticmethod
    def _set_range(e_range, wls_range) -> np.ndarray:
        if wls_range is None and e_range is None:
            raise ValueError("Wavelength range and energy range cannot be both None.")
        elif wls_range is not None and e_range is None:
            return wls_range
        elif wls_range is None and e_range is not None:
            wls_range = 1240 / e_range * 1000
        return wls_range

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
                tmp_dat = dat_filename_dict["subFname"]
                wls = self.wls_range
                n = self.subObj.n
                if isinstance(tmp_dat, (float, int)):
                    print(f"Setting constant refractive index n: {tmp_dat}")
                    n = np.array([tmp_dat] * len(wls))
                elif isinstance(tmp_dat, (list, np.ndarray)):
                    if len(tmp_dat) == len(wls):
                        print(f"Setting array refractive index n: {tmp_dat}")
                        n = tmp_dat
                    else:
                        raise TypeError(
                            "Please Check whether the length of refractive index and the length of the wavelength is equal"
                        )
                elif isinstance(tmp_dat, str):
                    var_list = freadInst.load(tmp_dat)
                    wls = np.array(var_list[0])
                    n = np.array(var_list[1])
                self.subObj = MediumObj(wls, n)
            else:
                print(
                    "No assigned \033[32mSUBSTRATE\033[0m dat file, using default '1' refractive index"
                )
            if "outFname" in keys and dat_filename_dict["outFname"] is not None:
                freadInst = FilesRead(dirname)
                tmp_dat = dat_filename_dict["outFname"]
                wls = self.wls_range
                n = self.outObj.n
                if isinstance(tmp_dat, (float, int)):
                    print(f"Setting constant refractive index n: {tmp_dat}")
                    n = np.array([tmp_dat] * len(wls))
                elif isinstance(tmp_dat, (list, np.ndarray)):
                    if len(tmp_dat) == len(wls):
                        print(f"Setting array refractive index n: {tmp_dat}")
                        n = tmp_dat
                    else:
                        raise TypeError(
                            "Please Check whether the length of refractive index and the length of the wavelength is equal"
                        )
                elif isinstance(tmp_dat, str):
                    var_list = freadInst.load(tmp_dat)
                    wls = np.array(var_list[0])
                    n = np.array(var_list[1])
                self.outObj = MediumObj(wls, n)
            else:
                print(
                    "No assigned \033[32mOUT\033[0m dat file, using default '1' refractive index"
                )

    def _rs_rp_cal(
        self,
        MatInst: Union[Permittivity, list[Permittivity], ReducedConductivity],
        theta_in,
    ):
        if (self.subObj.wls.min() > self.wls_range.min()) or (
            self.subObj.wls.max() < self.wls_range.max()
        ):
            raise ValueError(
                f"The wavelength range of substrate refractive index is inside the investigated range. Please reset the investigated range. The minimum: {self.subObj.wls.min()}. The Maximum: {self.subObj.wls.max()}"
            )

        f = FresnelCoeff(
            theta_in,
            Layer(
                0,
                self.wls_range,
                self.subObj.nfunc(self.wls_range),
            ),
            Layer(
                0,
                self.wls_range,
                self.outObj.nfunc(self.wls_range),
            ),
        )
        r_s, r_p = 1, 1
        if isinstance(MatInst, Permittivity):
            layers = [Layer(MatInst.thickness, self.wls_range, MatInst.RefractiveN)]
            r_s = f.thin_film_model(layers, direction="s")
            r_p = f.thin_film_model(layers, direction="p")
        elif isinstance(MatInst, list) and isinstance(MatInst[0], Permittivity):
            layers = [
                Layer(ele.thickness, ele.wls_range, ele.RefractiveN) for ele in MatInst
            ]
            r_s = f.thin_film_model(layers, direction="s")
            r_p = f.thin_film_model(layers, direction="p")
        elif isinstance(MatInst, ReducedConductivity):
            r_s = f.conductivity_model(MatInst.nfunc()(self.wls_range), direction="s")
            r_p = f.conductivity_model(MatInst.nfunc()(self.wls_range), direction="p")
        return r_s, r_p

    def calculate(
        self,
        MatInst: Union[Permittivity, list[Permittivity], ReducedConductivity],
    ) -> ShiftObj:
        r_s, r_p = self._rs_rp_cal(MatInst, theta_in=self.theta0)

        k0 = 2 * np.pi * self.subObj.nfunc(self.wls_range) / self.wls_range

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
        return IFShift(self.wls_range, Delta_IF, label="IF")

    def relative_shifts(
        self,
        MatInst: Union[Permittivity, list[Permittivity], ReducedConductivity],
    ) -> IFShift:
        r_s, r_p = self._rs_rp_cal(MatInst, theta_in=self.theta0)

        k0 = 2 * np.pi * self.subObj.nfunc(self.wls_range) / self.wls_range

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
        return IFShift(self.wls_range, Delta_IF, label="IF")


class GHCalculation(IFCalculation):
    def __init__(
        self,
        e_range=None,
        wls_range=None,
        light: Literal["s", "p"] | Light = "s",
        incident_angle: float = 45,
    ) -> None:
        super().__init__(e_range, wls_range, incident_angle=incident_angle)

        if isinstance(light, str):
            self.light = eval("{}Light()".format(light.upper()))
        elif isinstance(light, Light):
            self.light = light

    @property
    def theta_arr(self):
        delta_theta = 0.1 / 180 * np.pi
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

        k0 = 2 * np.pi * self.subObj.nfunc(self.wls_range) / self.wls_range

        Delta_GH = 1 / k0 * (wspInst.Ws * par_phis + wspInst.Wp * par_phip)

        return GHShift(self.wls_range, Delta_GH, label="GH")


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
            self.wls_range,
            np.ones((len(self.wls_range))),
            0,
        )

        if isinstance(self.MatInst, Permittivity):
            mat_in = Permittivity(
                self.wls_range,
                self.MatInst.perm_infty * np.ones((len(self.wls_range),)),
                self.MatInst.thickness,
            )
        elif isinstance(self.MatInst, ReducedConductivity):
            mat_in = ReducedConductivity(
                self.wls_range, np.zeros((len(self.wls_range),))
            )
        return mat_in

    @property
    def wls(self):
        return self.wls_range

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
