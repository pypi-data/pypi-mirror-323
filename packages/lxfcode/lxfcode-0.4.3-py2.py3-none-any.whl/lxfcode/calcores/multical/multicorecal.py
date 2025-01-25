import multiprocessing
import time
from typing import Callable
from tqdm import tqdm
import numpy as np
import os

__all__ = ["MultiCal"]


class MultiCal:
    def __init__(
        self,
        func: Callable,
        x_list: list | np.ndarray,
        other_args_list: list = [],
        core=3,
        disable_progress_bar=False,
    ) -> None:
        self.func = func
        self.x_list = x_list
        self.args = other_args_list
        self.core_num = core
        self.disable_progress_bar = disable_progress_bar

    def _split_xlists(self):
        out_divided_lists = []
        ldivide = len(self.x_list) // self.core_num
        last_i = 0
        for i in range(self.core_num - 1):
            tmp_list = self.x_list[i * ldivide : (i + 1) * ldivide]
            out_divided_lists.append(tmp_list)
            last_i = i
        out_divided_lists.append(self.x_list[(last_i + 1) * ldivide :])
        return out_divided_lists

    def _overdrive_func(
        self,
        core_i,
        list_to_cal,
        trans_out_list,
    ):
        ele_list = []
        if self.disable_progress_bar:
            num_eles = len(list_to_cal)
            print("Elements to calculate per progress: ", num_eles)

            for i, ele in enumerate(list_to_cal):
                if int(i / num_eles * 100) % 20 == 0:
                    print(
                        f"eles percent calculated at core {core_i}: ",
                        i / num_eles * 100,
                    )
                ele_list.append(self.func(ele, *self.args))
        else:
            for ele in tqdm(
                list_to_cal,
                ncols=80,
                # desc=f"Process—{core_i} pid:{str(os.getpid())}",
                # delay=0.01,
                # position=core_i,
                # ascii=False,
            ):
                ele_list.append(self.func(ele, *self.args))

        ele_list.append(core_i)
        trans_out_list.append(ele_list)

    def calculate(self):
        out_list = multiprocessing.Manager().list()
        p_f = multiprocessing.Pool(
            self.core_num,
            # initializer=tqdm.set_lock,
            # initargs=(multiprocessing.RLock(),),
        )

        divided_list = self._split_xlists()
        for i in range(self.core_num):
            p_f.apply_async(
                self._overdrive_func,
                args=(i, divided_list[i], out_list),
            )

        print(
            f"Executing func: '{self.func.__name__}' in parallel mode. Waiting for all subprocesses done..."
        )
        print("Total processes: ", self.core_num)
        p_f.close()
        p_f.join()

        print("All subprocesses done.")

        total_list = []
        for path_i in range(self.core_num):
            for ele_list in out_list:
                if ele_list[-1] == path_i:
                    total_list.extend(ele_list[0:-1])
        return total_list
