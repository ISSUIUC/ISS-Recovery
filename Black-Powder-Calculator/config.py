# Configuration file for the Recovery black powder calculation
import numpy as np
import util.units as u
import util.environment as env
import util.environment_utils as env_util

# Configuration:
TARGET_PRESSURE_INTERSTAGE = 16 # (psi) The target pressure to achieve seperation. "Typical pressure range is from 8-16 psi"
TARGET_PRESSURE_DEPLOY = 16 # (psi) Target pressure to deploy parachtute

# Rocket dimensions
AIRFRAME_DIAMETER = u.Measurement(3.75, u.Unit.INCHES) # Assuming the rocket to be a perfect cylinder, the diameter of the cylinder
SEPERATION_CLEARANCE_LENGTH = u.Measurement(3.875, u.Unit.INCHES) # How long the interstage coupler is
UPPER_BAY_LENGTH = u.Measurement(13.5, u.Unit.INCHES) # How long the upper stage recovery bay is
LOWER_BAY_LENGTH = u.Measurement(13.5, u.Unit.INCHES) # How long the lower stage recovery bay is

# Environment
SEPERATION_ALTITUDE = u.Measurement(2830, u.Unit.FEET) # Altitude (approximate AGL) at which seperation will take place
LOWER_DEPLOY_ALTITUDE = u.Measurement(9829, u.Unit.FEET) # Altitude (approximate AGL) at which lower stage deployment will take place
UPPER_DEPLOY_ALTITUDE = u.Measurement(37530, u.Unit.FEET) # Altitude (approximate AGL) at which upper stage deployment will take place
LAUNCH_ALTITUDE = u.Measurement(1257, u.Unit.FEET) # Altitude of launch site (above sea level)

# The following parameters do not affect the simulation! All seperation information is encoded in the TARGET_PRESSURE variable above !!
SHEAR_PIN_COUNT = 4
SHEAR_PIN_FORCE = 40.12 # in lbf
# The two variables above are are only for sanity checking!

# RCM parameters (For calculating bp burn efficiency)
RCM_VOLUME: float = (np.pi * (1)) * 10.9375 # in^3 (Values from seongyong)

# Constants
R = 266 # gas constant (inches * lbf / lbm)
BP_GAS_TEMPERATURE = 3307 # Temperature (Rankine) of combusted black powder gas