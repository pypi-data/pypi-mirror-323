from abc import ABCMeta, abstractmethod
import numpy as np

from ..hamiltonians.klattices import BiKLattices
from ..pubmeth.consts import *

from typing import Literal, Type, Union

from ..pubmeth.pointset import HexLats

from ..hamiltonians.sk_potential import SKPotential

__all__ = ["ABContiGraMoires", "ABContiMoHa", "ABCommGraMoires", "ABTBMoHa"]


class ABContiGraMoires(metaclass=ABCMeta):
    mat_name = "Moire"

    def __init__(
        self,
        twist_angle: float,
        haClassType: Type["ABContiMoHa"],
        vFcoeff: float = 1,
        a0: float = 2.46,  #   Angstrom
        kshells: int = 7,
        w_inter: float = 118,
        tperp_coeff=1.0,
        **kwargs,
    ) -> None:
        self.a0 = a0
        self.twist_angle = twist_angle
        self.haClassType = haClassType
        self.vF = 1e6 * vFcoeff
        self.w = w_inter
        self.shells = kshells
        self.tperp_coeff = tperp_coeff
        pass

    @property
    def aM(self):
        sc_period = self.a0 / (2 * np.sin(self.twist_angle / 180 * np.pi / 2))
        return sc_period

    @property
    def renormed_BZ_K_side(self):
        return abs(4 * np.pi / (3 * self.aM))

    @property
    def K0(self):
        return abs(4 * np.pi / (3 * self.a0))

    @property
    def areaM(self):
        return np.sqrt(3) / 2 * self.aM**2

    @property
    def areaO(self):
        return np.sqrt(3) / 2 * self.a0**2

    @property
    def epsilonM(self):
        return h_bar_eV * self.vF * self.renormed_BZ_K_side * m2A * eV2meV

    @property
    def epsilonO(self):
        return h_bar_eV * self.vF * self.K0 * m2A * eV2meV


class ABContiMoHa(metaclass=ABCMeta):
    b_p_arr = np.array([np.sqrt(3) / 2, 3 / 2])
    b_n_arr = np.array([-np.sqrt(3) / 2, 3 / 2])
    K_b = np.array([-np.sqrt(3) / 2, -1 / 2])
    K_t = np.array([-np.sqrt(3) / 2, 1 / 2])
    Gamma = np.array([0, 0])
    M = (K_b + K_t) / 2
    BZ_renormed = True

    def __init__(
        self,
        moInst: ABContiGraMoires,
        signature: Literal["twist_angle", "mat_name"] = "twist_angle",
    ) -> None:
        self.moInst = moInst
        self.k1, self.k2 = BiKLattices(self.moInst.shells).basis_set()
        self.expand_v = BiKLattices(self.moInst.shells).expand_vecs()

        self.sigs = getattr(self.moInst, signature)

        if signature == "twist_angle":
            self.sigs = "{:.2f}".format(self.sigs)
            self.sigs_title = r"$\theta={}\degree$".format(self.sigs)
        elif signature == "mat_name":
            self.sigs_title = f"Material Type: {self.sigs}"

    @abstractmethod
    def _h1(self, k_arr):
        pass

    @abstractmethod
    def _h2(self, k_arr):
        pass

    @abstractmethod
    def _hinter(self, k_arr):
        pass

    @abstractmethod
    def h(self, k_arr) -> np.ndarray:
        pass


class ABCommGraMoires(metaclass=ABCMeta):
    def __init__(
        self,
        m0: int,
        r: int,
        haClassType: Type["ABTBMoHa"],
        a1: np.ndarray = np.array([np.sqrt(3) / 2, -1 / 2]),
        a2: np.ndarray = np.array([np.sqrt(3) / 2, 1 / 2]),
        a0: float = 2.46,
        d0: float = 3.35,
    ) -> None:
        self.m0 = m0
        self.r = r
        self.a1 = a0 * a1
        self.a2 = a0 * a2

        self.haClassType = haClassType

        self.twist_angle = round(
            (
                np.arccos(
                    (3 * m0**2 + 3 * m0 * r + r**2 / 2)
                    / (3 * m0**2 + 3 * m0 * r + r**2)
                )
                / pi
                * 180
            ),
            2,
        )

        self.mat_name = "{:.2f} Commensurate Moire".format(self.twist_angle)

        self.a0 = a0
        self.d = d0

        self.scale = int(np.linalg.norm(self.R1) // np.linalg.norm(self.a1) * 2)

        print(f"Hamiltonian shape: ({self.n_atoms},{self.n_atoms})")

    @property
    def aM(self):
        return np.linalg.norm(self.R1)
        # return self.a0 / (2 * np.sin(self.twist_angle / 180 * np.pi / 2))

    @property
    def areaM(self):
        # return np.sqrt(3)
        return np.sqrt(3) / 2 * self.aM**2

    @property
    def renormed_BZ_K_side(self):
        return 1

    @property
    def areaO(self):
        return np.sqrt(3) / 2 * self.a0**2

    @property
    def R1(self):
        R1 = (
            self.m0 * self.a1 + (self.m0 + self.r) * self.a2
            if self.r % 3 != 0
            else (self.m0 + (self.r // 3)) * self.a1 + (self.r // 3) * self.a2
        )
        return R1

    @property
    def R2(self):
        R2 = (
            -(self.m0 + self.r) * self.a1 + (2 * self.m0 + self.r) * self.a2
            if self.r % 3 != 0
            else -(self.r // 3) * self.a1 + (self.m0 + 2 * (self.r // 3)) * self.a2
        )
        return R2

    @property
    @abstractmethod
    def lat1(self) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def lat2(self) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def lindexes(self) -> list[int]:
        pass

    def lats_transf(self, r_angle=0, shift_arr=np.array([0, 0])):
        return HexLats(
            self.a1,
            self.a2,
            density_tuple=(self.scale, self.scale),
            r_angle=r_angle,
            shift_arr=np.array(shift_arr),
        ).basis_change(self.R1, self.R2)

    def lats_backto_cartesian(self, lat_i=1):
        lats_in = getattr(self, f"lat{lat_i}")
        return lats_in @ np.vstack([self.R1, self.R2])

    def _getlatswithin(self, lat_i, region_index=[0, 0]):
        """Get the lattices within supercell under R1R2 coordinates

        Args:
            lat_i: lattices index for layer

        Returns:
            lattices indexes under R1R2 coordinates within supercell.
        """
        lats = getattr(self, "lat{}".format(lat_i))
        cond1 = np.logical_and(
            lats[:, 0] < 0.5 + region_index[0], lats[:, 0] >= region_index[0] - 0.5
        )
        cond2 = np.logical_and(
            lats[:, 1] < 0.5 + region_index[1], lats[:, 1] >= region_index[1] - 0.5
        )
        cond = np.logical_and(cond1, cond2)
        return lats[cond]

    def atoms_rvec(
        self,
        lat_i: Union[str, np.ndarray] = "within",
        zdefault=0,
        region_index=[0, 0],
    ):
        """Function to get tht actual position vectors for each atom based on the input index or the
        actual R1 R2 coordinates.

        Args:
            zdefault (z shift for atoms): float
            lat_i: layer index. "within" means all the atoms within the supercell

        Returns:
            Atoms position vectors in the real space: np.ndarray
        """
        lats = getattr(self, "latwithin")(region_index)
        z = 0

        if isinstance(lat_i, np.ndarray):
            if len(lat_i.shape) == 1:
                lats = lat_i.reshape((1, -1))
                z = zdefault * np.ones((len(lats), 1))
            elif len(lat_i.shape) > 1 and lat_i.shape[0] > 1:
                lats = lat_i
                zi = (np.array(self.lindexes) - 1).reshape((-1, 1))
                z = np.kron(zi, np.ones((len(lats) // len(self.lindexes), 1))) * self.d
        elif lat_i == "within":
            lats = getattr(self, "latwithin")(region_index)
            zi = (np.array(self.lindexes) - 1).reshape((-1, 1))
            z = np.kron(zi, np.ones((len(lats) // len(self.lindexes), 1))) * self.d
        xy_pos = np.kron(lats[:, 0].reshape((-1, 1)), self.R1) + np.kron(
            lats[:, 1].reshape((-1, 1)), self.R2
        )
        return np.hstack([xy_pos, z])

    def latwithin(self, region_index=[0, 0]):
        lats = [
            self._getlatswithin("{}".format(i), region_index=region_index)
            for i in self.lindexes
        ]
        return np.vstack(lats)

    @property
    def expand_basis(self):
        return np.array(
            [
                [0, 0],
                [0, 1],
                [0, -1],
                [1, 0],
                [-1, 0],
                [1, 1],
                [1, -1],
                [-1, 1],
                [-1, -1],
            ]
        )

    def equal_rvecs(self, expand_times=0, bounds_vals=[0, 0]):
        ##  Expand equivalent atoms using expand basis, generally, it is assumed that nine expansion basises are used.
        ##  olats is the original lattices under R1-R2 coordinates but expanded by kronecker method.
        x, y = np.meshgrid(
            np.arange(-1 - expand_times, 2 + expand_times),
            np.arange(-1 - expand_times, 2 + expand_times),
        )

        expand_basis = np.hstack([x.reshape(-1, 1), y.reshape(-1, 1)])
        expand_vecs = np.kron(
            np.ones((len(self.latwithin(region_index=bounds_vals)), 1)), expand_basis
        )
        olats = np.kron(
            self.latwithin(region_index=bounds_vals),
            np.ones((len(expand_basis), 1)),
        )
        exlats = expand_vecs + olats

        rvecs = self.atoms_rvec(exlats)
        return rvecs

    @property
    def n_atoms(self):
        n_atoms = (
            (
                2
                * len(self.lindexes)
                * (3 * self.m0**2 + 3 * self.m0 * self.r + self.r**2)
            )
            if self.r % 3 != 0
            else (
                2 * len(self.lindexes) * (self.m0**2 + self.m0 * self.r + self.r**2 / 3)
            )
        )
        return int(n_atoms)


class ABTBMoHa(ABContiMoHa, metaclass=ABCMeta):
    BZ_renormed = False

    def __init__(
        self,
        moInst: ABCommGraMoires,
        Vppi0=-2700,
        Vpps0=480,
        delta0coeff=0.184,
        signature: Literal["twist_angle", "mat_name"] = "twist_angle",
    ) -> None:
        self.moInst = moInst
        self.sigs = self.moInst.twist_angle

        if signature == "twist_angle":
            self.sigs_title = r"$\theta={}\degree$".format(self.sigs)
        elif signature == "mat_name":
            self.sigs_title = f"Material Type: {self.sigs}"

        a1z = np.hstack([self.moInst.a1, np.zeros((1,))])
        a2z = np.hstack([self.moInst.a2, np.zeros((1,))])
        a3z = np.array([0, 0, 1])
        self.b1 = 2 * pi * (np.cross(a2z, a3z)) / (a1z @ np.cross(a2z, a3z))
        self.b2 = 2 * pi * (np.cross(a3z, a1z)) / (a1z @ np.cross(a2z, a3z))

        self.b_p_arr = (
            (
                (2 * self.moInst.m0 + self.moInst.r) * self.b1
                + (self.moInst.m0 + self.moInst.r) * self.b2
            )
            / (
                3 * self.moInst.m0**2
                + 3 * self.moInst.m0 * self.moInst.r
                + self.moInst.r**2
            )
            if self.moInst.r % 3 != 0
            else (
                (self.moInst.m0 + 2 * (self.moInst.r // 3)) * self.b1
                + (self.moInst.r // 3) * self.b2
            )
            / (
                self.moInst.m0**2
                + self.moInst.m0 * self.moInst.r
                + self.moInst.r**2 / 3
            )
        )

        self.b_n_arr = (
            (-(self.moInst.m0 + self.moInst.r) * self.b1 + self.moInst.m0 * self.b2)
            / (
                3 * self.moInst.m0**2
                + 3 * self.moInst.m0 * self.moInst.r
                + self.moInst.r**2
            )
            if self.moInst.r % 3 != 0
            else (
                -(self.moInst.r // 3) * self.b1
                + (self.moInst.m0 + (self.moInst.r // 3)) * self.b2
            )
            / (
                self.moInst.m0**2
                + self.moInst.m0 * self.moInst.r
                + self.moInst.r**2 / 3
            )
        )
        self.K_b = ((self.b_p_arr + 2 * self.b_n_arr) / 3)[:2]
        self.K_t = ((2 * self.b_p_arr + self.b_n_arr) / 3)[:2]
        self.M = (self.K_b + self.K_t) / 2
        self.Vppi0 = Vppi0
        self.Vpps0 = Vpps0
        self.delta0coeff = delta0coeff

    @property
    def skp(self):
        return SKPotential(
            Vppi0=self.Vppi0,
            Vpps0=self.Vpps0,
            a0=self.moInst.a0 / np.sqrt(3),
            d0=self.moInst.d,
            delta0=self.delta0coeff * self.moInst.a0,
        )

    @property
    def equal_distarrs(self) -> np.ndarray:
        olats = self.moInst.atoms_rvec("within")
        explats = self.moInst.equal_rvecs()
        olats_e: np.ndarray = np.kron(olats, np.ones((len(explats), 1)))
        explats_e: np.ndarray = np.kron(np.ones((len(olats), 1)), explats)

        dist_arrs = explats_e - olats_e

        return dist_arrs

    @property
    def equal_cos(self) -> np.ndarray:
        cos_arrs: np.ndarray = self.equal_distarrs[:, -1] / np.linalg.norm(
            self.equal_distarrs, axis=1
        )
        cos_arrs[np.isnan(cos_arrs)] = 0
        return cos_arrs

    @property
    def equal_vppi(self) -> np.ndarray:
        return self.skp.Vpp_pi(np.linalg.norm(self.equal_distarrs, axis=1))

    @property
    def equal_vpps(self) -> np.ndarray:
        return self.skp.Vpp_sigma(np.linalg.norm(self.equal_distarrs, axis=1))

    def h(self, k_arr):
        equal_cos = self.equal_cos.reshape((-1, len(self.moInst.expand_basis))).T
        equal_vppi = self.equal_vppi.reshape((-1, len(self.moInst.expand_basis))).T
        equal_vpps = self.equal_vpps.reshape((-1, len(self.moInst.expand_basis))).T
        phase_term: np.ndarray = np.exp(1j * k_arr @ self.equal_distarrs[:, :2].T)
        phase_term = phase_term.reshape(-1, len(self.moInst.expand_basis)).T
        h = phase_term * (equal_vppi * (1 - equal_cos**2) + equal_vpps * equal_cos**2)
        h: np.ndarray = np.sum(h, axis=0)
        h = h.reshape((len(self.moInst.latwithin()), len(self.moInst.latwithin())))

        return h

    def _h2(self, k_arr):
        pass

    def _h1(self, k_arr):
        pass

    def _hinter(self, k_arr):
        pass
