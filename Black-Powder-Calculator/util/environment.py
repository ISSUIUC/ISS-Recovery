from ambiance import Atmosphere
import util.units
import util.environment_utils

class Environment:
    def __init__(self, ground_alt: util.units.Measurement, wind_model: util.environment_utils.WindModel) -> None:
        self.ground_alt = ground_alt
        self.wind_model = wind_model

    def get_density(self, altitude: util.units.Measurement) -> float:
        """Gets the air density at a certain altitude above the ground"""
        alt = self.ground_alt + altitude
        atmo = Atmosphere(alt.m())
        return atmo.density[0]
    
    def get_temperature(self, altitude: util.units.Measurement) -> float:
        """Gets the air temperature at a certain altitude above the ground (in Kelvin)"""
        alt = self.ground_alt + altitude
        atmo = Atmosphere(alt.m())
        return atmo.temperature[0]
    
    def get_windspeed(self, altitude_above_ground: util.units.Measurement) -> util.units.Measurement:
        return self.wind_model.get_windspeed(altitude_above_ground)