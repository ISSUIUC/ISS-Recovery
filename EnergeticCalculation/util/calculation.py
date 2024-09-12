import EnergeticCalculation.config as config
import EnergeticCalculation.util.rocket_util as rocket
import EnergeticCalculation.util.units as u

def combustion_efficiency_temp(input: float):
    """Gets combustion efficiency from air temp"""
    return input/config.BP_GAS_TEMPERATURE

def combustion_efficiency_rcm(bp_mass:float, chamber_volume:float, peak_pressure:float):
    """Gets combustion efficiency based on bp mass, chamber volume, and peak pressure.
    Units: chamber volume (in^3), pressure (psi), mass (g)"""
    burned_bp: float = rocket.Simulation("_interopsim", peak_pressure, chamber_volume, config.BP_GAS_TEMPERATURE, 1).result()
    return burned_bp/bp_mass

def rcm_test(bp_mass, peak_pressure) -> float:
    eff = combustion_efficiency_rcm(bp_mass, config.RCM_VOLUME, peak_pressure)
    # print(f"(RCM sim): Peak pressure {peak_pressure} psi : Efficiency {(eff*100):.2f}%")
    return eff

def combustion_efficiency_mass(bp_mass: float, structure_wet_mass: float, structure_dry_mass:float):
    combusted_mass: float = structure_wet_mass - structure_dry_mass
    return combusted_mass / bp_mass

class RCMEfficiencyCalculation:
    def __init__(self, volume=config.RCM_VOLUME) -> None:
        self.rcm_volume = volume
        self.simulations = []

    def add_sim(self, bp_mass: float, reference_pressure: float, peak_pressure: float):
        self.simulations.append((bp_mass, reference_pressure, peak_pressure))

    def get_average_efficiency(self):
        eff_values = []
        for sim in self.simulations:
            bp_mass, reference_pressure, peak_pressure = sim
            eff_value = rcm_test(bp_mass,abs((peak_pressure * u.BAR_TO_PSI) - (reference_pressure * u.BAR_TO_PSI)))
            eff_values.append(eff_value)
        return sum(eff_values)/len(eff_values)
        

