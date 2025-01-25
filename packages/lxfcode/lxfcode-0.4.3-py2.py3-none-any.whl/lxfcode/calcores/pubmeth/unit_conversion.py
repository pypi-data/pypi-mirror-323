import numpy as np
from .consts import h_bar_eV, eV2meV


def energy2omega(energy_in_meV):
    omega_arr = np.array(energy_in_meV) / (h_bar_eV * eV2meV)

    return omega_arr


def wls2omega(wls_in_nm):
    energy_in_meV = 1240 / wls_in_nm * 1000
    omega_arr = np.array(energy_in_meV) / (h_bar_eV * eV2meV)

    return omega_arr
