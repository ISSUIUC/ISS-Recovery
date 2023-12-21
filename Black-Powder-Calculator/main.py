
# Equation for calculating black powder needed
# http://hararocketry.org/hara/resources/how-to-size-ejection-charge/
import numpy as np
Pressure = 8 # assuming we want this much pressure (psi)
# "Typical pressure range is from 8-16 psi"
Diameter = 3 # airframe diameter (inches)
Area = np.pi*Diameter**2/4
Area1 = np.pi*(1.5**2)
R = 266 # gas constant (inches * lbf / lbm)
T_separation = 518.67 #515.46 # 900 ft. (Rankine)
T_lower = 518.67 #515.46 # 900 ft. (Rankine)
T_upper = 518.67 #490.141 # 8000 ft. (Rankine)
L_lower = 12.2 # length between bulkheads in the lower stage
L_upper = 17 # length between bulkheads in the upper stage
V_lower = Area * L_lower
V_upper = Area * L_upper
g_to_lb = 454 # number of grams in a pound (g to lbm)
V_separation = 31.762 # (cubic inches)
    
B_separation = Pressure * V_separation / (R * T_separation) * g_to_lb # BP needed for staging separation
B_lower = Pressure * V_lower / R / T_lower * g_to_lb # BP needed for booster tube separation
B_upper = Pressure * V_upper / R / T_upper * g_to_lb # BP needed for sustainer separation
print('BP needed for staging separation: {:.3f}g'.format(B_separation),)
print('BP needed for lower stage separation: {:.3f}g'.format(B_lower))
print('BP needed for upper stage separation: {:.3f}g'.format(B_upper))
print(V_upper)