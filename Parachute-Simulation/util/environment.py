from ambiance import Atmosphere
import util.units

class Environment:
    def __init__(self, ground_alt: util.units.Measurement) -> None:
        self.ground_alt = ground_alt

    def get_density(self, altitude: util.units.Measurement) -> float:
        """Gets the air density at a certain altitude above the ground"""
        alt = self.ground_alt + altitude
        atmo = Atmosphere(alt.m())
        return atmo.density[0]