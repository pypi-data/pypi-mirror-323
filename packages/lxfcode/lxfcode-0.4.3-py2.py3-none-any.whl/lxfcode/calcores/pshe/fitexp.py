import os
import pickle
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from ..abc.aboptics import (
    LorentzOscillator,
    LorentzParameters,
    Permittivity,
    ReducedConductivity,
    WaveLengthRange,
)
from ..abc.abpshe import (
    ExpDat,
    ExpGHShiftEle,
    ExpIFShiftEle,
    OutDat,
    SubDat,
)
from ..abc.self_types import DatFiles
from ..filesop import FilesRead
from ..filesop.filesave import FilesSave
from ..pshe.shift import (
    BGGH,
    BGIF,
    GHCalculation,
    GHShift,
    IFCalculation,
    IFShift,
    ShiftObj,
)
from ..pubmeth.methods import MultiLines

__all__ = ["LorentzFitExp", "LorentzFitExpShift"]


class LorentzFitExpShift:
    """ """

    def __init__(
        self,
        mediaFileName: DatFiles,
        expFileName: str | None = None,
        expFileSheetI: int = 0,
    ) -> None:
        self.mediaDat = mediaFileName
        self.expVars = FilesRead().load(expFileName, expFileSheetI)

    def plot_exp(self, fname="ExpShiftCollection", ylabel="Shift (nm)", legs_list=None):
        x = self.expVars[0]

        vars = self.expVars[1:]

        x_arr = [x] * len(vars)

        mlInst = MultiLines(x_arr, vars, fdirname="ExpShift")

        mlInst.plot_y_shifted_collections(
            fname=fname, xlabel=r"$\lambda$ (nm)", ylabel=ylabel, legs_list=legs_list
        )

    def _save_pkl_file(self, lpInst: LorentzParameters):
        pkl_dir = "pkl_file/"
        if not os.path.exists(pkl_dir):
            os.makedirs(pkl_dir)

        lpFileName = input(
            "\033[32mPlease give a name to save the npy file for this Lorentzian peak setting: \n\033[0m"
        )

        lpInst.plot(fname=lpFileName)

        pklFile = pickle.dumps(lpInst)

        with open(pkl_dir + lpFileName + ".pkl", "wb") as p:
            p.write(pklFile)

    def _read_pkl_file(self, lpFileName):
        pkl_dir = "pkl_file/"

        with open(f"{pkl_dir}{lpFileName}.pkl", "rb") as f:
            lpInst: LorentzParameters = pickle.load(f)

        return lpInst

    def _mod_pars(self, lpInst: LorentzParameters, lpFileName):
        def ele_mod(
            lpInst: LorentzParameters, attribute_name: str, par_i: int, par_value: float
        ):
            attr = getattr(lpInst, attribute_name)
            attr[par_i - 1] = par_value
            setattr(lpInst, attribute_name, attr)

        def case_judge(lpInst: LorentzParameters, par_type):
            match par_type:
                case "c":
                    par_type = "e_centers"
                case "a":
                    par_type = "amplitudes"
                case "b":
                    par_type = "broadenings"
            print(f"For now the {par_type} are: ", getattr(lpInst, par_type), "\n")

            flag = "y"
            while flag == "y":
                par_i = input(
                    "Choose the position of parameter you want to modify: (start from 1)\n"
                )
                par_i = int(par_i)
                par_value = input("Input value:\n")
                par_value = float(par_value)

                ele_mod(lpInst, "e_centers", par_i, par_value)
                flag = input(f"Continue to mod {par_type}? (y/n)")

        file_changed = False
        mod_or_not = input(
            "\033[32mDo you want to modify any parameters in the existing file? (y/n)\033[0m\n"
        )

        if mod_or_not == "y":
            file_changed = True
        while mod_or_not == "y":
            mod_type = input(
                "\033[32mWhich kind of parameters do you want to modify? ([c]enters/[a]mplitudes/[b]roadenings)\n\033[0m"
            )
            case_judge(lpInst, mod_type)
            mod_or_not = input(
                "\033[32mAny other parameters want to modify? (y/n)\033[0m\n"
            )

        if file_changed:
            save_or_not = input(
                "Parameters changed, do you want to save a new file? (y/n)\n"
            )
            if save_or_not == "y":
                self._save_pkl_file(lpInst)
        else:
            print("Nothing changed, return the original Lorentzian setting")

        lpInst.plot(lpFileName + "_mod")

        return lpInst

    def preset_Lorentz_peaks(
        self,
        check_existing_file=True,
        x_type=None,
        putin_type=None,
        centers_in=None,
        amplitudes_in=None,
        broadenings_in=None,
        lpFileName=None,
        mod_pars_interact=False,
        **args,
    ):
        pkl_dir = "pkl_file/"
        if not os.path.exists(pkl_dir):
            os.makedirs(pkl_dir)

        def inner_check(lpFileName=None, choice=None, **args):
            any_to_load = "y"
            if any_to_load == "y":
                if lpFileName is None:
                    lpFileName = input(
                        '\033[32mLoad Filename (without .pkl): (enter "n" to input new Lorentzian Oscillators parameters) \033[0m\n'
                    )
                if lpFileName == "n":
                    return self.preset_Lorentz_peaks(
                        check_existing_file=False, x_type=x_type, **args
                    )

                if os.path.exists(f"{pkl_dir}{lpFileName}.pkl"):
                    print("Data exist, loading...")

                else:
                    if choice is None:
                        choice = input(
                            "\033[31mNo such file.\033[0m \033[32mDo you want to reinput the file name or directly input new Lorentzian peak parameters? ([r]einput/[n]ewinput)\033[0m\n"
                        )
                    if choice == "r":
                        return self.preset_Lorentz_peaks(x_type=x_type, **args)
                    elif choice == "n":
                        return self.preset_Lorentz_peaks(
                            check_existing_file=False, x_type=x_type, **args
                        )

                with open(f"{pkl_dir}{lpFileName}.pkl", "rb") as f:
                    lpInst: LorentzParameters = pickle.load(f)

                if mod_pars_interact:
                    return self._mod_pars(lpInst, lpFileName)

                lpInst.plot(lpFileName)
                print("Loading Lorentzian peaks combinations complete. Parameters are:")
                print([lpInst.e_centers, lpInst.amplitudes, lpInst.broadenings])
                return lpInst
            elif any_to_load == "n":
                print("\033[32mInputting new Lorentzian peaks!\033[0m\n")
                return self.preset_Lorentz_peaks(
                    check_existing_file=False, x_type=x_type, **args
                )

        if check_existing_file:
            return inner_check(lpFileName=lpFileName)

        x = np.array(self.expVars[0])

        if x_type is None:
            x_type: Literal["wls", "e"] = input(
                "\033[32mWhat is the type of your x variable? (wls/e)\033[0m\n"
            )
        if putin_type is None:
            putin_type: Literal["wls", "e"] = input(
                "\033[32mWhich type of Lorentzian peaks centers do you want to input? (wls/e)\n\033[0m"
            )
        if putin_type != "wls" and putin_type != "e":
            raise TypeError(
                "\033[31mYou should choose one kind of Lorentzian peak x type\033[0m"
            )

        if centers_in is None:
            centers_in = input(
                f"\033[32mPlease enter a list of CENTERS of peaks you want to put: (separated by comma, in {putin_type} unit)\n\033[0m"
            )
        if amplitudes_in is None:
            amplitudes_in = input(
                "\033[32mPlease enter a list of AMPLITUDES of peaks you want to put: (separated by comma, the amplitude will be renormalized)\n\033[0m"
            )
        if broadenings_in is None:
            broadenings_in = input(
                "\033[32mPlease enter a list of BROADENINGS of peaks you want to put: (separated by comma, in meV unit)\n\033[0m"
            )

        center_list = [float(ele_x) for ele_x in centers_in.split(",")]
        amplitude_list = [float(ele_x) for ele_x in amplitudes_in.split(",")]
        broadenings_list = [float(ele_x) for ele_x in broadenings_in.split(",")]
        print(
            "Parameters you put in: \n",
            center_list,
            "\n",
            amplitude_list,
            "\n",
            broadenings_list,
            "\n",
        )

        if len(center_list) != len(amplitude_list) or len(center_list) != len(
            broadenings_list
        ):
            raise TypeError("Lengths of different list don't consist!")

        lpInst = None
        if x_type == "wls":
            if putin_type == "wls":
                lpInst = LorentzParameters(
                    wls_centers=center_list,
                    amplitudes=amplitude_list,
                    broadenings=broadenings_list,
                    wls_range=np.linspace(x[0], x[-1], 300),
                    renormalized=True,
                )
            elif putin_type == "e":
                lpInst = LorentzParameters(
                    e_centers=center_list,
                    amplitudes=amplitude_list,
                    broadenings=broadenings_list,
                    wls_range=np.linspace(x[0], x[-1], 300),
                    renormalized=True,
                )
        elif x_type == "e":
            if putin_type == "wls":
                lpInst = LorentzParameters(
                    wls_centers=center_list,
                    amplitudes=amplitude_list,
                    broadenings=broadenings_list,
                    e_range=np.linspace(x[0], x[-1], 300),
                    renormalized=True,
                )
            elif putin_type == "e":
                lpInst = LorentzParameters(
                    e_centers=center_list,
                    amplitudes=amplitude_list,
                    broadenings=broadenings_list,
                    e_range=np.linspace(x[0], x[-1], 300),
                    renormalized=True,
                )

        lpInst: LorentzParameters

        if lpFileName is None:
            lpFileName = input(
                "\033[32mPlease give a name to save the npy file for this Lorentzian peak setting: \n\033[0m"
            )

        lpInst.plot(fname=lpFileName)

        pklFile = pickle.dumps(lpInst)

        with open(pkl_dir + lpFileName + ".pkl", "wb") as p:
            p.write(pklFile)

        return lpInst

    def _eleshift_cal(
        self, calObjInst: Permittivity | ReducedConductivity, shift_type=None, **args
    ):
        def gh_or_if_cal(
            shift_type: Literal["g", "i"],
            single_or_diff=None,
            incident_angle=None,
            light_polar_type=None,
            diff_type=None,
            **args,
        ):
            if single_or_diff is None:
                single_or_diff: Literal["s", "d"] = input(
                    "\033[32mSingle polarization shift or delta shift? ([s]ingle/[d]elta)\033[0m\n"
                )
            if incident_angle is None:
                incident_angle = input(
                    "\033[32mWhat is the incident angle? (in degree unit)\033[0m\n"
                )
            incident_angle = float(incident_angle)

            if single_or_diff == "s":
                if shift_type == "i":
                    if light_polar_type is None:
                        light_polar_type = input(
                            "\033[32mWhat polarization of the light? ([l]cp/[r]cp)\033[0m"
                        )
                    light_polar_type: Literal["lcp", "rcp"] = light_polar_type + "cp"
                    cal_type = IFCalculation
                elif shift_type == "g":
                    if light_polar_type is None:
                        light_polar_type = input(
                            "\033[32mWhat polarization of the light? ([s]/[p])\033[0m"
                        )
                    light_polar_type = light_polar_type
                    cal_type = GHCalculation

                calInst = cal_type(
                    e_range=calObjInst.e_range,
                    light=light_polar_type,
                    incident_angle=incident_angle,
                )

                calInst.load_imported_sub_out_dat(self.mediaDat)

                shiftInst = calInst.calculate(calObjInst)
                shiftInst.plot(
                    f"{shift_type}_single_{light_polar_type}",
                    title=light_polar_type.upper(),
                )
                return shiftInst
            elif single_or_diff == "d":
                if shift_type == "i":
                    if diff_type is None:
                        diff_type: Literal[1, 2] = input(
                            "\033[32m[1]lcp-rcp or [2]rcp-lcp?\033[0m\n"
                        )
                    diff_type = int(diff_type)
                    polar1, polar2 = "lcp", "rcp"
                    cal_type = IFCalculation
                elif shift_type == "g":
                    if diff_type is None:
                        diff_type: Literal[1, 2] = input(
                            "\033[32m[1]s-p or [2]p-s?\033[0m"
                        )
                    diff_type = int(diff_type)
                    polar1, polar2 = "s", "p"
                    cal_type = GHCalculation

                calShiftInst1 = cal_type(
                    e_range=calObjInst.e_range,
                    light=polar1,
                    incident_angle=incident_angle,
                )
                calShiftInst2 = cal_type(
                    e_range=calObjInst.e_range,
                    light=polar2,
                    incident_angle=incident_angle,
                )

                calShiftInst1.load_imported_sub_out_dat(self.mediaDat)
                calShiftInst2.load_imported_sub_out_dat(self.mediaDat)

                shift1 = calShiftInst1.calculate(calObjInst)
                shift2 = calShiftInst2.calculate(calObjInst)

                diff: ShiftObj = shift1 - shift2
                diff.plot(
                    f"{shift_type}_diff_{diff_type}",
                    title="Delta Shift",
                    ylabel="Shift",
                )

                if diff_type == 1:
                    return diff
                elif diff_type == 2:
                    return -diff

        if shift_type is None:
            shift_type = input(
                "\033[32mWhat kind of shift are you calculating? ([i]f/[g]h)\033[0m\n"
            )

        shiftInstOut = gh_or_if_cal(shift_type, **args)

        return shiftInstOut

    def shift_cal(
        self,
        x_type=None,
        model_type=None,
        eps_infty=None,
        thickness=None,
        **args,
    ):
        if x_type is None:
            x_type = input(
                "\033[32mWhat is the type of your x variable? (wls/e)\n\033[0m"
            )

        if model_type is None:
            model_type: Literal["c", "t"] = input(
                "\033[32mEntering shift calculatins:\033[0m Which model do you want to choose? ([c]onductivity/[t]hin-film model)\n"
            )

        if model_type == "c":
            print(
                "\033[31mFor conductivity model, the amplitudes of the Lorentzian peaks should be SMALLER than 1.\033[0m\n",
            )

            lpInst: LorentzParameters = self.preset_Lorentz_peaks(x_type=x_type, **args)

            print("Lorentzian peaks parameters set successfully!")
            calObjInst = ReducedConductivity.load_from_lorentz_oscillator(lpInst)

            plotname = None
            if "lpFileName" in args.keys():
                plotname = args["lpFileName"]
                print(f"Plotting with name {plotname}")
            else:
                plotname = "Cond"

            calObjInst.plot(plotname)

            shiftInst = self._eleshift_cal(calObjInst=calObjInst, **args)

        elif model_type == "t":
            print(
                "\033[31mFor thin-film model, Lorentzian peaks are set to expand permittivity\033[0m\n",
            )
            if eps_infty is None:
                eps_infty = input(
                    "\033[31mPlease enter the high-frequency permittivity: (epsilon_infinity)\033[0m\n"
                )
            eps_infty = float(eps_infty)

            if thickness is None:
                thickness = input(
                    "\033[31mPlease enter the thinckness of the material: \033[0m\n"
                )
            thickness = float(thickness)

            lpInst: LorentzParameters = self.preset_Lorentz_peaks(x_type=x_type, **args)

            calObjInst = Permittivity.load_from_lorentzOscillators(
                perm_infty=eps_infty, lp=lpInst, d=thickness
            )

            calObjInst.plot_perm()
            calObjInst.plot_n()

            shiftInst = self._eleshift_cal(calObjInst=calObjInst, **args)

        return shiftInst, calObjInst

    def save_dat(
        self, shiftInst: ShiftObj, calObjInst: ReducedConductivity | Permittivity
    ):
        save_or_not: Literal["y", "n"] = input("Save the data into txt file? (y/n)")
        if save_or_not == "y":
            txt_dir = "./txt_dir/"
            if not os.path.exists(txt_dir):
                os.makedirs(txt_dir)
            fname = input("Input a name: (don't enter suffix)")

            np.savetxt(txt_dir + fname + "_shiftlambda.txt", shiftInst.wls)
            np.savetxt(txt_dir + fname + "_shift.txt", shiftInst.shift)

            if isinstance(calObjInst, ReducedConductivity):
                np.savetxt(txt_dir + fname + "_condlambda.txt", calObjInst.wls_range)
                np.savetxt(txt_dir + fname + "_cond.txt", calObjInst.sigma_tilde)
            elif isinstance(calObjInst, Permittivity):
                np.savetxt(txt_dir + fname + "_permlambda.txt", calObjInst.wls_range)
                np.savetxt(txt_dir + fname + "_perm.txt", calObjInst.perm)

    def compare_Lorentz_peaks_with_exp(
        self, dat_i=None, fname="compare_exp_the", **args
    ):
        if dat_i is None:
            dat_i = input("Which column of data do you want to load? (start with 1)\n")
        dat_i = int(dat_i)

        x = self.expVars[0]
        exp_dat = self.expVars[dat_i]

        shiftInst, calObjInst = self.shift_cal(**args)

        mlInst = MultiLines(
            [x, shiftInst.wls], [exp_dat, shiftInst.shift], fdirname="CompareShifts"
        )

        self.save_dat(shiftInst, calObjInst)

        mlInst.plot_y_shifted_collections(fname=fname)


class LorentzFitExp:
    def __init__(
        self,
        perm_infty,
        thickness,
        theta0=np.pi / 4,
        subi=0,
        outi=0,
        if_dat_name: str = "IF_colle",
        gh_dat_name: str = "GH_colle",
        sub_name="SubN",
        out_name="OutN",
        fInst=FilesSave("PSHE/fitting"),
    ) -> None:
        self.perm_infty = perm_infty
        self.thickness = thickness

        self.theta0 = theta0
        self.subi = subi
        self.outi = outi

        self.exp_dat = ExpDat(if_dat_name=if_dat_name, gh_dat_name=gh_dat_name)
        self.out_dat = OutDat(out_name=out_name)
        self.sub_dat = SubDat(dat_filename=sub_name)

        self.fInst = fInst

    def perm_construct(self, wlsInst, args):
        lo_len = len(args) // 3
        center = args[:lo_len]
        amp = args[lo_len : 2 * lo_len]
        gamma = args[2 * lo_len : 3 * lo_len]

        lp = LorentzParameters(center, amp, gamma)
        lo = LorentzOscillator(lp, wlsInst)

        cond = ReducedConductivity.load_from_lorentz_oscillator(lp)
        perm = Permittivity.sigma2d_to_perm(self.perm_infty, cond, self.thickness)

        return lo, perm

    def shift_func(
        self,
        wls_x,
        *args,
        shift_type: Literal["if", "gh"] = "if",
        lightp: Literal["rcp", "lcp", "s", "p"] = "lcp",
    ):
        """
        args: [centers, amps, gammas, shift]
        """
        args = list(args[0])
        wlsInst = WaveLengthRange(wls_x)
        lo, perm = self.perm_construct(wlsInst, args)

        calInst: IFCalculation | GHCalculation = eval(
            "{}Calculation(wlsInst=wlsInst,light=lightp,theta0=self.theta0,subi=self.subi,outi=self.outi)".format(
                shift_type.upper()
            )
        )

        return calInst.calculate(perm).shift + args[-1]

    def plot_exp(self):
        self.exp_dat.plot_if_data()
        self.exp_dat.plot_gh_data()

    def fit(
        self,
        sample_i,
        lp: LorentzParameters,
        shift_type: Literal["if", "gh"] = "if",
        lightp: Literal["rcp", "lcp", "s", "p"] = "rcp",
        update_fit=False,
        plot_fitted_cond=True,
        twin_lim=[0, 0.6],
    ):
        fname = "{}exp_{}_sample{}".format(shift_type, lightp, sample_i)
        fInst = self.fInst + "FitFiles"

        if getattr(self.exp_dat, "exist_{}_data".format(shift_type)):
            print("Existing experiment data, fitting...")
        else:
            print("No experiment data found")

        sample_list = getattr(self.exp_dat, "{}_shifts_list".format(shift_type))
        sample_dat: ExpIFShiftEle | ExpGHShiftEle = sample_list[sample_i]

        wlsInst = WaveLengthRange(sample_dat.wls)

        lo, perm = self.perm_construct(wlsInst, lp.pars_set)

        the_shift: IFShift | GHShift = eval(
            "{}Calculation(wlsInst=wlsInst,light=lightp,theta0=self.theta0,subi=self.subi,outi=self.outi,).calculate(perm)".format(
                shift_type.upper()
            )
        )

        # bg_shift = BGIF(
        #     wlsInst=wlsInst,
        #     MatInst=perm,
        #     light=lightp,
        #     theta0=self.theta0,
        #     subi=self.subi,
        #     outi=self.outi,
        # )

        bg_shift: BGIF | BGGH = eval(
            "BG{}(wlsInst=wlsInst,MatInst=perm,light=lightp,theta0=self.theta0,subi=self.subi,outi=self.outi,)".format(
                shift_type.upper()
            )
        )

        setattr(
            sample_dat,
            "{}_shift".format(lightp),
            getattr(sample_dat, "{}_shift".format(lightp))
            / getattr(sample_dat, "{}_kb".format(lightp))[0]
            * bg_shift.bg_if_kb[0],
        )
        setattr(
            sample_dat,
            "{}_shift".format(lightp),
            getattr(sample_dat, "{}_shift".format(lightp))
            - getattr(sample_dat, "{}_center_y".format(lightp))
            + bg_shift.bg_if_center_y,
        )

        Line(
            [getattr(sample_dat, "wls"), the_shift.wls],
            [getattr(sample_dat, "{}_shift".format(lightp)), the_shift.shift],
            self.fInst.dirname,
        ).multiplot(
            "initpar_{}exp_{}_sample{}".format(shift_type, lightp, sample_i),
            ["Experiment", "Theoretical"],
            r"$\lambda$ (nm)",
            r"$\Delta_{%s}^{%s}$" % (shift_type.upper(), lightp.upper()),
            title="{}-{} shift (Sample {})".format(
                lightp.upper(), shift_type.upper(), sample_i
            ),
            linestyles=[".", "-"],
        )

        if fInst.exist_npy(fname) and (not update_fit):
            print("Fitting done before, generating figures")
            popt = fInst.load_npy(fname)
        else:
            print("Fitting...\n")
            print("Init parameters are: ")
            print(lp.pars_set)
            popt = curve_fit(
                lambda x, *p0: self.shift_func(
                    x, p0, lightp=lightp, shift_type=shift_type
                ),
                getattr(sample_dat, "wls"),
                getattr(sample_dat, "{}_shift".format(lightp)),
                p0=lp.pars_set,
                bounds=lp.pars_bound,
                maxfev=50000,
            )[0]
            fInst.save_npy(fname, popt)

        lo_len = len(popt) // 3

        print("Fitted parameters:")
        print("Centers: ", list(popt[:lo_len]))
        print("Amplitudes: ", list(popt[lo_len : 2 * lo_len]))
        print("Gamma: ", list(popt[2 * lo_len : 3 * lo_len]))
        print("Overall shift: ", popt[-1], "\n")

        lo, perm = self.perm_construct(wlsInst, popt)

        fitted_shift: IFShift | GHShift = eval(
            "{}Calculation(wlsInst=wlsInst,light=lightp,theta0=self.theta0,subi=self.subi,outi=self.outi,).calculate(perm)".format(
                shift_type.upper()
            )
        )

        ax, fig = Line(
            [getattr(sample_dat, "wls"), fitted_shift.wls],
            [getattr(sample_dat, "{}_shift".format(lightp)), fitted_shift.shift],
            self.fInst.dirname + "/fittedpar",
        ).multiplot(
            "fittedpar_{}exp_{}_sample{}".format(shift_type, lightp, sample_i),
            ["Experiment", "Theoretical"],
            r"$\lambda$ (nm)",
            r"$\Delta_{%s}^{%s}$" % (shift_type.upper(), lightp.upper()),
            title="{}-{} shift (Sample {})".format(
                lightp.upper(), shift_type.upper(), sample_i
            ),
            linestyles=[".", "-"],
            ax_return=True,
        )

        if plot_fitted_cond:
            cond = self._plot_2d_cond(popt, wlsInst)
            cond.fInst = self.fInst + "Cond"
            cond.plot(fname)

            ex_lines = list(ax.get_lines())
            ax_twin = ax.twinx()
            add_line = ax_twin.plot(
                cond.wls,
                cond.real_part,
                "r--",
            )
            ax_twin.set_ylabel(r"$\mathrm{Re}[\tilde{\sigma}]$", color="r")
            ax_twin.spines["right"].set_color("red")
            ax_twin.set_ylim(twin_lim)
            line_list = ex_lines + add_line
            ax_twin.tick_params(axis="y", color="r")

            handles, labels = ax.get_legend_handles_labels()
            leg_list = labels + ["Fitted 2D conductivity"]
            ax.legend(line_list, leg_list)

            for ele_label in ax_twin.get_yticklabels():
                ele_label.set_color("red")
            self.fInst.save_fig(fig, fname)
            plt.close(fig)

        return popt

    def _plot_2d_cond(self, popt, wlsInst) -> ReducedConductivity:
        lo_len = len(popt) // 3

        centers = popt[:lo_len]
        amps = popt[lo_len : 2 * lo_len]
        gammas = popt[2 * lo_len : 3 * lo_len]

        lp = LorentzParameters(centers, amps, gammas)
        lo = LorentzOscillator(lp, wlsInst)

        return ReducedConductivity.load_from_lorentz_oscillator(lo)

    def comp_cond(
        self,
        fname,
        fname_list,
        wlsInst: WaveLengthRange = WaveLengthRange(500, 700),
        title="",
        legends=None,
    ):
        fInst = self.fInst + "FitFiles"
        cond_list = []

        if legends is None:
            legends = ["Sample {}".format(ele[-1]) for ele in fname_list]
        else:
            pass
        for ele_name in fname_list:
            popt = fInst.load_npy(ele_name)
            lo_len = len(popt) // 3

            centers = popt[:lo_len]
            amps = popt[lo_len : 2 * lo_len]
            gammas = popt[2 * lo_len : 3 * lo_len]
            lp = LorentzParameters(centers, amps, gammas)
            lo = LorentzOscillator(lp, wlsInst)
            cond = ReducedConductivity.load_from_lorentz_oscillator(lo)
            cond_list.append(cond.real_part)
        Line(
            [wlsInst.wls_arr] * len(fname_list),
            cond_list,
            fdirname=self.fInst.dirname,
        ).multiplot(
            fname,
            legends,
            xlabel=r"$\lambda$ (nm)",
            ylabel=r"$\mathrm{Re}[\tilde{\sigma}]$",
            title=title,
        )


# def main():
#
#     # wlsInst = WaveLengthRange(500, 700)
#     # lp = LorentzParameters([2000], [0.5], [50])
#     # lo = LorentzOscillator(lp, wlsInst)
#     # cond = ReducedConductivity.lorentzO(lo)
#     # perm = Permittivity.sigma2d_to_perm(15.6, cond, 0.65)
#
#     # lp = LorentzParameters([2200], [0.5], [50])
#     # lo = LorentzOscillator(lp, wlsInst)
#     # cond = ReducedConductivity.lorentzO(lo)
#     # perm2 = Permittivity.sigma2d_to_perm(15.6, cond, 0.65)
#
#     # ghshift_s = GHCalculation(wlsInst, "s").calculate(perm)
#     # ghshift_p = GHCalculation(wlsInst, "p").calculate(perm)
#
#     # testshift_p = GHCalculation(wlsInst, "p").calculate([perm2, perm])
#     # testshift_s = GHCalculation(wlsInst, "s").calculate([perm2, perm])
#
#     # # ghshift = BGGH(wlsInst, perm).calculate(perm)
#     # ghshift_s.plot("GH-s")
#     # ghshift_p.plot("GH-p")
#
#     # testshift_p.plot("GH-p-test")
#     # testshift_s.plot("GH-s-test")
#
#     # wlsInst = WaveLengthRange(400, 800)
#     # lp = LorentzParameters(
#     #     [1800, 1900, 2000, 2100], [0.3, 0.3, 0.3, 0.3], [50, 50, 50, 50]
#     # )
#     # lo = LorentzOscillator(lp, wlsInst)
#     # lo.plot()
#     lp = LorentzParameters(
#         [
#             1825.9742034223834,
#             1875.2060782602973,
#             1929.5850575646718,
#             1976.429785797628,
#             2086.455798630417,
#             2176.2986522772508,
#             2268.5445084234475,
#             2402.87722433451,
#         ],
#         [
#             0.5051608050534825,
#             0.20000000000000004,
#             0.5544960560275749,
#             0.3711244844449047,
#             0.45322987395570524,
#             0.35748517088865626,
#             0.4225113293747884,
#             0.6586445253162231,
#         ],
#         [
#             29.400467019873812,
#             10.000000000000002,
#             43.484925870525245,
#             23.02968872333086,
#             45.61049846071738,
#             97.46330614895763,
#             110.67848457626937,
#             54.13900146331418,
#         ],
#         components="e_amp_gamma",
#         gamma_bot=10,
#         shift_span=100,
#     )
#     # LorentzFitExp(15.6, 0.65).plot_exp()
#     # for ele in range(len(ExpDat().gh_shifts_list)):
#     #     LorentzFitExp(15.6, 0.65).fit(ele, lp, lightp="p", shift_type="gh")
#
#     # LorentzFitExp(15.6, 0.65).fit(
#     #     4, lp, lightp="p", shift_type="gh", update_fit=False, twin_lim=[0, 1]
#     # )
#
#     # for ele in range(len(ExpDat().gh_shifts_list)):
#     #     LorentzFitExp(15.6, 0.65).fit(
#     #         ele, lp, lightp="rcp", shift_type="if", update_fit=False, twin_lim=[0, 0.5]
#     #     )
#     #     LorentzFitExp(15.6, 0.65).fit(
#     #         ele, lp, lightp="lcp", shift_type="if", update_fit=False, twin_lim=[0, 0.5]
#     #     )
#     #     LorentzFitExp(15.6, 0.65).fit(
#     #         ele, lp, lightp="s", shift_type="gh", update_fit=False, twin_lim=[0, 1]
#     #     )
#     #     LorentzFitExp(15.6, 0.65).fit(
#     #         ele, lp, lightp="p", shift_type="gh", update_fit=False, twin_lim=[0, 1]
#     #     )
#
#     # fname_list = ["ghexp_p_sample{}".format(ele) for ele in [0, 1, 2, 4]]
#     # LorentzFitExp(15.6, 0.65).comp_cond(
#     #     "p_light_comp_exclude3", fname_list, title="P-light GH fitted conductivity"
#     # )
#
#     # fname_list = ["ghexp_s_sample{}".format(ele) for ele in [0, 1, 2, 4]]
#     # LorentzFitExp(15.6, 0.65).comp_cond(
#     #     "s_light_comp_exclude3", fname_list, title="S-light GH fitted conductivity"
#     # )
#
#     # fname_list = ["ifexp_lcp_sample{}".format(ele) for ele in [0, 1, 2, 3, 4]]
#     # LorentzFitExp(15.6, 0.65).comp_cond(
#     #     "lcp_light_comp", fname_list, title="LCP-light IF fitted conductivity"
#     # )
#
#     # fname_list = ["ifexp_rcp_sample{}".format(ele) for ele in [0, 1, 2, 3, 4]]
#     # LorentzFitExp(15.6, 0.65).comp_cond(
#     #     "rcp_light_comp", fname_list, title="RCP-light IF fitted conductivity"
#     # )
#
#     fname_list = [
#         "ghexp_p_sample4",
#         "ghexp_s_sample4",
#         "ifexp_lcp_sample4",
#         "ifexp_rcp_sample4",
#     ]
#     LorentzFitExp(15.6, 0.65).comp_cond(
#         "cond_comp_sample4",
#         fname_list,
#         title="Fitted conductivity for sample 4",
#         legends=["p", "s", "LCP", "RCP"],
#     )
#
#     pass


# if __name__ == "__main__":
#     main()
