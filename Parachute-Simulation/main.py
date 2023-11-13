# ISS recovery parachute sim
import util.parachute as parachute
import util.units as m
import util.environment as environment
import config

launch_site = environment.Environment(config.LAUNCH_SITE_ALTITUDE, config.WIND_SPEED)


# drogue
drogue_radius = parachute.ParachuteCalculation.calculate_radius_max_descent_vel(config.ROCKET_MASS, config.DROGUE_DRAG_COEFF, launch_site, config.MAIN_ALTITUDE, config.TARGET_DROGUE_DESCENT)
print("\n=== DROGUE ===")
print("To achieve a drogue descent velocity of " + str(config.TARGET_DROGUE_DESCENT) + ":")
# For proper outputting
drogue_radius.set_unit(config.OUTPUT_UNITS)
print("Parachute radius: " + str(drogue_radius))
print()

# main
main_radius = parachute.ParachuteCalculation.calculate_radius_landing(config.ROCKET_MASS, config.MAIN_DRAG_COEFF, launch_site, config.TARGET_LANDING_VEL)
print("=== MAIN ===")
print("To achieve a landing velocity of " + str(config.TARGET_LANDING_VEL) + ":")
# For proper outputting
main_radius.set_unit(config.OUTPUT_UNITS)
print("Parachute radius: " + str(main_radius))

print("\nperforming drift analysis...")
# Drift analysis
drogue = parachute.Parachute(config.DROGUE_DRAG_COEFF, drogue_radius, config.ROCKET_MASS)
main = parachute.Parachute(config.MAIN_DRAG_COEFF, main_radius, config.ROCKET_MASS)

drift_drogue = drogue.get_drift(config.ANALYSIS_TIMESTEP, config.APOGEE_ALTITUDE, config.MAIN_ALTITUDE, launch_site)
drift_main = main.get_drift(config.ANALYSIS_TIMESTEP, config.MAIN_ALTITUDE, m.Measurement(0), launch_site)
total_drift = drift_drogue + drift_main

total_drift.set_unit(config.DRIFT_UNITS)

print("=== DRIFT ANALYSIS ===")
print("DROGUE will drift ", drift_drogue, "  from the launch site")
print("MAIN will drift ", drift_main, "  from the launch site")
print("\nThe total drift will be", total_drift)
print()