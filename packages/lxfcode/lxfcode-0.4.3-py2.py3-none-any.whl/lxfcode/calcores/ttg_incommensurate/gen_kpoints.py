import numpy as np
import matplotlib.pyplot as plt

from ..materials import SLGra


def main():
    slgInst = SLGra()
    print(slgInst.K0)


if __name__ == "__main__":
    main()
