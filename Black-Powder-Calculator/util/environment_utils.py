import util.units
from abc import ABC, abstractmethod

class WindModel(ABC):
    reference_windspeed: util.units.Measurement

    def __init__(self, reference_windspeed: util.units.Measurement) -> None:
        self.reference_windspeed = reference_windspeed
    
    @abstractmethod
    def get_windspeed(self, altitude_above_ground: util.units.Measurement) -> util.units.Measurement:
        raise NotImplementedError("Not implemented : get_windspeed")
    
class WindModelHellman(WindModel):
    """Models windspeed as a hellman model (https://en.wikipedia.org/wiki/Wind_gradient)"""
    def __init__(self, reference_windspeed: util.units.Measurement, hellman_coefficient: float) -> None:
        self.hellman_coeff = hellman_coefficient
        super().__init__(reference_windspeed)

    def get_windspeed(self, altitude_above_ground: util.units.Measurement) -> util.units.Measurement:
        # 10 used as a magic number.
        return self.reference_windspeed * (abs(altitude_above_ground.m() / 10)**(self.hellman_coeff))
    
class WindModelConstant(WindModel):
    """Models windspeed as a constant wind speed"""
    def __init__(self, reference_windspeed: util.units.Measurement) -> None:
        super().__init__(reference_windspeed)

    def get_windspeed(self, altitude_above_ground: util.units.Measurement) -> util.units.Measurement:
        return self.reference_windspeed

