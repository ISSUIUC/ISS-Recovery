# Equation for calculating black powder needed
# http://hararocketry.org/hara/resources/how-to-size-ejection-charge/
import numpy as np
import util.units as u
import util.environment as env
import util.environment_utils as env_util

# Configuration:
TARGET_PRESSURE = 12 # (psi) The target pressure to achieve seperation. "Typical pressure range is from 8-16 psi"

SEPERATION_ALTITUDE = u.Measurement(2830, u.Unit.FEET) # Altitude (approximate AGL) at which seperation will take place
LOWER_DEPLOY_ALTITUDE = u.Measurement(9829, u.Unit.FEET) # Altitude (approximate AGL) at which lower stage deployment will take place
UPPER_DEPLOY_ALTITUDE = u.Measurement(37530, u.Unit.FEET) # Altitude (approximate AGL) at which upper stage deployment will take place

LAUNCH_ALTITUDE = u.Measurement(1257, u.Unit.FEET) # Altitude of launch site (above sea level)

SHEAR_PIN_COUNT = 3
SHEAR_PIN_FORCE = 42 # in lbf

# Rocket dimensions
AIRFRAME_DIAMETER = u.Measurement(4, u.Unit.INCHES) # Assuming the rocket to be a perfect cylinder, the diameter of the cylinder
SEPERATION_CLEARANCE_LENGTH = u.Measurement(4, u.Unit.INCHES) # How long the interstage coupler is
UPPER_BAY_LENGTH = u.Measurement(14.5, u.Unit.INCHES) # How long the upper stage recovery bay is
LOWER_BAY_LENGTH = u.Measurement(14.5, u.Unit.INCHES) # How long the lower stage recovery bay is

# Constants
R = 266 # gas constant (inches * lbf / lbm)

# ============= Calculation [Do not modify beyond this line] =============
environment = env.Environment(LAUNCH_ALTITUDE, env_util.WindModelConstant(u.Measurement(0))) # Set up launch env

class Simulation:
    """Abstraction for a single black powder calculation"""
    LB_TO_GRAMS = 454
    def __init__(self, name:str, pressure, volume, temperature, bp_efficiency=1) -> None:
        self.name = name
        self.pressure = pressure
        self.volume = volume
        self.temperature = temperature
        self.efficiency = bp_efficiency

    def bp_burn_efficiency(self):
        if(self.efficiency == 1):
            return (self.temperature/3307)*100
        else:
            return self.efficiency*100

    def result(self):
        return ((self.pressure * self.volume) / (R * self.temperature)) * self.LB_TO_GRAMS * (1/self.efficiency)


class Stage:
    """Abstraction layer for the bp calculations for a single rocket stage."""
    def __init__(self, name, area, length, default_pressure=TARGET_PRESSURE) -> None:
        self.name = name
        self.cross_section_area = area
        self.length = length
        self.default_volume = self.get_volume()
        self.default_pressure = default_pressure
        self.sims: list[Simulation] = []

    def add_sim(self, name: str, temperature, pressure=-1, volume=-1, efficiency=1):
        if(volume == -1):
            volume = self.default_volume
        if(pressure == -1):
            pressure = self.default_pressure
        self.sims.append(Simulation(name, pressure, volume, temperature, efficiency))

    def get_volume(self) -> float:
        return self.length * self.cross_section_area
    
    def __str__(self) -> str:
        res_text = f"=== {self.name} ===\n"
        for sim in self.sims:
            res_text += f"{sim.name}: {sim.result():.3f}g \x1b[90m({sim.bp_burn_efficiency():.1f}% efficiency)\x1b[0m\n"
        return res_text


def K_to_R(kelvin: float) -> float:
    """Kelvin to Rankine converter"""
    return kelvin * 1.8

airframe_cross_section_area = np.pi * (AIRFRAME_DIAMETER.inches()/2)**2 # (in^2)

shear_pin_force = (SHEAR_PIN_COUNT * SHEAR_PIN_FORCE)
friction_force = 0
total_force =  shear_pin_force + (TARGET_PRESSURE * airframe_cross_section_area) + friction_force
equivalent_pressure = total_force / airframe_cross_section_area

bp_gas_temperature = 3307
seperation_temperature = K_to_R(environment.get_temperature(SEPERATION_ALTITUDE)) # Temp (in Rankine) of ambient temp at seperation altitude
lower_deploy_temperature = K_to_R(environment.get_temperature(LOWER_DEPLOY_ALTITUDE)) # Temp (in Rankine) of ambient temp at 1st stage recovery deployment altitude
upper_deploy_temperature = K_to_R(environment.get_temperature(UPPER_DEPLOY_ALTITUDE)) # Temp (in Rankine) of ambient temp at 2nd stage recovery deployment altitude

old_calculator_temp = 518.67

def combustion_efficiency_temp(input: float):
    """Gets combustion efficiency from air temp"""
    return input/bp_gas_temperature

def combustion_efficiency_rcm(bp_mass:float, chamber_volume:float, peak_pressure:float):
    """Gets combustion efficiency based on bp mass, chamber volume, and peak pressure."""
    """Units: chamber volume (in^3), pressure (psi), mass (g)"""
    burned_bp: float = Simulation("_interopsim", peak_pressure, chamber_volume, bp_gas_temperature, 1).result()
    return burned_bp/bp_mass

def temp_c_text(input: float):
    eff = combustion_efficiency_temp(input)
    return f"({(eff*100):.1f}% efficiency)"

# Calculate volumes of the 3 bays
seperation_area_volume: u.Measurement = SEPERATION_CLEARANCE_LENGTH * airframe_cross_section_area
upper_bay_volume: u.Measurement = UPPER_BAY_LENGTH * airframe_cross_section_area
lower_bay_volume: u.Measurement = LOWER_BAY_LENGTH * airframe_cross_section_area

LB_TO_GRAMS = 454 # Conversion factor





seperation_stage = Stage("INTERSTAGE", airframe_cross_section_area, SEPERATION_CLEARANCE_LENGTH.inches(), default_pressure=equivalent_pressure)
seperation_stage.add_sim("\x1b[90mAbsolute Lower bound (Best case)\x1b[0m", bp_gas_temperature)
seperation_stage.add_sim("\x1b[90mAbsolute Upper bound (Worst case)\x1b[0m", seperation_temperature)
seperation_stage.add_sim("\x1b[90mCalculator v1 (historical)\x1b[0m", old_calculator_temp)
seperation_stage.add_sim("\x1b[32mBEST GUESS (historical: SG1)\x1b[0m", bp_gas_temperature, efficiency=0.162)
seperation_stage.add_sim("\x1b[90m50 efficiency\x1b[0m", bp_gas_temperature, efficiency=0.5)
seperation_stage.add_sim("\x1b[90m80 efficiency\x1b[0m", bp_gas_temperature, efficiency=0.8)

lower_stage = Stage("BOOSTER", airframe_cross_section_area, LOWER_BAY_LENGTH.inches(), default_pressure=equivalent_pressure)
lower_stage.add_sim("\x1b[90mAbsolute Lower bound (Best case)\x1b[0m", bp_gas_temperature)
lower_stage.add_sim("\x1b[90mAbsolute Upper bound (Worst case)\x1b[0m", lower_deploy_temperature)
lower_stage.add_sim("\x1b[90mCalculator v1 (historical)\x1b[0m", old_calculator_temp)
lower_stage.add_sim("\x1b[32mBEST GUESS (historical: SG1)\x1b[0m", bp_gas_temperature, efficiency=0.162)
lower_stage.add_sim("\x1b[90m50 efficiency\x1b[0m", bp_gas_temperature, efficiency=0.5)
lower_stage.add_sim("\x1b[90m80 efficiency\x1b[0m", bp_gas_temperature, efficiency=0.8)


upper_stage = Stage("SUSTAINER", airframe_cross_section_area, UPPER_BAY_LENGTH.inches(), default_pressure=equivalent_pressure)
upper_stage.add_sim("\x1b[90mAbsolute Lower bound (Best case)\x1b[0m", bp_gas_temperature)
upper_stage.add_sim("\x1b[90mAbsolute Upper bound (Worst case)\x1b[0m", upper_deploy_temperature)
upper_stage.add_sim("\x1b[90mCalculator v1 (historical)\x1b[0m", old_calculator_temp)
upper_stage.add_sim("\x1b[32mBEST GUESS (historical: SG1)\x1b[0m", bp_gas_temperature, efficiency=0.162)
upper_stage.add_sim("\x1b[90m50 efficiency\x1b[0m", bp_gas_temperature, efficiency=0.5)
upper_stage.add_sim("\x1b[90m80 efficiency\x1b[0m", bp_gas_temperature, efficiency=0.8)

print(f"BP Calculation results")
print(f"(Shear pins) {SHEAR_PIN_COUNT} shear pins @ {SHEAR_PIN_FORCE}lbf (each)")
print(f"(Forces) {TARGET_PRESSURE}psi with {shear_pin_force}lbs shear pin force: {total_force}lbf (equiv {equivalent_pressure}psi)")
print()


print(seperation_stage)
print(lower_stage)
print(upper_stage)