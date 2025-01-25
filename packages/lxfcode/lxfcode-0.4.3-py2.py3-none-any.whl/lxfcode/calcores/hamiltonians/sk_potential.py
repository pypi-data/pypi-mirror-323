from typing import Union
import numpy as np
import matplotlib.pyplot as plt


class SKPotential:
    def __init__(self, Vppi0, Vpps0, a0, d0, delta0) -> None:
        self.Vppi0 = Vppi0
        self.Vpps0 = Vpps0

        self.a0 = a0
        self.d0 = d0
        self.delta0 = delta0

    def Vpp_pi(self, d: Union[float, np.ndarray]):
        """V_pp_pi interaction

        Args:
            d: The distance norm between two orbitals

        Returns:
            interaction between orbitals.
        """
        return self.Vppi0 * np.exp(-((d - self.a0) / self.delta0))

    def Vpp_sigma(self, d: Union[float, np.ndarray]):
        """V_pp_sigma interaction

        Args:
            d: The distance norm between two orbitals

        Returns:
            interaction between orbitals.
        """
        return self.Vpps0 * np.exp(-((d - self.d0) / self.delta0))
