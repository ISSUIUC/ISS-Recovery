# all necessary unit conversion values and functions
from enum import Enum
# values
IN_TO_CM = 2.54
CM_TO_IN = 0.393701
IN_TO_M = 0.0254
IN_TO_FT = 12
CM_TO_M = .01
FT_TO_M = 0.3048
M_TO_FT = 3.28084
M_TO_CM = 100
KM_TO_M = 1000
M_TO_KM = 0.001
MI_TO_KM = 1.60934
MI_TO_M = MI_TO_KM * KM_TO_M

class Unit(float, Enum):
    CENTIMETERS = CM_TO_M
    INCHES = IN_TO_M
    FEET = FT_TO_M
    KILOMETERS = KM_TO_M
    MILES = MI_TO_M
    METERS = 1

class UTime(float, Enum):
    SECOND = 1
    MINUTE = 60
    HOUR = 3600

class UMass(float, Enum):
    KG = 1
    LB = 0.453592

class MassMeasurement:
    """Weaker version of Measurement, only for measuring mass."""
    _internal_measurement = 0
    def __init__(self, measurement_value: float, measurement_unit: UMass = UMass.KG) -> None:
        self._internal_measurement = measurement_value * measurement_unit.value

    def to(self, unit: UMass):
        return self._internal_measurement * (1/unit.value)
    
    def kg(self):
        return self.to(UMass.KG)
    
    def lb(self):
        return self.to(UMass.LB)

    def __str__(self) -> str:
        return str(self._internal_measurement) + " kg"

# Unit utility class
class Measurement:
    class MeasurementUnitType(int, Enum):
        STANDARD = 0
        RATE = 1
        
    """A class to standardize measurements across different units."""
    _internal_measurement = 0
    """The internal measurement given. Internally all measurements are stored in meters. Rate measurements are stored in m/s"""
    _p_unit: Unit = Unit.METERS
    _t_unit: UTime = None
    _unit_type = MeasurementUnitType.STANDARD
    """The unit type"""
    
    def __init__(self, measurement_value: float, measurement_unit: Unit = Unit.METERS) -> None:
        self._internal_measurement = measurement_value * measurement_unit.value
        self._p_unit = measurement_unit

    def set_unit(self, unit: Unit):
        """Sets the preferred unit of the measurement. Does not change the measurement."""
        self._p_unit = unit
        return self

    def length_unit_to_text(measurement_unit: Unit) -> str:
        match measurement_unit:
            case Unit.METERS:
                return "m"
            case Unit.FEET:
                return "ft"
            case Unit.CENTIMETERS:
                return "cm"
            case Unit.INCHES:
                return "in"
            case Unit.KILOMETERS:
                return "km"
            case Unit.MILES:
                return "mi"
            
    def time_unit_to_text(measurement_unit: UTime) -> str:
        match measurement_unit:
            case UTime.SECOND:
                return "s"
            case UTime.HOUR:
                return "hr"
            case UTime.MINUTE:
                return "min"

    def to(self, measurement_unit: Unit) -> float:
        return self._internal_measurement * (1/measurement_unit.value)
    
    def ft(self) -> float:
        return self.to(Unit.FEET)
    
    def m(self) -> float:
        return self.to(Unit.METERS)

    def cm(self) -> float:
        return self.to(Unit.CENTIMETERS)
    
    def inches(self) -> float:
        return self.to(Unit.INCHES)
    
    def get_time_unit(self) -> UTime:
        if(self._t_unit == None):
            raise ValueError("This measurement is not a rate. Getting the time unit is meaningless.")
        return self._t_unit
    
    # Rate methods
    def per(self, time_unit: UTime):
        new_measurement = Measurement(self._internal_measurement * (1/time_unit.value), Unit.METERS)
        new_measurement._p_unit = self._p_unit
        new_measurement._unit_type = Measurement.MeasurementUnitType.RATE
        new_measurement._t_unit = time_unit
        return new_measurement
    
    # Algebra methods
    def __add__(self, other):
        if isinstance(other, Measurement):
            unit = self._p_unit
            return Measurement(self.to(unit) + other.to(unit), self._p_unit)
        raise TypeError(f"Unsupported addition operation between {type(self)}, {type(other)}")

    def __sub__(self, other):
        if isinstance(other, Measurement):
            unit = self._p_unit
            return Measurement(self.to(unit) - other.to(unit), self._p_unit)
        raise TypeError(f"Unsupported subtraction operation between {type(self)}, {type(other)}")
    
    def __mul__(self, other):
        if isinstance(other, Measurement):
            unit = self._p_unit
            return Measurement(self.to(unit) * other.to(unit), self._p_unit)
        raise TypeError(f"Unsupported multiplication operation between {type(self)}, {type(other)}")
    
    def __mul__(self, scalar: float):
        if(self._unit_type == Measurement.MeasurementUnitType.STANDARD):
            return Measurement(self.to(self._p_unit) * scalar, self._p_unit)
        else:
            new_m = Measurement(self.to(self._p_unit) * scalar, self._p_unit)
            new_m._t_unit = self._t_unit
            new_m._unit_type = Measurement.MeasurementUnitType.RATE
            return new_m

    
    def __truediv__(self, other):
        if isinstance(other, Measurement):
            unit = self._p_unit
            return Measurement(self.to(unit) / other.to(unit), self._p_unit)
        raise TypeError(f"Unsupported division operation between {type(self)}, {type(other)}")

    def __truediv__(self, scalar: float):
        return Measurement(self.to(self._p_unit) / scalar, self._p_unit)

    # Comparisons
    def __lt__(self, other):
        return self.m() < other.m()
    
    def __gt__(self, other):
        return self.m() > other.m()
    
    def __eq__(self, other):
        return self.m() == other.m()
    
    def __ge__(self, other):
        return self.m() >= other.m()
    
    def __le__(self, other):
        return self.m() <= other.m()
    
    def __ne__(self, other):
        return self.m() != other.m()
    
    # Unary
    def __neg__(self):
        return Measurement(-self._internal_measurement, self._p_unit)
    
    # Other utilities
    def __str__(self) -> str:
        if(self._unit_type == Measurement.MeasurementUnitType.RATE):
            return f"{self.to(self._p_unit) * self._t_unit.value:.2f} {Measurement.length_unit_to_text(self._p_unit)}/{Measurement.time_unit_to_text(self._t_unit)}   ({str(self.m())} m/s)"
        else:
            return f"{self.to(self._p_unit):.2f} {Measurement.length_unit_to_text(self._p_unit)}   ({str(self.m())} m)"
                

