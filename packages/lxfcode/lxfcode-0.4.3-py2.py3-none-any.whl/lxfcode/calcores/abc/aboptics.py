from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..opt_cond import OptCondPlot

from functools import cached_property
from typing import Literal, Union

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from ..filesop.filesave import FilesSave
from ..pubmeth.consts import *
from ..pubmeth.methods import Line, set_e_wls
from ..pubmeth.unit_conversion import wls2omega

__all__ = ["FresnelCoeff", "LorentzParameters", "ReducedConductivity", "Permittivity"]


class Layer:
    def __init__(self, thickness, wls, n) -> None:
        self.d = thickness
        self.wls = wls
        self.n = n


class TransferElement:
    def __init__(self, arr) -> None:
        self.arr = arr

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return TransferElement(self.arr + other.arr)
        elif isinstance(other, (float, int, np.ndarray)):
            return TransferElement(self.arr + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(
        self, factor: Union["TransferElement", float, int, np.ndarray]
    ) -> "TransferElement":
        if isinstance(factor, self.__class__):
            return TransferElement(self.arr * factor.arr)
        elif isinstance(factor, (float, int, np.ndarray)):
            return TransferElement(self.arr * factor)
        return TransferElement(self.arr)

    def __rmul__(self, factor):
        return self.__mul__(factor)

    def __truediv__(self, factor: Union["TransferElement", float, int, np.ndarray]):
        if isinstance(factor, self.__class__):
            return TransferElement(self.arr / factor.arr)
        elif isinstance(factor, (float, int, np.ndarray)):
            return TransferElement(self.arr / factor)

    def __rtruediv__(self, factor: Union["TransferElement", float, int, np.ndarray]):
        if isinstance(factor, self.__class__):
            return TransferElement(factor.arr / self.arr)
        elif isinstance(factor, (float, int, np.ndarray)):
            return TransferElement(factor / self.arr)


class ExpTransferElement(TransferElement):
    def __init__(self, arr) -> None:
        self.arr = np.exp(arr)


class WaveLengthRange:
    """
    Put the wavelength range list or array you investigate into the args parameter.

    Or you can input the start and the end wavelength. The default points over the wavelength range is 300
    """

    def __init__(self, *args, wls_points=300) -> None:
        self._args = args
        if len(args) == 3:
            self._wls_start = args[0]
            self._wls_end = args[1]
            self.wls_points = args[2]
        elif len(args) == 2:
            self._wls_start = args[0]
            self._wls_end = args[1]
            self.wls_points = wls_points
        elif len(args) and isinstance(args[0], (np.ndarray, list)) == 1:
            pass

    @property
    def wls_arr(self) -> np.ndarray:
        if len(self._args) == 3 or len(self._args) == 2:
            return np.linspace(self._wls_start, self._wls_end, self.wls_points)
        elif len(self._args) == 1:
            return np.array(self._args[0])
        return np.linspace(500, 700, self.wls_points)

    @property
    def e_arr(self) -> np.ndarray:  # in meV
        if isinstance(self.wls_arr, np.ndarray):
            return 1240 / self.wls_arr * 1000

        if self.wls_arr is None:
            raise TypeError("wls is None, Please check")
        return 1240 / self.wls_arr * 1000


class Light:
    def __init__(self, a_s: float, a_p: float, eta=0.0) -> None:
        self.a_s = a_s
        self.a_p = a_p
        self.eta = eta


class LCPLight(Light):
    def __init__(self, a_s=1, a_p=1, eta=np.pi / 2) -> None:
        super().__init__(a_s, a_p, eta)


class RCPLight(Light):
    def __init__(self, a_s=1, a_p=1, eta=-np.pi / 2) -> None:
        super().__init__(a_s, a_p, eta)


class SLight(Light):
    def __init__(self, a_s=1, a_p=0, eta=0) -> None:
        super().__init__(a_s, a_p, eta)


class PLight(Light):
    def __init__(self, a_s=0, a_p=1, eta=0) -> None:
        super().__init__(a_s, a_p, eta)


class WspInst:
    def __init__(self, light: Light, R_s, R_p) -> None:
        self.light = light
        self.R_s = R_s
        self.R_p = R_p
        pass

    @property
    def Ws(self):
        return (
            self.R_s**2
            * self.light.a_s**2
            / (self.R_s**2 * self.light.a_s**2 + self.R_p**2 * self.light.a_p**2)
        )

    @property
    def Wp(self):
        return (
            self.R_p**2
            * self.light.a_p**2
            / (self.R_s**2 * self.light.a_s**2 + self.R_p**2 * self.light.a_p**2)
        )


class FresnelCoeff:
    def __init__(self, theta0, Layer1: Layer, Layer2: Layer) -> None:
        self.theta0 = theta0
        self.layer1 = Layer1
        self.layer2 = Layer2
        self.n0_index = Layer1.n
        self.n2_index = Layer2.n
        pass

    @property
    def theta2(self):
        quotient = self.n0_index * np.sin(self.theta0) / self.n2_index + 0j
        result = np.arcsin(quotient)
        result = np.real(result) - 1j * np.abs(np.imag(result))

        return result  # np.arcsin(quotient)

    @property
    def r_s(self):
        # return -np.sin(self.theta0 - self.theta2) / np.sin(self.theta0 + self.theta2)
        return (
            self.n0_index * np.cos(self.theta0) - self.n2_index * np.cos(self.theta2)
        ) / (self.n0_index * np.cos(self.theta0) + self.n2_index * np.cos(self.theta2))

    @property
    def r_p(self):
        # return np.tan(self.theta0 - self.theta2) / np.tan(self.theta0 + self.theta2)
        return (
            self.n2_index * np.cos(self.theta0) - self.n0_index * np.cos(self.theta2)
        ) / (self.n2_index * np.cos(self.theta0) + self.n0_index * np.cos(self.theta2))

    @property
    def t_s(self):
        return (
            2
            * self.n0_index
            * np.cos(self.theta0)
            / (
                self.n0_index * np.cos(self.theta0)
                + self.n2_index * np.cos(self.theta2)
            )
        )

    @property
    def t_p(self):
        return (
            2
            * self.n0_index
            * np.cos(self.theta0)
            / (
                self.n2_index * np.cos(self.theta0)
                + self.n0_index * np.cos(self.theta2)
            )
        )

    @property
    def delta(self):
        delta = (
            2
            * np.pi
            * self.n2_index
            * self.layer2.d
            * np.cos(self.theta2)
            / self.layer2.wls
        )
        return delta

    @property
    def phase_mat(self):
        phase = ExpTransferElement(1j * self.delta)
        phase_c = ExpTransferElement(-1j * self.delta)
        mat = np.array([[phase_c, 0], [0, phase]])
        return mat

    def _bound_mat(self, direction: Literal["s", "p"] = "s"):
        r = getattr(self, "r_{}".format(direction))
        t = getattr(self, "t_{}".format(direction))
        r_ele = TransferElement(r)
        t_ele = TransferElement(t)
        mat = np.array([[1, r_ele], [r_ele, 1]]) / t_ele
        return mat

    def thin_film_model(self, layers: list[Layer], direction: Literal["s", "p"]):
        """
        Layer list should not contain the layers in the init function
        """
        theta = self.theta0

        mat = np.eye(2)

        if isinstance(layers, Layer):
            layerscopy = [self.layer1, layers, self.layer2]
        elif isinstance(layers, list):
            layerscopy = layers[:]
            layerscopy.insert(0, self.layer1)
            layerscopy.append(self.layer2)
        for li in range(len(layerscopy) - 1):
            f = FresnelCoeff(theta, layerscopy[li], layerscopy[li + 1])
            mat = mat @ f._bound_mat(direction) @ f.phase_mat
            theta = f.theta2
        fi_vec = mat @ np.array([1, 0])
        out_r: TransferElement = fi_vec[-1] / fi_vec[0]
        return out_r.arr

    def conductivity_model(
        self, rsigma: "ReducedConductivity|float", direction: Literal["s", "p"] = "s"
    ):
        if direction == "s":
            r = (
                self.n0_index * np.cos(self.theta0)
                - self.n2_index * np.cos(self.theta2)
                - rsigma
            ) / (
                self.n0_index * np.cos(self.theta0)
                + self.n2_index * np.cos(self.theta2)
                + rsigma
            )
        elif direction == "p":
            r = (
                self.n2_index / np.cos(self.theta2)
                - self.n0_index / np.cos(self.theta0)
                + rsigma
            ) / (
                self.n2_index / np.cos(self.theta2)
                + self.n0_index / np.cos(self.theta0)
                + rsigma
            )
        return r


class LorentzParameters:
    """
    Input the 'centers', 'amplitudes', 'broadenings' of different Lorentzian peaks into pars parameter.
    """

    def __init__(
        self,
        e_centers: np.ndarray | list | None = None,
        wls_centers: np.ndarray | list | None = None,
        amplitudes: np.ndarray | list | None = None,
        broadenings: np.ndarray | list | None = None,
        e_range: np.ndarray | None = None,
        wls_range: np.ndarray | None = None,
        renormalized: bool = False,
    ) -> None:
        self.e_centers = set_e_wls(e_centers, wls_centers)
        self.e_range = set_e_wls(e_range, wls_range)
        self.wls_range = 1240 / self.e_range * 1000

        self.amplitudes: np.ndarray = np.array(amplitudes)
        if renormalized:
            self.amplitudes = (
                np.array(amplitudes)
                * np.sqrt(np.array(broadenings) / np.array(self.e_centers))
                * np.array(self.e_centers)
            )

        self.broadenings: np.ndarray = np.array(broadenings)

    @staticmethod
    def _set_args(e_args, wls_args) -> np.ndarray:
        if e_args is None and wls_args is None:
            raise ValueError("You should assign centers of lorentzian peaks.")
        elif e_args is None and wls_args is not None:
            e_args = 1240 / np.array(wls_args) * 1000
        elif e_args is not None and wls_args is None:
            e_args = e_args
        else:
            raise ValueError("Please just set one of e_centers and wls_centers.")
        return e_args

    @property
    def _complex_result(self) -> np.ndarray:
        result = 0
        for i in range(len(self.e_centers)):
            tmp_c = self.e_centers[i]
            tmp_a = self.amplitudes[i]
            tmp_g = self.broadenings[i]
            result += tmp_a**2 / (
                tmp_c**2 - self.e_range**2 - 1j * tmp_g * self.e_range
            )

        return np.array(result)

    @property
    def real_part(self):
        return np.real(self._complex_result)

    @property
    def imag_part(self):
        return np.imag(self._complex_result)

    def plot(self, fname: str = "lo", on_what: Literal["e", "wls"] = "e"):
        fInst = FilesSave("LorentzO")
        comp_result = self._complex_result

        fig, ax = plt.subplots()
        x_range = None
        if on_what == "e":
            x_range = self.e_range
        elif on_what == "wls":
            x_range = self.wls_range
        ax.plot(x_range, np.real(comp_result), label="Real part")
        ax.plot(x_range, np.imag(comp_result), label="Imaginary part")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend()
        ax.set_title("Lorentzian Oscillators")
        fInst.save_fig(fig, fname)
        return comp_result

    def get_components(self) -> np.ndarray:
        result_list = []
        for i in range(len(self.e_centers)):
            tmp_c = self.e_centers[i]
            tmp_a = self.amplitudes[i]
            tmp_g = self.broadenings[i]
            result_list.append(
                tmp_a**2 / (tmp_c**2 - self.e_range**2 - 1j * tmp_g * self.e_range)
            )

        return np.array(result_list)


class LorentzOscillator:
    def __init__(
        self,
        lo_pars: LorentzParameters,
        wlsInst: WaveLengthRange = WaveLengthRange(500, 700),
    ) -> None:
        self.lo_pars = lo_pars
        self.wlsInst = wlsInst

    @cached_property
    def amplitude(self) -> np.ndarray:
        amps = (
            self.lo_pars.amplitudes
            * np.sqrt(self.lo_pars.broadenings / self.lo_pars.e_centers)
            * self.lo_pars.e_centers
        )
        return amps

    @property
    def gamma(self) -> np.ndarray:
        return self.lo_pars.gamma

    @property
    def center(self) -> np.ndarray:
        return self.lo_pars.center

    @property
    def e_x(self) -> np.ndarray:
        return self.wlsInst.e_arr

    @property
    def wls_x(self) -> np.ndarray:
        return self.wlsInst.wls_arr

    @cached_property
    def complex_result(self):
        amp = np.kron(np.ones((1, len(self.e_x))), self.amplitude.reshape(-1, 1))
        gamma = np.kron(np.ones((1, len(self.e_x))), self.gamma.reshape(-1, 1))
        centers = np.kron(np.ones((1, len(self.e_x))), self.center.reshape(-1, 1))
        x = np.kron(np.ones((len(self.amplitude), 1)), self.e_x.reshape(1, -1))
        result = amp**2 / (centers**2 - x**2 - 1j * gamma * x)
        result = np.sum(result, axis=0)
        return result

    @property
    def real_part(self):
        return np.real(self.complex_result)

    @property
    def imag_part(self):
        return np.imag(self.complex_result)

    def plot(self):
        Line([self.e_x] * 2, [self.real_part, self.imag_part]).multiplot(
            "realimag_lorentz", ["Real part", "Imaginary part"], "E (meV)"
        )


class ReducedConductivity:
    def __init__(
        self,
        e_range: np.ndarray | None = None,
        wls_range: np.ndarray | None = None,
        sigma_tilde: np.ndarray | None = None,
        fdirname: str = "Cond",
    ) -> None:
        self.e_range = set_e_wls(e_range, wls_range)
        self.wls_range = 1240 / self.e_range * 1000

        if sigma_tilde is None:
            raise ValueError("Cannot assign None to sigma tilde")

        self.sigma_tilde = sigma_tilde
        self.fInst: FilesSave = FilesSave(fdirname)

    @staticmethod
    def load_from_OptCond(optcond: OptCondPlot) -> "ReducedConductivity":
        complex_cond = optcond.plot(load_from_exist_dat=True)

        tmp_cond = np.sum(complex_cond * np.pi * alpha_fsc, axis=0)

        fig, ax_ab = plt.subplots(figsize=(7, 5))
        (line,) = ax_ab.plot(optcond.OptCondInst.e_range, np.real(tmp_cond))
        ax_ab.set_aspect("auto")
        ax_ab.set_xlabel("E (meV)", fontsize=12)
        ax_ab.set_ylabel(r"$\sigma_{\text{mono}}$", fontsize=12)
        FilesSave("ReCondFromOptCond").save_fig(
            fig,
            f"Cond_real_{optcond.OptCondInst.gamma}",
        )
        line.remove()
        ax_ab.plot(optcond.OptCondInst.e_range, np.imag(tmp_cond))
        FilesSave("ReCondFromOptCond").save_fig(
            fig,
            f"Cond_imag_{optcond.OptCondInst.gamma}",
        )

        plt.close(fig)

        sigma_tilde = complex_cond * np.pi * alpha_fsc
        return ReducedConductivity(
            wls_range=1240 / (optcond.OptCondInst.e_range) * 1000,
            sigma_tilde=np.sum(sigma_tilde, axis=0),
            fdirname="FromOptCond",
        )

    @staticmethod
    def load_from_lorentz_oscillator(lp: "LorentzParameters") -> "ReducedConductivity":
        return ReducedConductivity(
            e_range=lp.e_range, sigma_tilde=lp._complex_result * (-1j)
        )

    @property
    def real_part(self):
        return np.real(self.sigma_tilde)

    @property
    def imag_part(self):
        return np.imag(self.sigma_tilde)

    def plot(
        self, fname: None | str = "realimag_cond", on_what: Literal["wls", "e"] = "wls"
    ):
        if on_what == "wls":
            x = [self.wls_range] * 2
        elif on_what == "e":
            x = [self.e_range] * 2
        Line(
            x,
            [self.real_part, self.imag_part],
            fdirname=self.fInst.dirname,
        ).multiplot(
            fname,
            ["Real part", "Imaginary part"],
            r"$\lambda$ (nm)",
            r"$\tilde{\sigma}$",
        )

    def nfunc(self, kind: Literal["linear", "cubic", "quadratic", "zero"] = "linear"):
        f = interpolate.interp1d(self.wls_range, self.sigma_tilde, kind=kind)
        return f


class Permittivity:
    """
    If you want to construct permittivity through Lorentzian oscillators, use the static method 'LorentzO'.
    """

    def __init__(
        self,
        e_range: np.ndarray | None = None,
        wls_range: np.ndarray | None = None,
        perm: np.ndarray | None = None,
        thickness: float = 1,
        perm_infty: float = 1,
    ) -> None:  #    d in nm
        self.e_range = set_e_wls(e_range, wls_range)
        self.wls_range = 1240 / self.e_range * 1000

        if perm is None:
            raise ValueError("Cannot assign None to sigma tilde")

        self.perm = perm

        self.thickness = thickness
        self.perm_infty: float = perm_infty

    @staticmethod
    def load_from_lorentzOscillators(
        perm_infty: float, lp: LorentzParameters, d: float = 1
    ) -> "Permittivity":
        """
        perm_infty: The high-frequency dielectric constant

        lo: the LorentzOscillator class

        d: the thickness of the material
        """
        permInst = Permittivity(
            wls_range=lp.wls_range,
            perm=perm_infty + lp._complex_result,
            thickness=d,
            perm_infty=perm_infty,
        )
        return permInst

    @property
    def sigma2d(self):
        omega = wls2omega(self.wls_range)
        sigma2d = self.perm * omega * self.thickness / (c_speed * m2nm * 1j)
        return ReducedConductivity(self.wls_range, sigma2d)

    @cached_property
    def RefractiveN(self):
        return np.sqrt(self.perm)

    @property
    def real_part(self):
        return np.real(self.perm)

    @property
    def imag_part(self):
        return np.imag(self.perm)

    def plot_perm(self, perspective: Literal["e", "lambda"] = "e"):
        if perspective == "e":
            x = self.wls_range
        elif perspective == "lambda":
            x = 1240 / self.wls_range * 1000
        Line([x] * 2, [self.real_part, self.imag_part], fdirname="Perm").multiplot(
            "realimag_perm",
            ["Real part", "Imaginary part"],
            r"$\lambda$ (nm)",
            "Permittivity",
        )
        return

    @staticmethod
    def sigma2d_to_perm(perm_infty, cond: ReducedConductivity, thickness):
        omega = wls2omega(cond.wls_range)
        response_term = (
            1j * (cond.sigma_tilde * c_speed * m2nm) / (omega * thickness) + perm_infty
        )

        return Permittivity(
            wls_range=cond.wls_range,
            perm=response_term,
            thickness=thickness,
            perm_infty=perm_infty,
        )

    def plot_n(self):
        Line(
            [self.wls_range] * 2,
            [np.real(self.RefractiveN), np.imag(self.RefractiveN)],
            fdirname="Perm",
        ).multiplot(
            "realimag_n",
            ["Real part", "Imaginary part"],
            r"$\lambda$ (nm)",
            "Refractive index",
        )
        return
