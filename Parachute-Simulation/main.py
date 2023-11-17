# ISS recovery parachute sim
import util.parachute as parachute
import util.units as m
import util.environment as environment
import config

import matplotlib.pyplot as plt
import numpy as np

launch_site = environment.Environment(config.LAUNCH_SITE_ALTITUDE, config.WIND_SPEED)

class LimitExceededException(Exception):
    """Exception raised for exceeded limits"""
    def __init__(self, message="Limit exceeded (Unknown)"):
        super().__init__(message)

# drogue
print("\n=== DROGUE ===")
if not config.DROGIE_DIAMETER:
    drogue_radius = parachute.ParachuteCalculation.calculate_radius_max_descent_vel(config.ROCKET_MASS, config.DROGUE_DRAG_COEFF, launch_site, config.MAIN_ALTITUDE, config.TARGET_DROGUE_DESCENT)
    print("To achieve a drogue descent velocity of " + str(config.TARGET_DROGUE_DESCENT) + ":")
else:
    drogue_radius = config.DROGIE_DIAMETER/2
# For proper outputting
drogue_radius.set_unit(config.OUTPUT_UNITS)
print("Parachute radius: " + str(drogue_radius))
print()

# main
print("=== MAIN ===")
if not config.MAIN_DIAMETER:
    main_radius = parachute.ParachuteCalculation.calculate_radius_landing(config.ROCKET_MASS, config.MAIN_DRAG_COEFF, launch_site, config.TARGET_LANDING_VEL)
    print("To achieve a landing velocity of " + str(config.TARGET_LANDING_VEL) + ":")
else:
    main_radius = config.MAIN_DIAMETER/2
# For proper outputting
main_radius.set_unit(config.OUTPUT_UNITS)
print("Parachute radius: " + str(main_radius))

drogue = parachute.Parachute(config.DROGUE_DRAG_COEFF, drogue_radius, config.ROCKET_MASS)
main = parachute.Parachute(config.MAIN_DRAG_COEFF, main_radius, config.ROCKET_MASS)

# Check parachute limits
# drogue limit
print()
force_on_drogue = drogue.calculate_drag(launch_site.get_density(config.APOGEE_ALTITUDE), drogue.get_terminal_velocity(config.APOGEE_ALTITUDE, launch_site))
if force_on_drogue > config.MAXIMUM_PARACHUTE_FORCE_LIMIT:
    raise LimitExceededException(f"DROGUE force limit exceeded ({force_on_drogue} N > {config.MAXIMUM_PARACHUTE_FORCE_LIMIT} N)")
else:
    print(f"DROGUE force OK ({force_on_drogue} N)")
# main limit
force_on_main = main.calculate_drag(launch_site.get_density(config.MAIN_ALTITUDE), drogue.get_terminal_velocity(config.MAIN_ALTITUDE, launch_site))
if force_on_main > config.MAXIMUM_PARACHUTE_FORCE_LIMIT:
    raise LimitExceededException(f"MAIN force limit exceeded ({force_on_main} N > {config.MAXIMUM_PARACHUTE_FORCE_LIMIT} N)")
else:
    print(f"MAIN force OK ({force_on_main} N)")
print()

# Drift analysis

m_term =  main.get_terminal_velocity(m.Measurement(0), launch_site)
d_vel_at_main_deploy =  drogue.get_terminal_velocity(config.MAIN_ALTITUDE, launch_site)
d_vel_max =  drogue.get_terminal_velocity(config.APOGEE_ALTITUDE, launch_site)


# Calculate drift

drift_list = []
timestamp_list = []

drift_drogue = drogue.get_drift(config.ANALYSIS_TIMESTEP, config.APOGEE_ALTITUDE, config.MAIN_ALTITUDE, launch_site, m.Measurement(0).per(m.UTime.SECOND), 0)
drift_main = main.get_drift(config.ANALYSIS_TIMESTEP, config.MAIN_ALTITUDE, m.Measurement(0), launch_site, d_vel_at_main_deploy, drift_drogue.time)
print()
total_drift = drift_drogue.drift + drift_main.drift

total_drift.set_unit(config.DRIFT_UNITS)

print("=== DRIFT ANALYSIS ===")
print("DROGUE will drift ", drift_drogue.drift, "  from the launch site")
print("> DROGUE maximum velocity", drift_drogue.maximum_velocity.set_unit(m.Unit.FEET))
print("> DROGUE velocity at main deploy", d_vel_at_main_deploy.set_unit(m.Unit.FEET))
print("MAIN will drift ", drift_main.drift, " from the launch site")
print("> MAIN landing velocity: ", m_term.set_unit(m.Unit.FEET))
print("> Maximum possible force on MAIN at deployment: ", force_on_main, "N")
print("\nThe total drift will be", total_drift)
print()

total_timestamp_list = drift_drogue.ts_list + drift_main.ts_list
total_vel_list = drift_drogue.v_list + drift_main.v_list

fig, ax = plt.subplots()
ax.plot(total_timestamp_list, total_vel_list)

ax.set(xlabel='time (s)', ylabel='velocity (m/s)',
       title='Velocity vs time')

ax.vlines(len(drift_drogue.ts_list)*config.ANALYSIS_TIMESTEP, ymin=0, ymax=drift_drogue.maximum_velocity.m(), linestyles='dashed')
ax.text(x=len(drift_drogue.ts_list)*config.ANALYSIS_TIMESTEP+2, y=drift_drogue.maximum_velocity.m(), s="Main Deploy")

ax.vlines(0, ymin=0, ymax=drift_drogue.maximum_velocity.m(), linestyles='dashed')
ax.text(x=0+2, y=drift_drogue.maximum_velocity.m(), s="Drogue Deploy")

ax.grid()

fig.savefig("test.png")
plt.show()