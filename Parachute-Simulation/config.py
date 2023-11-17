import util.units as u

ROCKET_MASS = u.MassMeasurement(40, u.UMass.LB) # Mass of the rocket
LAUNCH_SITE_ALTITUDE = u.Measurement(1000, u.Unit.FEET) # Altitude of the launch site
APOGEE_ALTITUDE = u.Measurement(10, u.Unit.KILOMETERS) # Apogee deployment altitude
MAIN_ALTITUDE = u.Measurement(2000, u.Unit.FEET) # Main parachute deployment altitude
WIND_SPEED = u.Measurement(9, u.Unit.MILES).per(u.UTime.HOUR) # Wind speed

DROGUE_DIAMETER = u.Measurement(13.72, u.Unit.INCHES)
MAIN_DIAMETER = u.Measurement(47, u.Unit.INCHES)

# DROGIE_DIAMETER = None
# MAIN_DIAMETER = None

# Parachute parameters
DROGUE_DRAG_COEFF = 1.4 # C_d of the drogue parachute (DRIFT: NO EFFECT)
MAIN_DRAG_COEFF = 1.8 # C_d of the main parachute (DRIFT: NO EFFECT)

# LIMITS
MAXIMUM_PARACHUTE_FORCE_LIMIT = 8000 # Maximum force a parachute (mainly shockcord) can experience before breaking.
"""Unlimited"""

# Target values
TARGET_DROGUE_DESCENT = u.Measurement(80, u.Unit.FEET).per(u.UTime.SECOND) # Target drogue descent velocity
TARGET_LANDING_VEL = u.Measurement(20, u.Unit.FEET).per(u.UTime.SECOND) # Target velocity when hitting the ground

# ==== DRIFT SIMULATION PARAMETERS ====
ANALYSIS_TIMESTEP = 0.05 # Drift simulation timestep

# Output configuration
OUTPUT_UNITS = u.Unit.INCHES
DRIFT_UNITS = u.Unit.KILOMETERS