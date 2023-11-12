import scipy.constants
import util.units


class Parachute:
    def __init__(self, drag_coefficient: float, radius: util.units.Measurement):
        self.drag_coefficient = drag_coefficient
        self.radius = radius

    def calculate_drag(self, fluid_density: float, velocity: util.units.Measurement):
        return 0.5*(fluid_density * (velocity.m()**2) * self.drag_coefficient * ((self.radius.m()**2) * scipy.constants.pi))

    