# Equation for calculating black powder needed
# http://hararocketry.org/hara/resources/how-to-size-ejection-charge/
import numpy as np
import util.units as u
import util.environment as env
import util.environment_utils as env_util
import util.rocket_util as rocket
import util.calculation as calc
import config

sim_warnings: str = [] # Warnings that the simulation should throw
environment = env.Environment(config.LAUNCH_ALTITUDE, env_util.WindModelConstant(u.Measurement(0))) # Set up launch env
"""Sets up the launch environment, wind model is redundant."""

airframe_cross_section_area: float = np.pi * (config.AIRFRAME_DIAMETER.inches()/2)**2 # (in^2)
shear_pin_force: float = config.SHEAR_PIN_COUNT * config.SHEAR_PIN_FORCE # (lbf)

seperation_temperature = u.K_to_R(environment.get_temperature(config.SEPERATION_ALTITUDE)) # Temp (in Rankine) of ambient temp at seperation altitude
lower_deploy_temperature = u.K_to_R(environment.get_temperature(config.LOWER_DEPLOY_ALTITUDE)) # Temp (in Rankine) of ambient temp at 1st stage recovery deployment altitude
upper_deploy_temperature = u.K_to_R(environment.get_temperature(config.UPPER_DEPLOY_ALTITUDE)) # Temp (in Rankine) of ambient temp at 2nd stage recovery deployment altitude

seperation_stage = rocket.Stage("INTERSTAGE", airframe_cross_section_area, config.SEPERATION_CLEARANCE_LENGTH.inches(), default_pressure=config.TARGET_PRESSURE_INTERSTAGE)
seperation_stage.add_sim("\x1b[90mAbsolute Lower bound (Best case)\x1b[0m", config.BP_GAS_TEMPERATURE)
seperation_stage.add_sim("\x1b[90mAbsolute Upper bound (Worst case)\x1b[0m", seperation_temperature)

lower_stage = rocket.Stage("DEPLOYMENT BAY", airframe_cross_section_area, config.LOWER_BAY_LENGTH.inches(), default_pressure=config.TARGET_PRESSURE_DEPLOY)
lower_stage.add_sim("\x1b[90mAbsolute Lower bound (Best case)\x1b[0m", config.BP_GAS_TEMPERATURE)
lower_stage.add_sim("\x1b[90mAbsolute Upper bound (Worst case)\x1b[0m", lower_deploy_temperature)

print(f"[[ BP Calculation results ]]")
print(f"(Shear pins) {config.SHEAR_PIN_COUNT} shear pins @ {config.SHEAR_PIN_FORCE}lbf (each)")

if((config.TARGET_PRESSURE_DEPLOY * airframe_cross_section_area) < shear_pin_force):
    sim_warnings.append(f"config.TARGET_PRESSURE_DEPLOY is less than the required pressure to break shear pins! ({shear_pin_force:.2f}lbf > {(config.TARGET_PRESSURE_DEPLOY * airframe_cross_section_area):.2f}lbf) Lower stage will NOT deploy!")

print(f"(Forces) Interstage pressure: {config.TARGET_PRESSURE_INTERSTAGE}psi)")
print(f"(Forces) Deployment pressure: {config.TARGET_PRESSURE_DEPLOY}psi)")

print("\n==== RCM efficiency calculation ====") # This section calculates efficiency values given particular values from RCM testing.
efficiency_40k = calc.RCMEfficiencyCalculation(config.RCM_VOLUME)
efficiency_40k.add_sim(1, 1.04608, 0.166255)
efficiency_40k.add_sim(1, 1.111924, 0.180069)

efficiency_30k = calc.RCMEfficiencyCalculation(config.RCM_VOLUME)
efficiency_30k.add_sim(1, 1.540406, 0.284719)

avg_efficiency_40k = efficiency_40k.get_average_efficiency()
print(f"\nAverage bp efficiency (40k): {(avg_efficiency_40k*100):.2f}%")

avg_efficiency_30k = efficiency_30k.get_average_efficiency()
print(f"Average bp efficiency (30k): {(avg_efficiency_30k*100):.2f}%")
print()

lower_stage.add_sim(f"\x1b[32mBEST GUESS 40k (rcm @ {(avg_efficiency_40k*100):.2f}%)\x1b[0m", config.BP_GAS_TEMPERATURE, efficiency=avg_efficiency_40k)
seperation_stage.add_sim(f"\x1b[32mBEST GUESS 40k (rcm @ {(avg_efficiency_40k*100):.2f}%)\x1b[0m", config.BP_GAS_TEMPERATURE, efficiency=avg_efficiency_40k)

lower_stage.add_sim(f"\x1b[32mBEST GUESS 30k (rcm @ {(avg_efficiency_30k*100):.2f}%)\x1b[0m", config.BP_GAS_TEMPERATURE, efficiency=avg_efficiency_30k)
seperation_stage.add_sim(f"\x1b[32mBEST GUESS 30k (rcm @ {(avg_efficiency_30k*100):.2f}%)\x1b[0m", config.BP_GAS_TEMPERATURE, efficiency=avg_efficiency_30k)

print(seperation_stage)
print(lower_stage)

# Print errors
for warning in sim_warnings:
    print("\x1b[33m(WARN): " + warning + "\x1b[0m")