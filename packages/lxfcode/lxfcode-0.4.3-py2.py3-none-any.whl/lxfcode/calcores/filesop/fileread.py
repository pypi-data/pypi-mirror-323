import glob
import os

import pandas as pd
from pandas.errors import EmptyDataError

__all__ = ["FilesRead"]


class FilesRead:
    root_dir = os.getcwd()

    def __init__(self, dirname: str = "Data") -> None:
        self.dirname: str = dirname
        self.dir_levels = dirname.split("/")

        self.target_dir = os.path.join(self.root_dir, *self.dir_levels) + os.sep

    def _get_file(self, fname=None) -> list[str]:
        if fname is None:
            raise FileNotFoundError("You have to assign the file name!")
        else:
            fname_list = glob.glob(fname + "*")
            if not fname_list:
                raise FileNotFoundError("No file matches the name argument")
            else:
                return fname_list

    def load(self, fname: str | None, sheet_i: None | int = None) -> list:
        """
        fname: filename of the Data you want to load
        sheet_i: index for the sheet you want to load. Start with 0
        """

        fname_list = self._get_file(fname)
        vars_list = []

        ele_fname = fname_list[0]
        if len(fname_list) > 1:
            fi = input(
                f"More than 1 files are found: {fname_list}. Please put the index of file you want to use: (index start from 0) \n"
            )
            if not fi:
                fi = 0
            ele_fname = fname_list[int(fi)]

        match ele_fname.split(".")[-1]:
            case "xlsx":
                print("Data in xlsx format")
                if not sheet_i:
                    print("No shee index assigned, choose the first sheet...")
                    # sheet_i = input(
                    #     f"Please set the sheet index for file '{ele_fname}' (default: 0): \n"
                    # )
                    vars_list = self._excel_load(ele_fname, 0)
                else:
                    vars_list = self._excel_load(ele_fname, sheet_i=int(sheet_i))
            case "csv":
                print("Data in csv format")
                vars_list = self._csv_load(ele_fname)
        if not vars_list:
            raise EmptyDataError("No data in variable list!")

        return vars_list

    def _excel_load(self, fname, sheet_i=0):
        ##  Load excel file based on sheet_i
        dat = pd.read_excel(fname, sheet_i)
        ncols = len(dat.columns)

        vars_list = []
        for ele_col in range(ncols):
            ele_var = dat.iloc[:, ele_col]
            vars_list.append(ele_var)

        return vars_list

    def _csv_load(self, fname):
        dat = pd.read_csv(fname)
        ncols = len(dat.columns)

        vars_list = []
        for ele_col in range(ncols):
            ele_var = dat.iloc[:, ele_col]
            vars_list.append(ele_var)

        return vars_list
