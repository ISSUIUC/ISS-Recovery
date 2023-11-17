import scipy.constants
import util.units
import util.environment
import math
import config


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

class DriftAnalysisResult:
    def __init__(self, drift: util.units.Measurement, max_vel: util.units.Measurement) -> None:
        self.drift = drift
        self.maximum_velocity = max_vel

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

    def get_drift(self, timestep: float, start_altitude: util.units.Measurement, end_altitude: util.units.Measurement, environment: util.environment.Environment, start_velocity: util.units.Measurement) -> DriftAnalysisResult:
        drift = util.units.Measurement(0)
        alt = start_altitude
        velocity = start_velocity
        maximum_velocity = velocity
        # This will (for now) naively assume the rocket is already travelling at terminal velocity.
        print_debounce = 0
        print_debounce_max = 100
        while alt > end_altitude:

            drag_force = self.calculate_drag(environment.get_density(alt), velocity)
            drag_accel = drag_force/self.attached_mass.kg()
            acceleration = util.units.Measurement(scipy.constants.g - drag_accel).per(util.units.UTime.SECOND)
            velocity = velocity + (acceleration * timestep)

            term_vel = self.get_terminal_velocity(alt, environment)
            #if(velocity > term_vel):
            #    velocity = term_vel
            drift += environment.wind_speed * timestep

            alt -= velocity * timestep
            if(velocity > maximum_velocity):
                maximum_velocity = velocity

            print_debounce += 1
            if print_debounce > print_debounce_max:
                print(f"performing drift analysis... {100*(1-alt.m()/config.APOGEE_ALTITUDE.m()):.0f}%", end="    \r")
                print_debounce = 0

        
        return DriftAnalysisResult(drift, maximum_velocity.per(util.units.UTime.SECOND))
    