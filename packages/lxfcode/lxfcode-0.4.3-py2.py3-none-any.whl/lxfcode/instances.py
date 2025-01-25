import matplotlib.pyplot as plt
import numpy as np

from .calcores.absorption.absorption_cal import AbsorptionCal
from .calcores.hamiltonians.ham_out import HamOut
from .calcores.materials.graphene import SLGra
from .calcores.multical.raman_scan import RamanScan
from .calcores.pshe.fitexp import (
    ExpDat,
    LorentzFitExp,
    LorentzOscillator,
    LorentzParameters,
    OutDat,
    Permittivity,
    ReducedConductivity,
    SubDat,
    WaveLengthRange,
)
from .calcores.pshe.shift import BGGH, BGIF, GHCalculation, IFCalculation
from .calcores.superlattices.twisted_gra import (
    ContiTBG,
    EffABt,
    SKPars,
    TightAAtTTG,
    TightABtTTG,
    TightAtATTG,
    TightAtBTTG,
    TightTBG,
)
