from enum import Enum
import math

class OpeningFunction(Enum):
    LINEAR = lambda x: x
    SQRT = lambda x: math.sqrt(x)
    SQUARE = lambda x: x**2
    CUBE = lambda x: x**3
    NATURAL = lambda x: (math.exp(x) - 1) / 1.718
