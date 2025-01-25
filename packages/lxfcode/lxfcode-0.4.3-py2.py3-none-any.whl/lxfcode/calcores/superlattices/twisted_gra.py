from typing import Literal, Type

import numpy as np

from ..abc.abmoire import ABContiGraMoires, ABContiMoHa, ABTBMoHa
from ..abc.self_types import Path, SKPars
from ..absorption.absorption_cal import AbsorptionCal
from ..absorption.absorption_plot import AbsorptionPlot
from ..bands.bands_cal import BandsCal
from ..bands.bands_plot import BandsPlot
from ..dos.dos_cal import DosCal
from ..dos.dos_plot import DosPlot
from ..hamiltonians.conti_h import ContiTBGHa, EffABtHa, EffAtAHa, EffAtBHa
from ..hamiltonians.tb_h import (
    TightAAtTTGHa,
    TightABtTTGHa,
    TightAtATTGHa,
    TightAtBTTGHa,
    TightTBGHa,
)
from ..jdos.jdos_cal import JdosCal
from ..jdos.jdos_plot import JdosPlot
from ..opt_cond.optcond_cal import OptCondCal
from ..opt_cond.optcond_plot import OptCondPlot
from ..pubmeth import Line

# import matplotlib.pyplot as plt
from ..pubmeth.consts import *
from ..raman.raman_cal import RamanCal
from ..raman.raman_plot import RamanPlot
from ..superlattices.comm_stru import (
    CommAAtTTGStru,
    CommABtTTGStru,
    CommAtATTGStru,
    CommAtBTTGStru,
    CommTBGStru,
)
from ..superlattices.stru_plot import StruPlot

__all__ = [
    "ContiTBG",
    "EffABt",
    "EffAtA",
    "EffAtB",
    "TightTBG",
    "TightAAtTTG",
    "TightAtATTG",
    "TightABtTTG",
    "TightAtBTTG",
]


class ContiTBG(ABContiGraMoires):
    """

    extra_params:
        w_inter: (default) 118meV. The interlayer hopping for bilayer graphene

    """

    def __init__(
        self,
        twist_angle: float,
        haClassType: Type[ABContiMoHa] = ContiTBGHa,
        vFcoeff: float = 1,
        a0: float = 2.46,
        kshells: int = 7,
        w_inter=118,
        **kwargs,
    ) -> None:
        super().__init__(
            twist_angle, haClassType, vFcoeff, a0, kshells, w_inter, **kwargs
        )
        self.mat_name = "Twisted Bilayer Graphene"

    def eigs_at_points(self, point: Literal["K_t", "K_b", "M", "Gamma"] = "M"):
        h: ABContiMoHa = self.haClassType(self)

        eig_vals = np.linalg.eig(h.h(getattr(h, point)))[0]
        return np.real(eig_vals)

    def bands(
        self,
        path: list[Path] | list[np.ndarray] = ["K_t", "K_b", "Gamma", "M"],
        suffix="",
        ylim=None,
        density=100,
        ticklabelsize=10,
        titlesize=14,
        fontsize=12,
        title_name=None,
        h_pars: SKPars | None = None,
        disable_progress_bar=False,
    ) -> tuple[np.ndarray, list]:
        """
        Return: Energy, label_x
        """
        if title_name is None:
            bds_title = r"Band structures of {:.2f}$\degree$ {}".format(
                self.twist_angle, self.mat_name
            )
        else:
            bds_title = title_name

        ## Set parameters for Hamiltonian
        h: ABContiMoHa = self.haClassType(self)
        if h_pars is None:
            pass
        else:
            for keys, values in h_pars.items():
                setattr(h, keys, values)

        ##  Band calculations and Plot
        bcals = BandsCal(
            h,
            path=path,
            suffix=suffix,
            p_density=density,
            disable_progress_bar=disable_progress_bar,
        )
        bplot = BandsPlot(bcals, titlesize=titlesize, fontsize=fontsize)
        return bplot.plot(
            title_name=bds_title,
            ylim=ylim,
            ticklabelsize=ticklabelsize,
            # xfontsize=xfontsize,
        )

    def raman(
        self,
        density: int = 70,
        calcores: int = 3,
        ffolder: str = "",
        update_eles: bool = False,
        bds_num: int = 5,
        disable_elet: bool = True,
        gamma: float = 100.0,
        plot_over_eop: bool = False,
    ) -> RamanPlot:
        h: ABContiMoHa = self.haClassType(self)
        rcals = RamanCal(
            h, density=density, cal_corenum=calcores, bds_num=bds_num, gamma=gamma
        )
        rplot = RamanPlot(rcals, ffolder=ffolder, disable_elet=disable_elet)

        if plot_over_eop:
            ri_overeop, e_range = rplot.raman_eop_plot()
            ri_overeop_sum = ri_overeop.sum(axis=1).sum(axis=1)
            ri_modules = np.abs(ri_overeop_sum / (density**2 * self.areaM)) ** 2
            Line(
                [e_range] * 2,
                [np.real(ri_overeop_sum), np.imag(ri_overeop_sum)],
                fdirname=rplot.rFileInst.elet_fdir.dirname,
            ).multiplot(
                "realimag_overeop",
                ["real part", "imaginary part"],
                "E (meV)",
                "Raman intensity (a.u.)",
                "Raman over photon energy",
                xlim=[1200, 3000],
            )
            Line(e_range, ri_modules, fdirname=rplot.rFileInst.elet_fdir.dirname).plot(
                "ri_overeop",
                "E (meV)",
                "Raman intensity (a.u.)",
                "Raman over photon energy",
                xlim=[1200, 3000],
            )

        pexisted = rplot.rFileInst.existed()[0]
        if (not pexisted) or update_eles:
            rplot.plot(update_elet=update_eles)
        return rplot

    def jdos(
        self,
        density=70,
        broadening=1,
        vc_num=3,
        calcores=3,
        update_npy=False,
        cal_hint=False,
        e_range=np.linspace(100, 2500, 200),
        large_scal_cal=False,
    ):
        h: ABContiMoHa = self.haClassType(self)

        jcals = JdosCal(
            h,
            density,
            broadening=broadening,
            cal_corenum=calcores,
            vc_num=vc_num,
            cal_hint=cal_hint,
            e_range=e_range,
            large_scale_cal=large_scal_cal,
        )
        jplot = JdosPlot(jcals, update_npy=update_npy)

        jplot.plot()
        return

    def dos(
        self,
        density=70,
        broadening=1,
        calcores=3,
        update_npy=False,
        ffolder="",
        e_range=None,
        wls_range=None,
        large_scal_cal=False,
        save_dos_npy=False,
        spin_degeneracy=2,
        valley_degeneracy=2,
        h_pars: SKPars | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        e_range = self.e_wls_set(e_range, wls_range)

        h: ABContiMoHa = self.haClassType(self)

        if h_pars is None:
            pass
        else:
            for keys, values in h_pars.items():
                setattr(h, keys, values)

        dcals = DosCal(
            h,
            density,
            dos_broadening=broadening,
            cal_corenum=calcores,
            e_range=e_range,
            large_scale_cal=large_scal_cal,
            spin_degeneracy=spin_degeneracy,
            valley_degeneracy=valley_degeneracy,
        )
        dosplot = DosPlot(
            dcals, update_npy=update_npy, dos_save=save_dos_npy, ffolder=ffolder
        )

        return dosplot.plot()

    def absorption(
        self,
        density=70,
        calcores=3,
        e_range=None,
        wls_range=None,
        ffolder="",
        update_fig=False,
        bds_num=5,
        disable_elet=True,
        gamma=100,
        extra_degen=2,
        tight_h_pars: SKPars | None = None,
        upd_vel_files=False,
    ) -> np.ndarray:
        """
        NOTE: spin degeneracy has already been considered in the calculations. Valley degeneracy = 2 for continuum model.

        Args:
            density: density of k points in the Brillouin zone
            calcores: number of cores that participate in parallel calculations
            e_range: the range of photon energy
            ffolder: father folder to save the generated data files
            update_fig: update absorption figures
            bds_num: bands number involved in the absorption calculations. Starting from the charge neutral point
            disable_elet: disable the element figures generation
            gamma: broadening of the absorption calculations
            valley_degeneracy: the valley degeneracy to distinguish continuum and tight-binding model
            update_npy: update the .npy files saved in the data directory when changing the photon range
            h_pars: parameters to adjust the tight-binding output

        Returns:

        """
        e_range = self.e_wls_set(e_range, wls_range)

        h: ABContiMoHa = self.haClassType(self)
        if tight_h_pars is None:
            pass
        else:
            for keys, values in tight_h_pars.items():
                setattr(h, keys, values)

        abcals = AbsorptionCal(
            h,
            density=density,
            cal_corenum=calcores,
            bds_num=bds_num,
            gamma=gamma,
            degeneracy_factor=extra_degen,
            e_range=e_range,
            upd_vel_files=upd_vel_files,
        )
        abplot = AbsorptionPlot(abcals, ffolder, disable_elet=disable_elet)

        # print("All transitions information existed...")

        return abplot.plot(update_elet=update_fig)

    @staticmethod
    def e_wls_set(e_range, wls_range):
        if e_range is None and wls_range is None:
            e_range = np.linspace(1000, 4000, 400)
            return e_range
        elif e_range is not None and wls_range is None:
            e_range = e_range
            return e_range
        elif wls_range is not None and e_range is None:
            e_range = 1240 / wls_range * 1000
            return e_range
        else:
            raise NotImplementedError(
                "E range and wavelength range cannot be assigned simultaneously. Assign \033[31mONLY ONE\033[0m of them"
            )

    def opt_cond(
        self,
        density: int = 70,
        calcores: int = 3,
        e_range: None | np.ndarray = None,
        wls_range: None | np.ndarray = None,
        ffolder: str = "",
        plot_eles: bool = False,
        bds_num: int = 5,
        disable_elet: bool = True,
        gamma: float = 100,
        extra_degen: float = 2,
        tight_h_pars: SKPars | None = None,
        check_bds_upd: bool = False,
        upd_vel_files: bool = False,
        return_arr: bool = False,
        uniform_cbar_for_ele_e_component: bool = True,
        plot_ele_trans: bool = False,
        cv_pairs=None,
    ) -> OptCondPlot:
        """Optical conductivity calculations

        Args:
            density: [density of the k points in BZ. Total # of points: density^2]
            calcores: [# of CPU cores to do the calculations]
            e_range: [range of photon energy]
            wls_range: [range of wavelength energy. Only set one of e_range and wls_range]
            ffolder: [Use a father folder to contain all the results if you want]
            update_eles: [Update element transitions or not? This could take much time to save the figures]
            update_npy: [upate the npy file or not? Generally, if you changed the gamma, e_range or wls_range, you should update the npy file]
            bds_num: [bands you take into account for the transitions]
            disable_elet: [disable the element transitions plot. False in default]
            gamma: [Broadening of the transitions]
            extra_degen: [degeneracy of the absorption]
            tight_h_pars: [parameters of Slater-Koster interaction for tight-binding model]

        Returns:
            [OptCondPlot class]
        """
        e_range = self.e_wls_set(e_range, wls_range)

        h: ABContiMoHa = self.haClassType(self)

        if tight_h_pars is None:
            pass
        else:
            for keys, values in tight_h_pars.items():
                if not hasattr(h, keys):
                    raise AttributeError(
                        f"No attribute named '{keys}' in: ", h.__class__.__name__
                    )

                setattr(h, keys, values)

        cond_cals = OptCondCal(
            h,
            density=density,
            cal_corenum=calcores,
            bds_num=bds_num,
            gamma=gamma,
            degeneracy_factor=extra_degen,
            e_range=e_range,
            upd_vel_files=upd_vel_files,
        )
        cond_plot = OptCondPlot(cond_cals, ffolder, disable_elet=disable_elet)

        if return_arr:
            return cond_plot.plot(
                plot_eles=plot_eles,
                check_bds_upd=check_bds_upd,
                uniform_cbar_for_ele_e_component=uniform_cbar_for_ele_e_component,
                plot_ele_trans=plot_ele_trans,
                cv_pairs=cv_pairs,
            )

        cond_plot.plot(
            plot_eles=plot_eles,
            check_bds_upd=check_bds_upd,
            uniform_cbar_for_ele_e_component=uniform_cbar_for_ele_e_component,
            plot_ele_trans=plot_ele_trans,
            cv_pairs=cv_pairs,
        )

        return cond_plot


class EffABt(ContiTBG):
    def __init__(
        self,
        twist_angle: float,
        haClassType: Type[ABContiMoHa] = EffABtHa,
        vFcoeff: float = 1,
        a0: float = 2.46,
        kshells: int = 7,
        w_inter=118,
        tperp_coeff: float = 1.0,
    ) -> None:
        super().__init__(
            twist_angle,
            haClassType,
            vFcoeff,
            a0,
            kshells,
            w_inter=w_inter,
            tperp_coeff=tperp_coeff,
        )

        self.mat_name = "ABt-Twisted Trilayer Graphene"


class EffAtA(ContiTBG):
    def __init__(
        self,
        twist_angle: float,
        haClassType: Type[ABContiMoHa] = EffAtAHa,
        vFcoeff: float = 1,
        a0: float = 2.46,
        kshells: int = 7,
        tperp_coeff=1,
    ) -> None:
        super().__init__(
            twist_angle, haClassType, vFcoeff, a0, kshells, tperp_coeff=tperp_coeff
        )

        self.mat_name = "AtA-Twisted Trilayer Graphene"


class EffAtB(ContiTBG):
    def __init__(
        self,
        twist_angle: float,
        haClassType: Type[ABContiMoHa] = EffAtBHa,
        vFcoeff: float = 1,
        a0: float = 2.46,
        kshells: int = 7,
        w_inter=118,
        tperp_coeff=1,
    ) -> None:
        super().__init__(twist_angle, haClassType, vFcoeff, a0, kshells, w_inter)
        self.tperp_coeff = tperp_coeff

        self.mat_name = "AtB-Twisted Trilayer Graphene"


class TightTBG(CommTBGStru, ContiTBG):
    def __init__(
        self,
        m0: int,
        r: int,
        haClassType: Type[ABTBMoHa] = TightTBGHa,
        a1: np.ndarray = np.array([np.sqrt(3) / 2, -1 / 2]),
        a2: np.ndarray = np.array([np.sqrt(3) / 2, 1 / 2]),
        a0: float = 2.46,
        **kwargs,
    ) -> None:
        super().__init__(m0, r, haClassType, a1, a2, a0, **kwargs)

        self.mat_name = "Twisted Bilayer Graphene"

    def structure(self, expand_times=0, noplot=False, plot_contizone=False):
        h: TightTBGHa = self.haClassType(self)
        print("Signatures: ", h.sigs)
        strup = StruPlot(h.moInst)
        if noplot:
            out = strup.vecs(expand_times)
        else:
            out = strup.plot_stru(
                expand_times=expand_times, plot_contizone=plot_contizone
            )
        return out

    def absorption(
        self,
        density=70,
        calcores=3,
        e_range=None,
        wls_range=None,
        ffolder="",
        update_fig=False,
        bds_num=5,
        disable_elet=True,
        gamma=100,
        extra_degen=1,
        tight_h_pars: SKPars | None = None,
    ):
        return super().absorption(
            density,
            calcores,
            e_range,
            wls_range,
            ffolder,
            update_fig,
            bds_num,
            disable_elet,
            gamma,
            extra_degen,
            tight_h_pars,
        )

    def opt_cond(
        self,
        density: int = 70,
        calcores: int = 3,
        e_range: None | np.ndarray = None,
        wls_range: None | np.ndarray = None,
        ffolder: str = "",
        plot_eles: bool = False,
        bds_num: int = 5,
        disable_elet: bool = True,
        gamma: float = 100,
        extra_degen: float = 1,
        tight_h_pars: SKPars | None = None,
        check_bds_upd: bool = False,
        upd_vel_files: bool = False,
        return_arr: bool = False,
        uniform_cbar_for_ele_e_component: bool = True,
        plot_trans: bool = False,
        cv_pairs=None,
    ) -> OptCondPlot:
        return super().opt_cond(
            density,
            calcores,
            e_range,
            wls_range,
            ffolder,
            plot_eles,
            bds_num,
            disable_elet,
            gamma,
            extra_degen,
            tight_h_pars,
            check_bds_upd,
            upd_vel_files,
            return_arr,
            uniform_cbar_for_ele_e_component,
            plot_trans,
            cv_pairs,
        )


class TightAAtTTG(TightTBG, CommAAtTTGStru):
    def __init__(
        self,
        m0: int,
        r: int,
        haClassType: Type[ABTBMoHa] = TightAAtTTGHa,
        a1: np.ndarray = np.array([np.sqrt(3) / 2, -1 / 2]),
        a2: np.ndarray = np.array([np.sqrt(3) / 2, 1 / 2]),
        a0: float = 2.46,
    ) -> None:
        super().__init__(m0, r, haClassType, a1, a2, a0)
        self.mat_name = "AAt-TTG"


class TightAtATTG(TightTBG, CommAtATTGStru):
    def __init__(
        self,
        m0: int,
        r: int,
        haClassType: Type[ABTBMoHa] = TightAtATTGHa,
        a1: np.ndarray = np.array([np.sqrt(3) / 2, -1 / 2]),
        a2: np.ndarray = np.array([np.sqrt(3) / 2, 1 / 2]),
        a0: float = 2.46,
    ) -> None:
        super().__init__(m0, r, haClassType, a1, a2, a0)
        self.mat_name = "AtA-TTG"


class TightABtTTG(TightAAtTTG, CommABtTTGStru):
    def __init__(
        self,
        m0: int,
        r: int,
        haClassType: Type[ABTBMoHa] = TightABtTTGHa,
        a1: np.ndarray = np.array([np.sqrt(3) / 2, -1 / 2]),
        a2: np.ndarray = np.array([np.sqrt(3) / 2, 1 / 2]),
        a0: float = 2.46,
    ) -> None:
        super().__init__(m0, r, haClassType, a1, a2, a0)
        self.mat_name = "ABt-TTG"


class TightAtBTTG(TightTBG, CommAtBTTGStru):
    def __init__(
        self,
        m0: int,
        r: int,
        haClassType: Type[ABTBMoHa] = TightAtBTTGHa,
        a1: np.ndarray = np.array([np.sqrt(3) / 2, -1 / 2]),
        a2: np.ndarray = np.array([np.sqrt(3) / 2, 1 / 2]),
        a0: float = 2.46,
    ) -> None:
        super().__init__(m0, r, haClassType, a1, a2, a0)
        self.mat_name = "AtB-TTG"
