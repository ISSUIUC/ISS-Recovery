# ISS recovery parachute sim
import util.parachute as parachute
import util.units as m
import util.environment as environment
import config

import matplotlib.pyplot as plt
import numpy as np

launch_site = environment.Environment(config.LAUNCH_SITE_ALTITUDE, config.WIND_MODEL)

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
m_term =  main.get_terminal_velocity(m.Measurement(0), launch_site, other_parachutes=[drogue])
d_vel_at_main_deploy =  drogue.get_terminal_velocity(config.MAIN_ALTITUDE, launch_site)
d_vel_max =  drogue.get_terminal_velocity(config.APOGEE_ALTITUDE, launch_site)

# Calculate drift

drift_list = []
timestamp_list = []

drift_drogue = drogue.get_drift(config.ANALYSIS_TIMESTEP, config.APOGEE_ALTITUDE, config.MAIN_ALTITUDE, launch_site, m.Measurement(0).per(m.UTime.SECOND), 0, [], parachute.DriftMonteCarloParameters(0), main)
main_deploy_velocity = drift_drogue.v_list[len(drift_drogue.v_list) - 1]
drift_main = main.get_drift(config.ANALYSIS_TIMESTEP, config.MAIN_ALTITUDE, m.Measurement(0), launch_site, m.Measurement(main_deploy_velocity).per(m.UTime.SECOND), drift_drogue.time, [drogue])
print()
total_drift = drift_drogue.drift + drift_main.drift

total_drift.set_unit(config.DRIFT_UNITS)

main_final_velocity_fl = drift_main.v_list[len(drift_main.v_list) - 1]
main_avg_velocity = m.Measurement(drift_main.steady_state_velocity).per(m.UTime.SECOND).set_unit(config.LAND_SPEED_UNITS)
main_final_vel = m.Measurement(main_final_velocity_fl).per(m.UTime.SECOND).set_unit(config.LAND_SPEED_UNITS)

print("=== FORCE ANALYSIS (non monte-carlo) ===")
print(f"DROGUE will experience a maximum force of {drift_drogue.max_force * config.OPENING_SHOCK_FACTOR} N")
print(f"MAIN will experience a maximum force of {drift_main.max_force * config.OPENING_SHOCK_FACTOR} N")
print()
print("=== DRIFT ANALYSIS ===")
print("DROGUE will drift ", drift_drogue.drift, "  from the launch site")
print("> DROGUE maximum velocity", drift_drogue.maximum_velocity.set_unit(m.Unit.FEET))
print("> DROGUE average velocity: ", m.Measurement(drift_drogue.steady_state_velocity).per(m.UTime.SECOND).set_unit(config.LAND_SPEED_UNITS))
print("> DROGUE velocity at main deploy", d_vel_at_main_deploy.set_unit(m.Unit.FEET))
print("MAIN will drift ", drift_main.drift, " from the launch site")
print("> MAIN landing velocity: ", main_final_vel)
print("> MAIN average velocity: ", main_avg_velocity)
print("\nThe total drift will be", total_drift)
print()



def plot_drift_simulation(drogue_result: parachute.DriftAnalysisResult, main_result: parachute.DriftAnalysisResult):
    total_timestamp_list = drogue_result.ts_list + main_result.ts_list
    total_vel_list = drogue_result.v_list + main_result.v_list
    total_alt_list = drogue_result.alt_list + main_result.alt_list
    

    fig = plt.figure("Velocity graph")
    plt.plot(total_timestamp_list, total_vel_list)
    # ax.plot(total_timestamp_list, total_alt_list)
    plt.xlabel("time (s)")
    plt.ylabel("velocity (m/s)")
    plt.title("Velocity vs time")

    if(main_result.is_monte_carlo):
        plt.vlines(drogue_result.time, ymin=0, ymax=drogue_result.maximum_velocity.m(), linestyles='dashed')
        plt.text(x=drogue_result.time + 1, y=drogue_result.maximum_velocity.m(), s="Main Deploy (expected)")
        plt.vlines(drogue_result.time + main_result.monte_carlo_params.ejection_delay, ymin=0, ymax=drogue_result.maximum_velocity.m(), linestyles='dashed', color="red")
        plt.text(x=drogue_result.time + main_result.monte_carlo_params.ejection_delay + 1, y=drogue_result.maximum_velocity.m()*0.95, s="Main Deploy (actual)", color="red")
    else:
        plt.vlines(drogue_result.time, ymin=0, ymax=drogue_result.maximum_velocity.m(), linestyles='dashed')
        plt.text(x=drogue_result.time + 1, y=drogue_result.maximum_velocity.m(), s="Main Deploy")

    
    if(drogue_result.is_monte_carlo):
        plt.vlines(0, ymin=0, ymax=drogue_result.maximum_velocity.m(), linestyles='dashed')
        plt.text(x=0+1, y=drogue_result.maximum_velocity.m(), s="Drogue Deploy (expected)")
        plt.vlines(drogue_result.monte_carlo_params.ejection_delay, ymin=0, ymax=drogue_result.maximum_velocity.m(), linestyles='dashed', color="red")
        plt.text(x=drogue_result.monte_carlo_params.ejection_delay+1, y=drogue_result.maximum_velocity.m()*0.95, s="Drogue Deploy (actual)", color="red")
    else:
        plt.vlines(0, ymin=0, ymax=drogue_result.maximum_velocity.m(), linestyles='dashed')
        plt.text(x=0+1, y=drogue_result.maximum_velocity.m(), s="Drogue Deploy")

    plt.grid()

    fig = plt.figure("Disreef shock")
    plt.plot(drogue_result.ts_list, drogue_result.disreef_forces)

    plt.xlabel("time (s)")
    plt.ylabel("Disreef shock (lbf)")
    plt.title("Disreef shock vs time")


    plt.show()

plot_drift_simulation(drift_drogue, drift_main)

# ============== MONTE CARLO ==============
print("=== Monte carlo ===")

max_force_drogue_list = [drift_drogue.max_force * config.OPENING_SHOCK_FACTOR]
max_force_main_list = [drift_main.max_force * config.OPENING_SHOCK_FACTOR]
drogue_results = [drift_drogue]
main_results = [drift_main]
max_force_timestamp_list = [0]
cur_deploy_delay: float = config.DEPLOY_DELAY_FINENESS # We calculated 0s, skip it.
while cur_deploy_delay <= config.DEPLOY_DELAY_MAXIMUM:
    # Run simulation
    
    d_result = drogue.get_drift(config.ANALYSIS_TIMESTEP, config.APOGEE_ALTITUDE, config.MAIN_ALTITUDE, launch_site, 
                                m.Measurement(0).per(m.UTime.SECOND), 0, [], parachute.DriftMonteCarloParameters(cur_deploy_delay))
    m_result = main.get_drift(config.ANALYSIS_TIMESTEP, config.MAIN_ALTITUDE, m.Measurement(0), launch_site, m.Measurement(main_deploy_velocity).per(m.UTime.SECOND),
                               drift_drogue.time, [drogue], parachute.DriftMonteCarloParameters(cur_deploy_delay))
    
    d_force = d_result.max_force * config.OPENING_SHOCK_FACTOR
    m_force = m_result.max_force * config.OPENING_SHOCK_FACTOR

    print(f"Sim [{cur_deploy_delay}]: (main: {m_force:.1f}N), (drogue: {d_force:.1f}N), added to analysis")
    # Add results
    max_force_drogue_list.append(m.N_to_lbf(d_force))
    max_force_main_list.append(m.N_to_lbf(m_force))
    max_force_timestamp_list.append(cur_deploy_delay)
    drogue_results.append(d_result)
    main_results.append(m_result)
    
    # Propagate monte-carlo
    cur_deploy_delay += config.DEPLOY_DELAY_FINENESS

print("Monte carlo analysis complete.")

# Plot shock vs time after deploy
fig = plt.figure("montecarlo-shock-plot")
plt.plot(max_force_timestamp_list, max_force_main_list, label="Main")
plt.plot(max_force_timestamp_list, max_force_drogue_list, label="Drogue")

plt.xlabel("deployment delay (s)")
plt.ylabel("Maximum shock during descent (lbf)")
plt.title("Opening shock vs deployment delay")

plt.grid()

plt.savefig("./monte_out/march-sustainer-50kft.png")

# Plot "3d" plot (all slices)
fig = plt.figure("montecarlo-slice-plot")

for i in range(len(main_results)):
    m_res = main_results[i]
    d_res = drogue_results[i]

    total_timestamp_list = d_res.ts_list + m_res.ts_list
    total_vel_list = d_res.v_list + m_res.v_list
    total_alt_list = d_res.alt_list + m_res.alt_list

    plt.plot(total_timestamp_list, total_vel_list, color=(i/len(main_results),0,0))


plt.show()
    

