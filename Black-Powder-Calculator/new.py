# Equation for calculating black powder needed
# http://hararocketry.org/hara/resources/how-to-size-ejection-charge/
import numpy as np
import util.units as u
import util.environment as env
import util.environment_utils as env_util

# Configuration:
TARGET_PRESSURE = 12 # (psi) The target pressure to achieve seperation. "Typical pressure range is from 8-16 psi"

SEPERATION_ALTITUDE = u.Measurement(2000, u.Unit.FEET) # Altitude (approximate AGL) at which seperation will take place
LOWER_DEPLOY_ALTITUDE = u.Measurement(9829, u.Unit.FEET) # Altitude (approximate AGL) at which lower stage deployment will take place
UPPER_DEPLOY_ALTITUDE = u.Measurement(30000, u.Unit.FEET) # Altitude (approximate AGL) at which upper stage deployment will take place

LAUNCH_ALTITUDE = u.Measurement(1257, u.Unit.FEET) # Altitude of launch site (above sea level)

# Rocket dimensions
AIRFRAME_DIAMETER = u.Measurement(4, u.Unit.INCHES) # Assuming the rocket to be a perfect cylinder, the diameter of the cylinder
SEPERATION_CLEARANCE_LENGTH = u.Measurement(4, u.Unit.INCHES) # How long the interstage coupler is
UPPER_BAY_LENGTH = u.Measurement(14.5, u.Unit.INCHES) # How long the upper stage recovery bay is
LOWER_BAY_LENGTH = u.Measurement(14.5, u.Unit.INCHES) # How long the lower stage recovery bay is

# Constants
R = 266 # gas constant (inches * lbf / lbm)

# ============= Calculation [Do not modify beyond this line] =============
environment = env.Environment(LAUNCH_ALTITUDE, env_util.WindModelConstant(u.Measurement(0))) # Set up launch env

def K_to_R(kelvin: float) -> float:
    """Kelvin to Rankine converter"""
    return kelvin * 1.8

airframe_cross_section_area = np.pi * (AIRFRAME_DIAMETER.inches()/2)**2 # (in^2)

seperation_temperature = K_to_R(environment.get_temperature(SEPERATION_ALTITUDE)) # Temp (in Rankine) of ambient temp at seperation altitude
lower_deploy_temperature = K_to_R(environment.get_temperature(LOWER_DEPLOY_ALTITUDE)) # Temp (in Rankine) of ambient temp at 1st stage recovery deployment altitude
upper_deploy_temperature = K_to_R(environment.get_temperature(UPPER_DEPLOY_ALTITUDE)) # Temp (in Rankine) of ambient temp at 2nd stage recovery deployment altitude

# Calculate volumes of the 3 bays
seperation_area_volume: u.Measurement = SEPERATION_CLEARANCE_LENGTH * airframe_cross_section_area
upper_bay_volume: u.Measurement = UPPER_BAY_LENGTH * airframe_cross_section_area
lower_bay_volume: u.Measurement = LOWER_BAY_LENGTH * airframe_cross_section_area

GRAMS_TO_LB = 454 # Conversion factor

# Calculate ideal powder amounts
powder_amount_seperation = ((TARGET_PRESSURE * seperation_area_volume.inches()) / (R * seperation_temperature)) * GRAMS_TO_LB
powder_amount_lower = ((TARGET_PRESSURE * lower_bay_volume.inches()) / (R * lower_deploy_temperature)) * GRAMS_TO_LB
powder_amount_upper = ((TARGET_PRESSURE * upper_bay_volume.inches()) / (R * upper_deploy_temperature)) * GRAMS_TO_LB

print(f'[Interstage]  BP: {powder_amount_seperation:.3f}g  ({TARGET_PRESSURE}psi @ {SEPERATION_ALTITUDE})')
print(f'[Booster Stage Deploy]  BP: {powder_amount_lower:.3f}g  ({TARGET_PRESSURE}psi @ {LOWER_DEPLOY_ALTITUDE})')
print(f'[Sustainer Stage Deploy]  BP: {powder_amount_upper:.3f}g  ({TARGET_PRESSURE}psi @ {UPPER_DEPLOY_ALTITUDE})')