
# Equation for calculating black powder needed
# http://hararocketry.org/hara/resources/how-to-size-ejection-charge/
import numpy as np
import util.units as u
import util.environment as env
import util.environment_utils as env_util


# Configuration:
TARGET_PRESSURE = 12 # (psi) The target pressure to achieve seperation. "Typical pressure range is from 8-16 psi"

SEPERATION_ALTITUDE = u.Measurement(900, u.Unit.FEET)
LOWER_DEPLOY_ALTITUDE = u.Measurement(900, u.Unit.FEET)
UPPER_DEPLOY_ALTITUDE = u.Measurement(8000, u.Unit.FEET)

LAUNCH_ALTITUDE = u.Measurement(0, u.Unit.FEET)

# Rocket dimensions
AIRFRAME_DIAMETER = u.Measurement(3, u.Unit.INCHES)
SEPERATION_CLEARANCE_LENGTH = u.Measurement(3, u.Unit.INCHES)
UPPER_BAY_LENGTH = u.Measurement(17, u.Unit.INCHES)
LOWER_BAY_LENGTH = u.Measurement(12.2, u.Unit.INCHES)

# Constants
R = 266 # gas constant (inches * lbf / lbm)

# Calculation =============

environment = env.Environment(LAUNCH_ALTITUDE, env_util.WindModelConstant(u.Measurement(0)))

def K_to_R(kelvin: float) -> float:
    """Kelvin to Rankine converter"""
    return kelvin * 1.8


airframe_cross_section_area = np.pi * (AIRFRAME_DIAMETER.inches()/2)**2 # (m^2)

print(airframe_cross_section_area)

seperation_temperature = K_to_R(environment.get_temperature(SEPERATION_ALTITUDE))
lower_deploy_temperature = K_to_R(environment.get_temperature(LOWER_DEPLOY_ALTITUDE))
upper_deploy_temperature = K_to_R(environment.get_temperature(UPPER_DEPLOY_ALTITUDE))


seperation_area_volume: u.Measurement = SEPERATION_CLEARANCE_LENGTH * airframe_cross_section_area
upper_bay_volume: u.Measurement = UPPER_BAY_LENGTH * airframe_cross_section_area
lower_bay_volume: u.Measurement = LOWER_BAY_LENGTH * airframe_cross_section_area

seperation_area_volume = u.Measurement(31.762, u.Unit.INCHES)

GRAMS_TO_LB = 454

powder_amount_seperation = ((TARGET_PRESSURE * seperation_area_volume.inches()) / (R * seperation_temperature)) * GRAMS_TO_LB
powder_amount_lower = ((TARGET_PRESSURE * lower_bay_volume.inches()) / (R * lower_deploy_temperature)) * GRAMS_TO_LB
powder_amount_upper = ((TARGET_PRESSURE * upper_bay_volume.inches()) / (R * upper_deploy_temperature)) * GRAMS_TO_LB

print('BP needed for staging separation: {:.3f}g'.format(powder_amount_seperation),)
print('BP needed for lower stage separation: {:.3f}g'.format(powder_amount_lower))
print('BP needed for upper stage separation: {:.3f}g'.format(powder_amount_upper))