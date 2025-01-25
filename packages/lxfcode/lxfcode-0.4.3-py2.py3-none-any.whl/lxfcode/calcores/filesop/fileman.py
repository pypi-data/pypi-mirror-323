from typing import Any
from .filesave import FilesSave
from ..abc.abcal import ABCal
import os

__all__ = ["FileManager"]


class FileManager:
    _allinfo_prefix = "alltrans"
    ele_name = "e_{}"

    def __init__(
        self,
        calInst: ABCal,
        root_dir_name="Dat",
        ffolder: str = "",
        results_list: list[str] = [],
        dir_extra_suffix: list[str] = [],
    ) -> None:
        self.calInst = calInst
        self.ffolder = os.path.join(*ffolder.split("/"))

        if len(dir_extra_suffix) != 0:
            dir_extra_suffix.insert(0, "")

        self._classinfo = (
            f"../{self.ffolder}/{self.calInst.haInst.__class__.__name__}_{self.calInst.haInst.sigs}_{self.calInst.density}"
            + "_".join(dir_extra_suffix)
        )

        self.root_dir = FilesSave(root_dir_name) + self._classinfo

        self.results_list = results_list

        if results_list:
            print("setting results variables")
            for ele_re_name in results_list:
                attr_val = "_".join(
                    (
                        [ele_re_name] + self._classinfo.split("/")[1:]
                        if self.ffolder
                        else ([ele_re_name] + self._classinfo.split("/")[2:])
                    ),
                )

                setattr(self, ele_re_name, attr_val)

    def load(self, update_sourcenpy=False, enable_message=True):
        messInst = Messager(enable_message)
        messInst(
            f"Checking whether the data exists for calculation class: {self.calInst.__class__.__name__}"
        )
        dat_exist_flag = None
        vars_list = []
        for ele_re_name in self.results_list:
            if self.root_dir.exist_npy(getattr(self, ele_re_name)):
                messInst(
                    f"Found existting data in {self.root_dir.npy_dir}: ",
                    getattr(self, ele_re_name),
                )
                messInst("Loading data...")

                vars_list.append(self.root_dir.load_npy(getattr(self, ele_re_name)))
                dat_exist_flag = True

            else:
                dat_exist_flag = False
                print(
                    f"No existing data in {self.root_dir.npy_dir} for variable '{ele_re_name}'"
                )
                break

        if not dat_exist_flag or update_sourcenpy:
            messInst("Calculating based on the calculate instances passed in")
            vars_list = self._calculations()
            if len(vars_list) != len(self.results_list):
                raise IndexError(
                    "Length of return list doesn't consist with the length of the results you require. Please check!"
                )

            for i, ele_re_name in enumerate(self.results_list):
                messInst(
                    "Saving during calculations",
                    f"data in {self.root_dir.npy_dir} for variable '{ele_re_name}'",
                )
                self.root_dir.save_npy(getattr(self, ele_re_name), vars_list[i])

        return vars_list

    def save(self, vars_list) -> None:
        if len(vars_list) != len(self.results_list):
            raise IndexError(
                "Length of return list doesn't consist with the length of the results you require. Please check!"
            )

        for i, ele_re_name in enumerate(self.results_list):
            print(
                "Saving by save function: ",
                f"data in {self.root_dir.npy_dir} for variable '{ele_re_name}'",
            )
            self.root_dir.save_npy(getattr(self, ele_re_name), vars_list[i])

    def _calculations(self) -> Any:
        return self.calInst.calculate()


class Messager:
    def __init__(self, enable: bool = True) -> None:
        self.enable = enable

    def __call__(self, info: str, *args: Any, **kwds: Any) -> Any:
        if self.enable:
            print(info)
        else:
            pass
