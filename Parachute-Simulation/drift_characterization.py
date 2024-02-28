import matplotlib.pyplot as plt
import numpy as np
import util.units

class DescentCharacterization:
    def __init__(self, char_file) -> None:
        with open(char_file, "r") as infile:
            lines = infile.read().splitlines()
            self.alts = [float(n) for n in lines[0].split(",")]
            timestamps = [float(n) for n in lines[1].split(",")]
            tm = float(lines[3])
            self.timestamps = [(tm - ts) for ts in timestamps]
            self.alts.reverse()
            self.timestamps.reverse()
            infile.close()

    def get_descent_time_for_alt(self, altitude: util.units.Measurement) -> float:
        alt_m = altitude.m()
        return np.interp(alt_m, self.alts, self.timestamps)
    
    def plot(self):
        plt.plot(self.alts, self.timestamps)
        plt.title("Descent time vs altitude")
    
        plt.show()

        

char = DescentCharacterization("./drift_out.txt")
windspeed = util.units.Measurement(12, util.units.Unit.MILES).per(util.units.UTime.HOUR)
print(windspeed)
print((windspeed * char.get_descent_time_for_alt(util.units.Measurement(11887))).m())
char.plot()