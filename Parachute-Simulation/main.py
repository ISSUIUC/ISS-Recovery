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

# Opening characteristics
main_opening_characteristics = parachute.ParachuteOpeningCharacteristics(config.MAIN_FILL_CHAR_FUNCTION, config.MAIN_T_FILL)
drogue_opening_characteristics = parachute.ParachuteOpeningCharacteristics(config.DROGUE_FILL_CHAR_FUNCTION, config.DROGUE_T_FILL)

# drogue
print("\n=== DROGUE ===")
drogue = None
if not config.DROGUE_DIAMETER:
    drogue_radius = parachute.ParachuteCalculation.calculate_radius_max_descent_vel(config.ROCKET_MASS, config.DROGUE_DRAG_COEFF, launch_site, config.MAIN_ALTITUDE, config.TARGET_DROGUE_DESCENT)
    drogue = parachute.Parachute(config.DROGUE_DRAG_COEFF, drogue_radius, config.ROCKET_MASS, drogue_opening_characteristics)
    print("To achieve a drogue descent velocity of " + str(config.TARGET_DROGUE_DESCENT) + ":")
    print("Parachute diameter: " + str(drogue_radius.set_unit(config.OUTPUT_UNITS)*2.0))
else:
    drogue_radius = config.DROGUE_DIAMETER/2
    drogue = parachute.Parachute(config.DROGUE_DRAG_COEFF, drogue_radius, config.ROCKET_MASS, drogue_opening_characteristics)
    print("With a drogue parachute diameter of " + str(config.DROGUE_DIAMETER) + ":")
    print("Terminal drogue velocity at main deploy: " + str(drogue.get_terminal_velocity(config.MAIN_ALTITUDE, launch_site)))

# For proper outputting
print()

# main
print("=== MAIN ===")
if not config.MAIN_DIAMETER:
    main_radius = parachute.ParachuteCalculation.calculate_radius_landing(config.ROCKET_MASS, config.MAIN_DRAG_COEFF, launch_site, config.TARGET_LANDING_VEL)

    # main_radius stores the radius of a parachute needed to solely handle landing. We are deploying two chutes, so we 
    # need to account for that.
    print("To achieve a landing velocity of " + str(config.TARGET_LANDING_VEL) + ":")
    print("TOTAL required diameter: ", str(main_radius.set_unit(config.OUTPUT_UNITS)*2.0))
    main_radius = parachute.ParachuteCalculation.calculate_radius_with_other_chute(main_radius, drogue)

    main = parachute.Parachute(config.MAIN_DRAG_COEFF, main_radius, config.ROCKET_MASS, main_opening_characteristics)
    
    print("MAIN Parachute diameter: " + str(main_radius.set_unit(config.OUTPUT_UNITS)*2.0))
    print(f" > Additional parachute: DROGUE (diameter: {str(drogue_radius*2.0)})")
else:
    main_radius = config.MAIN_DIAMETER/2
    main = parachute.Parachute(config.MAIN_DRAG_COEFF, main_radius, config.ROCKET_MASS, main_opening_characteristics)
    print("With a main parachute diameter of " + str(config.MAIN_DIAMETER) + ":")
    print("Main terminal velocity at deploy: " + str(main.get_terminal_velocity(config.MAIN_ALTITUDE, launch_site)))
    print("Main terminal velocity at landing: " + str(main.get_terminal_velocity(m.Measurement(0, m.Unit.METERS), launch_site)))
# For proper outputting
print()
main_radius.set_unit(config.OUTPUT_UNITS)


# Drift analysis
m_term =  main.get_terminal_velocity(m.Measurement(0), launch_site)
d_vel_at_main_deploy =  drogue.get_terminal_velocity(config.MAIN_ALTITUDE, launch_site)
d_vel_max =  drogue.get_terminal_velocity(config.APOGEE_ALTITUDE, launch_site)


# Calculate drift

drift_list = []
timestamp_list = []

drift_drogue = drogue.get_drift(config.ANALYSIS_TIMESTEP, config.APOGEE_ALTITUDE, config.MAIN_ALTITUDE, launch_site, m.Measurement(0).per(m.UTime.SECOND), 0)
main_deploy_velocity = drift_drogue.v_list[len(drift_drogue.v_list) - 1]
drift_main = main.get_drift(config.ANALYSIS_TIMESTEP, config.MAIN_ALTITUDE, m.Measurement(0), launch_site, m.Measurement(main_deploy_velocity).per(m.UTime.SECOND), drift_drogue.time, [drogue])
print()
total_drift = drift_drogue.drift + drift_main.drift

total_drift.set_unit(config.DRIFT_UNITS)

main_final_velocity_fl = drift_main.v_list[len(drift_main.v_list) - 1]
main_final_vel = m.Measurement(main_final_velocity_fl).per(m.UTime.SECOND).set_unit(config.LAND_SPEED_UNITS)

print("=== FORCE ANALYSIS ===")
print(f"DROGUE will experience a maximum force of {drift_drogue.max_force} N")
print(f"MAIN will experience a maximum force of {drift_main.max_force} N")
print()
print("=== DRIFT ANALYSIS ===")
print("DROGUE will drift ", drift_drogue.drift, "  from the launch site")
print("> DROGUE maximum velocity", drift_drogue.maximum_velocity.set_unit(m.Unit.FEET))
print("> DROGUE velocity at main deploy", d_vel_at_main_deploy.set_unit(m.Unit.FEET))
print("MAIN will drift ", drift_main.drift, " from the launch site")
print("> MAIN landing velocity: ", main_final_vel)
print("\nThe total drift will be", total_drift)
print()

total_timestamp_list = drift_drogue.ts_list + drift_main.ts_list
total_vel_list = drift_drogue.v_list + drift_main.v_list
total_alt_list = drift_drogue.alt_list + drift_main.alt_list

fig, ax = plt.subplots()
ax.plot(total_timestamp_list, total_vel_list)
# ax.plot(total_timestamp_list, total_alt_list)

ax.set(xlabel='time (s)', ylabel='velocity (m/s)',
       title='Velocity vs time')

ax.vlines(drift_drogue.time, ymin=0, ymax=drift_drogue.maximum_velocity.m(), linestyles='dashed')
ax.text(x=drift_drogue.time + 2, y=drift_drogue.maximum_velocity.m(), s="Main Deploy")

ax.vlines(0, ymin=0, ymax=drift_drogue.maximum_velocity.m(), linestyles='dashed')
ax.text(x=0+2, y=drift_drogue.maximum_velocity.m(), s="Drogue Deploy")

ax.grid()

fig.savefig("test.png")
plt.show()