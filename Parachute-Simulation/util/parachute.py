import scipy.constants
import util.units
import util.environment
import math
import config


class ParachuteOpeningCharacteristics:
    def __init__(self, opening_function: callable, fill_time: float) -> None:
        self.opening_function = opening_function
        self.fill_time = fill_time

    def get_opening_percentage(self, time_after_opening) -> float:
        if(self.fill_time <= 0):
            return 1
        percent_characteristic_curve = time_after_opening / self.fill_time
        if(percent_characteristic_curve > 1):
            percent_characteristic_curve = 1

        return self.opening_function(percent_characteristic_curve)

class DriftAnalysisResult:
    def __init__(self, drift: util.units.Measurement, max_vel: util.units.Measurement, time: float, timestamp_list: list[float], vel_list: list[float], alt_list: list[float], max_force: float) -> None:
        self.drift = drift
        self.time = time
        self.ts_list = timestamp_list
        self.v_list = vel_list
        self.alt_list = alt_list
        self.maximum_velocity = max_vel
        self.max_force = max_force

class Parachute:
    def __init__(self, drag_coefficient: float, radius: util.units.Measurement, attached_mass: util.units.MassMeasurement, opening_characteristics: ParachuteOpeningCharacteristics):
        self.drag_coefficient = drag_coefficient
        self.radius = radius
        self.attached_mass = attached_mass
        self.parachute_area = self.area()
        self.opening_characteristics = opening_characteristics

    def calculate_drag(self, fluid_density: float, velocity: util.units.Measurement) -> float:
        """Returns drag in newtons"""
        return 0.5*(fluid_density * (velocity.m()**2) * self.drag_coefficient * ((self.radius.m()**2) * scipy.constants.pi))
    
    def calculate_drag_with_opening(self, fluid_density: float, velocity: util.units.Measurement, opening_percentage: float) -> float:
        """Returns drag in newtons, with accounting for parachute opening"""
        protrated_parachute_radius = self.radius.m() * opening_percentage
        return 0.5*(fluid_density * (velocity.m()**2) * self.drag_coefficient * ((protrated_parachute_radius**2) * scipy.constants.pi))
    
    def get_terminal_velocity(self, altitude: util.units.Measurement, environment: util.environment.Environment) -> util.units.Measurement:
        """Get terminal velocity at altitude"""
        term_vel = math.sqrt((2 * self.attached_mass.kg() * scipy.constants.g)/(environment.get_density(altitude) * self.drag_coefficient * self.area()))
        return util.units.Measurement(term_vel).per(util.units.UTime.SECOND)

    def area(self) -> float:
        """Get area of the parachute (Always in units of meters)"""
        return self.radius.m()**2 * scipy.constants.pi
    
    def area_to_radius(area: float) -> float:
        return math.sqrt(area / scipy.constants.pi)

    def get_drift(self, timestep: float, start_altitude: util.units.Measurement, 
                  end_altitude: util.units.Measurement, environment: util.environment.Environment, 
                  start_velocity: util.units.Measurement, start_time: float, other_parachutes: list = []) -> DriftAnalysisResult:
        drift = util.units.Measurement(0)
        alt = start_altitude
        velocity = start_velocity
        maximum_velocity = velocity
        print_debounce = 0
        print_debounce_max = 100


        normal_timestep = timestep
        fine_timestep = config.FINE_ANALYSIS_TIMESTEP

        total_time = start_time
        ts_list = []
        vel_list = []
        alt_list = []
        max_force_cur = 0

        

        while alt > end_altitude:
            # Dynamic timestep: Reduce the magnitude of timestep when we're approaching/at critical events
            print_debounce += 1
            if(abs(alt.m() - config.MAIN_ALTITUDE.m()) < config.DYNAMIC_TIMESTEP_RANGE.m()):
                timestep = fine_timestep
                if print_debounce > print_debounce_max:
                    print(f"performing drift analysis... {100*(1-alt.m()/config.APOGEE_ALTITUDE.m()):.0f}%  [Fine timestep]", end="    \r")
                    print_debounce = 0
            else:
                timestep = normal_timestep
                if print_debounce > print_debounce_max:
                    print(f"performing drift analysis... {100*(1-alt.m()/config.APOGEE_ALTITUDE.m()):.0f}%  [Normal timestep]", end="    \r")
                    print_debounce = 0

            # Since this function simulates a parachute with other parachutes as secondary, we will assume
            # all other parachutes are already opened :)   
            time_since_opening = total_time - start_time
            parachute_opening_percentage = self.opening_characteristics.get_opening_percentage(time_since_opening)

            total_time += timestep
            ts_list.append(total_time)
            vel_list.append(velocity.m())
            alt_list.append(alt.m())
            
            drag_force = self.calculate_drag_with_opening(environment.get_density(alt), velocity, parachute_opening_percentage)
            cur_parachute_force = drag_force
            other_parachute_list: list[Parachute] = other_parachutes # Type hinting lol
            for parachute in other_parachute_list:
                drag_force += parachute.calculate_drag(environment.get_density(alt), velocity)

            if(cur_parachute_force > max_force_cur):
                max_force_cur = cur_parachute_force

            drag_accel = drag_force/self.attached_mass.kg()
            acceleration = util.units.Measurement(scipy.constants.g - drag_accel).per(util.units.UTime.SECOND)

            velocity = velocity + (acceleration * timestep)

            term_vel = self.get_terminal_velocity(alt, environment)
            #if(velocity > term_vel):
            #    velocity = term_vel
            drift += environment.get_windspeed(alt) * timestep

            alt -= velocity * timestep
            if(velocity > maximum_velocity):
                maximum_velocity = velocity


        
        return DriftAnalysisResult(drift, maximum_velocity.per(util.units.UTime.SECOND), total_time, ts_list, vel_list, alt_list, max_force_cur)

class ParachuteCalculation:

    def calculate_radius_with_other_chute(total_radius: util.units.Measurement, other_parachute: Parachute) -> util.units.Measurement:
        total_area = (total_radius.m()**2) * scipy.constants.pi
        this_parachute_area = total_area - other_parachute.area()
        return util.units.Measurement(Parachute.area_to_radius(this_parachute_area))


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
