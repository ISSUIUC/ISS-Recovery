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

class Unit(float, Enum):
    CENTIMETERS = CM_TO_M
    INCHES = IN_TO_M
    FEET = FT_TO_M
    METERS = 1

# Unit utility class
class Measurement:
    _internal_measurement = 0
    _p_unit = Unit.METERS
    """The internal measurement given. Internally all measurements are stored in meters."""

    def __init__(self, measurement_value: float, measurement_unit: Unit = Unit.METERS) -> None:
        self._internal_measurement = measurement_value * measurement_unit.value
        self._p_unit = measurement_unit

    def unit_to_text(measurement_unit: Unit) -> str:
        match measurement_unit:
            case Unit.METERS:
                return "m"
            case Unit.FEET:
                return "ft"
            case Unit.CENTIMETERS:
                return "cm"
            case Unit.INCHES:
                return "in"
            

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
    
    # Algebra methods
    def __add__(self, other):
        unit = self._p_unit
        return Measurement(self.to(unit) + other.to(unit), self._p_unit)
    
    def __sub__(self, other):
        unit = self._p_unit
        return Measurement(self.to(unit) - other.to(unit), self._p_unit)
    
    def __mul__(self, other):
        unit = self._p_unit
        return Measurement(self.to(unit) * other.to(unit), self._p_unit)
    
    def __truediv__(self, other):
        unit = self._p_unit
        return Measurement(self.to(unit) / other.to(unit), self._p_unit)

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
        return f"{str(self.to(self._p_unit))} {Measurement.unit_to_text(self._p_unit)}   ({str(self.m())} m)"
                

