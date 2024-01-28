import util.units as u
import util.parachute_utils as putil
import util.environment_utils as eutil

# Sustainer dry mass: 19.8 lbs
# Booster dry mass: 13.7 lbs
# Sustainer wet mass: 35.3 lbs
# Booster wet mass: 50.7 lbs
# Use DRY MASS since motor will have burned

ROCKET_MASS = u.MassMeasurement(19.8, u.UMass.LB) # Mass of the rocket
LAUNCH_SITE_ALTITUDE = u.Measurement(1250, u.Unit.FEET) # Altitude of the launch site
APOGEE_ALTITUDE = u.Measurement(39000, u.Unit.FEET) # Apogee deployment altitude
MAIN_ALTITUDE = u.Measurement(2000, u.Unit.FEET) # Main parachute deployment altitude

# WIND_MODEL = eutil.WindModelConstant(u.Measurement(9, u.Unit.MILES).per(u.UTime.HOUR))
WIND_MODEL = eutil.WindModelConstant(u.Measurement(12, u.Unit.MILES).per(u.UTime.HOUR))
# WIND_SPEED = u.Measurement(9, u.Unit.MILES).per(u.UTime.HOUR) # Wind speed


# DROGUE_DIAMETER = None
# MAIN_DIAMETER = None

DROGUE_DIAMETER = u.Measurement(20, u.Unit.INCHES)
MAIN_DIAMETER = u.Measurement(60, u.Unit.INCHES)



# Parachute parameters
DROGUE_DRAG_COEFF = 2 # C_d of the drogue parachute (DRIFT: NO EFFECT)
MAIN_DRAG_COEFF = 2 # C_d of the main parachute (DRIFT: NO EFFECT)
DROGUE_T_FILL = 1 # Fill time for DROGUE
MAIN_T_FILL = 1 # Fill time for MAIN
DROGUE_FILL_CHAR_FUNCTION = putil.OpeningFunction.NATURAL
MAIN_FILL_CHAR_FUNCTION = putil.OpeningFunction.NATURAL

# LIMITS
MAXIMUM_PARACHUTE_FORCE_LIMIT = 800 # lbf, Maximum force the parachute system can endure (force tolerance of weakest part connected to the chute system)

# Target values
TARGET_DROGUE_DESCENT = u.Measurement(75, u.Unit.FEET).per(u.UTime.SECOND) # Target drogue descent velocity
TARGET_LANDING_VEL = u.Measurement(26, u.Unit.FEET).per(u.UTime.SECOND) # Target velocity when hitting the ground

# ==== DRIFT SIMULATION PARAMETERS ====
ANALYSIS_TIMESTEP = 0.05 # Drift simulation timestep (Default 0.05)
DYNAMIC_TIMESTEP_RANGE = u.Measurement(80, u.Unit.METERS) # What range above/below critical events should the timestep be lowered?
FINE_ANALYSIS_TIMESTEP = 0.001 # Default 0.001

# ==== MONTE CARLO PARAMETERS ====
OPENING_SHOCK_FACTOR = 2 # Ck, from opening shock calculation (dimensionless)
DEPLOY_DELAY_MAXIMUM = 15 # seconds
DEPLOY_DELAY_FINENESS = 0.2 # The intervals to use for the monte carlo simulation

# Output configuration
OUTPUT_UNITS = u.Unit.INCHES
LAND_SPEED_UNITS = u.Unit.FEET # per second
DRIFT_UNITS = u.Unit.KILOMETERS
OUTPUT_SHOCK_FILE = "march_sustainer_39kft"
OUTPUT_MONTECARLO_FILE = "monte_carlo_39kft"