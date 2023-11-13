import util.units as u

ROCKET_MASS = u.MassMeasurement(40, u.UMass.LB)
"""Mass of the rocket"""
LAUNCH_SITE_ALTITUDE = u.Measurement(1000, u.Unit.FEET)
"""Altitude of the launch site"""
APOGEE_ALTITUDE = u.Measurement(30000, u.Unit.FEET)
"""Altitude at which the apogee parachute is deployed"""
MAIN_ALTITUDE = u.Measurement(2000, u.Unit.FEET)
"""Altitude at which the main parachute is deployed"""
WIND_SPEED = u.Measurement(9, u.Unit.MILES).per(u.UTime.HOUR)

# Parachute parameters
DROGUE_DRAG_COEFF = 1.4
"""C_D of the drogue"""
MAIN_DRAG_COEFF = 1.8
"""C_D of the main"""

# Target values
TARGET_DROGUE_DESCENT = u.Measurement(80, u.Unit.FEET).per(u.UTime.SECOND)
"""Target drogue descent velocity"""

TARGET_LANDING_VEL = u.Measurement(20, u.Unit.FEET).per(u.UTime.SECOND)
"""Target landing velocity"""

# ==== DRIFT SIMULATION PARAMETERS ====
ANALYSIS_TIMESTEP = 0.05


# Output configuration
OUTPUT_UNITS = u.Unit.INCHES
DRIFT_UNITS = u.Unit.KILOMETERS