import os
import numpy as np
from matplotlib.figure import Figure
import cv2

__all__ = ["FilesSave"]


class FilesSave:
    root_dir = os.getcwd()

    def __init__(self, dirname: str = "Data") -> None:
        self.dirname: str = dirname
        self.dir_levels = dirname.split("/")

        self.target_dir = os.path.join(self.root_dir, *self.dir_levels) + os.sep
        self.npy_dir = self.target_dir + "npy" + os.sep
        self.fig_dir = self.target_dir + "fig" + os.sep

    def __add__(self, sublevels: str):
        levels = sublevels.split("/")
        if levels[0] == "..":
            levels.pop(0)
            new_level = self.dir_levels.copy()
            new_level.insert(1, levels[0])
            levels.pop(0)

            sumdir = os.path.join(*new_level, *levels)
            return FilesSave(sumdir)
        sumdir = os.path.join(*self.dir_levels, *levels)
        return FilesSave(sumdir)

    def __repr__(self) -> str:
        return self.target_dir

    def __radd__(self, sublevels: str):
        return self.__add__(sublevels)

    def save_npy(self, fname, npy, subfolder=""):
        if not subfolder:
            npy_dir = self.npy_dir
        else:
            folder_levels = subfolder.split("/")
            npy_dir = os.path.join(self.npy_dir, *folder_levels) + os.sep
        if not os.path.exists(npy_dir):
            os.makedirs(npy_dir)
        np.save(npy_dir + fname + ".npy", npy)

    def exist_npy(self, fname):
        if os.path.exists(self.npy_dir + fname + ".npy"):
            return True

    def load_npy(self, fname):
        if self.exist_npy(fname):
            return np.load(self.npy_dir + fname + ".npy")
        else:
            raise FileNotFoundError("No npy file named: ", fname)

    def load_fig_path(self, fname, subfolder="") -> str:
        folder_levels = subfolder.split("/")
        figdir = os.path.join(self.fig_dir, *folder_levels) + os.sep
        if (
            bool(subfolder)
            and os.path.exists(figdir)
            and os.path.exists(figdir + fname)
        ):
            return figdir + fname
        else:
            raise FileNotFoundError(
                "input subfolder doesn't exist or file doesn't exist"
            )

    def save_fig(self, fig: Figure, fname, save_pdf=False, subfolder=""):
        if not subfolder:
            fig_dir = self.fig_dir
        else:
            folder_levels = subfolder.split("/")
            fig_dir = os.path.join(self.fig_dir, *folder_levels) + os.sep

        if not os.path.exists(fig_dir):
            os.makedirs(fig_dir)

        fig.savefig(
            fig_dir + fname + ".png",
            dpi=330,
            facecolor="w",
            bbox_inches="tight",
            pad_inches=0.1,
        )
        if save_pdf:
            fig.savefig(
                fig_dir + fname + ".pdf",
                dpi=330,
                facecolor="w",
                bbox_inches="tight",
                pad_inches=0.1,
            )

    def exist_fig(self, fname="", subfolder=""):
        folder_levels = subfolder.split("/")
        figdir = os.path.join(self.fig_dir, *folder_levels) + os.sep
        if bool(fname):
            if os.path.exists(figdir + fname + ".png"):
                return True
            return False
        if os.path.exists(figdir) and os.listdir(figdir):
            return True
        return False

    def save_movie(
        self,
        figs_list: list[str],
        mv_fname: str,
        frames=25,
        subfolder="",
        fig_dir=None,
        fig_format=".png",
    ):
        if fig_dir is None:
            figs_list = [
                self.fig_dir + ele_fname + fig_format for ele_fname in figs_list
            ]
        else:
            figs_list = [fig_dir + ele_fname + fig_format for ele_fname in figs_list]
        folder_levels = subfolder.split("/")
        folder_levels.insert(0, "mv")
        mv_dir = os.path.join(self.target_dir, *folder_levels) + os.sep

        if not os.path.exists(mv_dir):
            os.makedirs(mv_dir)
        img_example = cv2.imread(figs_list[0])
        img_shape = img_example.shape[:2]
        print("shape: ", img_shape)

        writer = cv2.VideoWriter(
            mv_dir + mv_fname + ".mp4",
            cv2.VideoWriter_fourcc("m", "p", "4", "v"),
            frames,
            img_shape[::-1],
            True,
        )
        shapes_list = []
        for elef in figs_list:
            read_img = cv2.imread(elef)
            read_img = cv2.resize(read_img, dsize=img_shape[::-1])
            writer.write(read_img)
            shapes_list.append(read_img.shape[:2])
        writer.release()
