from enum import Enum
import math

class OpeningFunction(Enum):
    LINEAR = lambda x: x
    SQRT = lambda x: math.sqrt(x)
    SQUARE = lambda x: x**2
    CUBE = lambda x: x**3
    NATURAL = lambda x: (math.exp(x) - 1) / (math.e-1)
    SINE = lambda x: (1/2)*(math.sin(math.pi*(x-(1/2)))) + 0.5
