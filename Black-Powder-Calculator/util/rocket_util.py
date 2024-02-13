import config

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
            return (self.temperature/config.BP_GAS_TEMPERATURE)*100
        else:
            return self.efficiency*100

    def result(self):
        """Gives the amount of bp (in grams) to achieve target system pressure"""
        return ((self.pressure * self.volume) / (config.R * self.temperature)) * self.LB_TO_GRAMS * (1/self.efficiency)
    
    def result_inverse(self, bp_grams: float):
        """Gives the pressure made by a given amount of bp (in grams)"""
        pressure = ((bp_grams/((1/self.efficiency) * self.LB_TO_GRAMS))*(config.R * self.temperature)) / self.volume
        return pressure



class Stage:
    """Abstraction layer for the bp calculations for a single rocket stage."""
    def __init__(self, name, area, length, default_pressure=config.TARGET_PRESSURE_DEPLOY) -> None:
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
