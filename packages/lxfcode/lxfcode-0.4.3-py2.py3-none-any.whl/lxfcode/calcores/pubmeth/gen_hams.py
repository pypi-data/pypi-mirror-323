import numpy as np
import scipy


def DiracH(p_arr: np.ndarray, angle_in):
    theta_in = angle_in / 180 * np.pi

    def ele_h(p_x, p_y):
        return np.array(
            [
                [0, np.exp(-1j * theta_in) * (p_x - 1j * p_y)],
                [np.exp(1j * theta_in) * (p_x + 1j * p_y), 0],
            ]
        )

    if len(p_arr.shape) > 1:
        "Multiple k array to form block diagonal"

        out_list = [ele_h(p_arr[:, 0][i], p_arr[:, 1][i]) for i in range(len(p_arr))]

        return scipy.linalg.block_diag(*out_list)
    return ele_h(p_arr[0], p_arr[1])


def ParabH(p_arr: np.ndarray, angle_in, epsilon, tperp=357):
    theta_in = angle_in / 180 * np.pi

    def ele_h(p_x, p_y):
        return np.array(
            [
                [0, np.exp(-1j * theta_in) * (p_x - 1j * p_y), 0, tperp / epsilon],
                [np.exp(1j * theta_in) * (p_x + 1j * p_y), 0, 0, 0],
                [0, 0, 0, np.exp(-1j * theta_in) * (p_x - 1j * p_y)],
                [tperp / epsilon, 0, np.exp(1j * theta_in) * (p_x + 1j * p_y), 0],
            ]
        )

    if len(p_arr.shape) > 1:
        "Multiple k array to form block diagonal"

        out_list = [ele_h(p_arr[:, 0][i], p_arr[:, 1][i]) for i in range(len(p_arr))]

        return scipy.linalg.block_diag(*out_list)

    return ele_h(p_arr[0], p_arr[1])


def AAstackedH(p_arr: np.ndarray, angle_in, epsilon, tperp_AA=93, tperp_BB=105):
    theta_in = angle_in / 180 * np.pi

    def ele_h(p_x, p_y):
        return np.array(
            [
                [
                    0,
                    np.exp(-1j * theta_in) * (p_x - 1j * p_y),
                    tperp_AA / epsilon,
                    0,
                ],
                [
                    np.exp(1j * theta_in) * (p_x + 1j * p_y),
                    0,
                    0,
                    tperp_BB / epsilon,
                ],
                [
                    tperp_AA / epsilon,
                    0,
                    0,
                    np.exp(-1j * theta_in) * (p_x - 1j * p_y),
                ],
                [
                    0,
                    tperp_BB / epsilon,
                    np.exp(1j * theta_in) * (p_x + 1j * p_y),
                    0,
                ],
            ]
        )

    if len(p_arr.shape) > 1:
        "Multiple k array to form block diagonal"

        out_list = [ele_h(p_arr[:, 0][i], p_arr[:, 1][i]) for i in range(len(p_arr))]

        return scipy.linalg.block_diag(*out_list)

    return ele_h(p_arr[0], p_arr[1])
