import scipy.constants
import util.units
import util.environment
import math

class ParachuteCalculation:
    def calculate_radius(mass: util.units.MassMeasurement, drag_coeff: float, air_density: float, target_velocity: util.units.Measurement) -> util.units.Measurement:
        """Generic radius calculation"""
        rad = math.sqrt((2 * mass.kg() * scipy.constants.g)/(scipy.constants.pi * drag_coeff * air_density * (target_velocity.m()**2)))
        return util.units.Measurement(rad)
    
    def calculate_radius_landing(mass: util.units.MassMeasurement, drag_coeff: float, launch_env: util.environment.Environment, target_velocity: util.units.Measurement) -> util.units.Measurement:
        """Calculate the radius of parachute required to hit the ground at `target_velocity` in the conditions at `launch_env`"""
        air_density = launch_env.get_density(util.units.Measurement(0))
        return ParachuteCalculation.calculate_radius(mass, drag_coeff, air_density, target_velocity)
    
    def calculate_radius_max_descent_vel(mass: util.units.MassMeasurement, drag_coeff: float, launch_env: util.environment.Environment, altitude: util.units.Measurement, target_velocity: util.units.Measurement) -> util.units.Measurement:
        """Calculate the radius of parachute required to have a descent rate of `target_velocity` at altitude `altitude` above `launch_env`"""
        air_density = launch_env.get_density(altitude)
        return ParachuteCalculation.calculate_radius(mass, drag_coeff, air_density, target_velocity)

class Parachute:
    def __init__(self, drag_coefficient: float, radius: util.units.Measurement, attached_mass: util.units.MassMeasurement):
        self.drag_coefficient = drag_coefficient
        self.radius = radius
        self.attached_mass = attached_mass
        self.parachute_area = self.area()

    def calculate_drag(self, fluid_density: float, velocity: util.units.Measurement) -> float:
        """Returns drag in newtons"""
        return 0.5*(fluid_density * (velocity.m()**2) * self.drag_coefficient * ((self.radius.m()**2) * scipy.constants.pi))
    
    def get_terminal_velocity(self, altitude: util.units.Measurement, environment: util.environment.Environment) -> util.units.Measurement:
        """Get terminal velocity at altitude"""
        term_vel = math.sqrt((2 * self.attached_mass.kg() * scipy.constants.g)/(environment.get_density(altitude) * self.drag_coefficient * self.area()))
        return util.units.Measurement(term_vel).per(util.units.UTime.SECOND)

    def area(self) -> float:
        """Get area of the parachute (Always in units of meters)"""
        return self.radius.m()**2 * scipy.constants.pi
    
    def area_to_radius(area: float) -> float:
        return math.sqrt(area / scipy.constants.pi)

    def get_drift(self, timestep: float, start_altitude: util.units.Measurement, end_altitude: util.units.Measurement, environment: util.environment.Environment) -> util.units.Measurement:
        drift = util.units.Measurement(0)
        alt = start_altitude

        # This will (for now) naively assume the rocket is already travelling at terminal velocity.
        while alt > end_altitude:
            term_vel = self.get_terminal_velocity(alt, environment)
            drift += environment.wind_speed * timestep
            alt -= term_vel * timestep

        return drift

    
    

    
    

    