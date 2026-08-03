import numpy as np
import sdatmospheric as sd

import constants as const

def descent_speed_drogue(chute_d, cd, mass, rho, reef_ratio):
    area = np.pi * (chute_d / 2) ** 2 * reef_ratio
    return np.sqrt(2 * mass * const.GRAVITY / (rho * cd * area))


def descent_speed_main(chute_d, cd, mass, rho):
    area = np.pi * (chute_d / 2) ** 2
    return np.sqrt(2 * mass * const.GRAVITY / (rho * cd * area))

def run_sim():
    """Main entry point into drift simulation"""

