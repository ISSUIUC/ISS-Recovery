# Wrapper for Energetic and Parachute calculation for the api
# Path hack.
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import EnergeticCalculation.util.calculation
import EnergeticCalculation.util.rocket_util as rocket
import EnergeticCalculation.config as energetic_config
import numpy as np


# Schema verification
def verify_MassParam(data):
    # Returns error if the schema doesn't follow MassParam schema
    if type(data) != list:
        return "Request does not conform to MassParam schema: Request is not a list[int|float,3]", 400

    if len(data) != 3:
        return f"Request does not conform to MassParam schema: Request is a list[], but length is {len(data)}", 400
    
    for item in data:
        if type(item) != float and type(item) != int:
            return f"Request does not conform to MassParam schema: Request is a list, but contains non-numeric elements", 400
        
    return None, None

def verify_RCMParamDatapoint(data):
    # Returns error if the schema doesn't follow RCMParam schema
    if type(data) != list:
        return "Request does not conform to RCMParamDatapoint schema: Data is not a list[int|float,4]", 400

    if len(data) != 3:
        return f"Request does not conform to RCMParamDatapoint schema: Data is a list[], but length is {len(data)}", 400
    
    for item in data:
        if type(item) != float and type(item) != int:
            return f"Request does not conform to RCMParamDatapoint schema: Data is a list, but contains non-numeric elements", 400
    return None, None

def verify_RCMParams(data):
    # Returns error if the schema isnt a list of RCMParams
    if type(data) != dict:
        return "Request does not conform to RCMParam schema: Request is not a dict", 400
    
    if "volume" not in data:
        return "Request does not conform to RCMParam schema: Missing volume", 400
    
    if type(data["volume"]) != int and type(data["volume"]) != float:
        return "Request does not conform to RCMParam schema: Volume must be numeric", 400
    
    if "datapoints" not in data:
        return "Request does not conform to RCMParam schema: Missing datapoints", 400
    
    if type(data["datapoints"]) != list:
        return "Request does not conform to RCMParam schema: Datapoints must be a list of `RCMParamDatapoint`s", 400
    
    if len(data["datapoints"]) == 0:
        return "Request does not conform to RCMParam schema: Datapoints cannot be empty", 400
        
    for datapoint in data["datapoints"]:
        error, code = verify_RCMParamDatapoint(datapoint)
        if error:
            return f"Request does not conform to list[RCMParam] schema: Not all elements conform to RCMParam.\n  {datapoint}: {error}", code

    return None, None

def verify_ESimData(data):
    # Returns error if the schema isnt a list of RCMParams
    if type(data) != dict:
        return "Request does not conform to ESimData schema: Request is not a dict", 400
    
    if "name" not in data:
        return "Request does not conform to RCMParam schema: Missing name", 400
    
    if type(data["name"]) != str:
        return "Request does not conform to RCMParam schema: name must be a string", 400
    
    if "dimensions" not in data:
        return "Request does not conform to RCMParam schema: Missing dimensions", 400
    
    if type(data["dimensions"]) != dict:
        return "Request does not conform to RCMParam schema: dimensions must be a dict", 400

    if "efficiency" not in data:
        return "Request does not conform to RCMParam schema: Missing efficiency", 400
    
    if type(data["efficiency"]) != list:
        return "Request does not conform to RCMParam schema: efficiency must be a list[number]", 400
    
    dimensions = data["dimensions"]
    if "diameter" not in dimensions:
        return "Request does not conform to RCMParam schema: Missing dimensions.diameter", 400
    
    if type(dimensions["diameter"]) != int and type(dimensions["diameter"]) != float:
        return "Request does not conform to RCMParam schema: dimensions.diameter must be numeric", 400
    
    if "length" not in dimensions:
        return "Request does not conform to RCMParam schema: Missing dimensions.length", 400
    
    if type(dimensions["length"]) != int and type(dimensions["length"]) != float:
        return "Request does not conform to RCMParam schema: dimensions.length must be numeric", 400
    
    for eff in data["efficiency"]:
        if type(eff) != int and type(eff) != float:
            return "Request does not conform to RCMParam schema: All entries in efficiency must be numeric", 400

    return None, None

# Simulations

def energetic_mass_calculation(energetic_mass: float, wet_mass: float, dry_mass: float):
    return EnergeticCalculation.util.calculation.combustion_efficiency_mass(energetic_mass, wet_mass, dry_mass)

def energetic_rcm_calculation(rcm_data):

    volume = rcm_data["volume"]
    data = rcm_data["datapoints"]

    calculator = EnergeticCalculation.util.calculation.RCMEfficiencyCalculation(volume)
    for datapoint in data:
        calculator.add_sim(datapoint[0], datapoint[1], datapoint[2])

    return calculator.get_average_efficiency()

def energetic_sim(sim_data):

    airframe_diameter: float = sim_data["dimensions"]["diameter"]
    section_length: float = sim_data["dimensions"]["length"]
    pressure: float = sim_data["target_pressure"]
    sim_name = sim_data["name"]
    efficiency: list[float] = sim_data["efficiency"]

    airframe_cross_section_area: float = np.pi * (airframe_diameter/2)**2 # (in^2)

    sim_volume = rocket.Stage(sim_name, airframe_cross_section_area, section_length, default_pressure=pressure)

    for sim_eff in efficiency:
        sim_volume.add_sim(f"{(sim_eff*100):.1f}", energetic_config.BP_GAS_TEMPERATURE, efficiency=sim_eff)

    return sim_volume.sims