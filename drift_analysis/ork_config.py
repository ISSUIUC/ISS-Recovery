
from logging import config


LATITUDE             = 35.347538
LONGITUDE            = -117.809397
LAUNCH_SITE_ALTITUDE = 610

ALTITUDE_TIMESTEP    = 100

SUSTAINER_CSV        = "openrocket_sustainer.csv"
BOOSTER_CSV          = "openrocket_booster.csv"

SUS_MASS             = 8.38
SUS_CD               = 1.1
SUS_CHUTE_DIAMETER   = 1.552
SUS_REEF_RATIO       = 0.1
SUS_MAIN_DEPLOY_ALT  = 305

BOO_MASS             = 13.37
BOO_CD               = 1.1
BOO_CHUTE_DIAMETER   = 1.747
BOO_REEF_RATIO       = 0.1
BOO_MAIN_DEPLOY_ALT  = 305

APOGEE_OFFSET        = 3218.4

MC_RUNS              = 500
MC_WIND_SPEED_SIGMA  = 0.12
MC_WIND_DIR_SIGMA    = 8.0
MC_CD_SIGMA          = 0.07
MC_MASS_SIGMA        = 0.03
MC_APOGEE_SIGMA      = 150.0
MC_MAIN_ALT_SIGMA    = 50.0
MC_REEF_SIGMA        = 0.01
MC_APO_XY_SIGMA      = 75.0
M_PER_DEG_LAT = 111_320.0