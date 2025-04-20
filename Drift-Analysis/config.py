import util.units as u
import util.parachute_utils as putil
import util.environment_utils as eutil

'===================================================================================='

# variables , global use
LAUNCH_SITE_ALTITUDE = u.Measurement(2000, u.Unit.FEET) # Altitude of the launch site
MAIN_ALTITUDE = u.Measurement(3000, u.Unit.FEET) # Main parachute deployment altitude
APOGEE_OFFSET = u.Measurement(1, u.Unit.FEET) # Used to simulate off-nominal deployment. "1" will simulate deployment at apogee.
DROGUE_DRAG_COEFF = 1.5 # C_d of the drogue parachute (DRIFT: NO EFFECT)
MAIN_DRAG_COEFF = 1.5 # C_d of the main parachute (DRIFT: NO EFFECT)
DROGUE_T_FILL = 1 # Fill time for DROGUE
MAIN_T_FILL = 1 # Fill time for MAIN

# variables, local use
ROCKET_MASS_BOOSTER = u.MassMeasurement(30.83, u.UMass.LB) # Mass of the rocket
ROCKET_MASS_SUSTAINER = u.MassMeasurement(16.75, u.UMass.LB) # Mass of the rocket

APOGEE_ALTITUDE_BOOSTER = u.Measurement(17000, u.Unit.FEET) # Apogee deployment altitude
APOGEE_ALTITUDE_SUSTAINER = u.Measurement(88000, u.Unit.FEET) # Apogee deployment altitude

DROGUE_DIAMETER_BOOSTER = u.Measurement(15, u.Unit.INCHES)
DROGUE_DIAMETER_SUSTAINER = u.Measurement(10, u.Unit.INCHES)
MAIN_DIAMETER_BOOSTER = u.Measurement(68, u.Unit.INCHES)
MAIN_DIAMETER_SUSTAINER = u.Measurement(53, u.Unit.INCHES)

'===================================================================================='


WIND_MODEL = eutil.WindModelConstant(u.Measurement(0, u.Unit.MILES).per(u.UTime.HOUR)) # OBSOLETE

DROGUE_FILL_CHAR_FUNCTION = putil.OpeningFunction.NATURAL
MAIN_FILL_CHAR_FUNCTION = putil.OpeningFunction.NATURAL

# ==== DRIFT SIMULATION PARAMETERS ====
ANALYSIS_TIMESTEP = 0.05 # Drift simulation timestep (Default 0.05)
DYNAMIC_TIMESTEP_RANGE = u.Measurement(80, u.Unit.METERS) # What range above/below critical events should the timestep be lowered?
FINE_ANALYSIS_TIMESTEP = 0.001 # Default 0.001

# Output configuration
OUTPUT_UNITS = u.Unit.INCHES
LAND_SPEED_UNITS = u.Unit.FEET # per second
DRIFT_UNITS = u.Unit.MILES
