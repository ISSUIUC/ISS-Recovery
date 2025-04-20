import util.parachute as parachute
import util.units as m
import util.environment as environment
import config

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

class LimitExceededException(Exception):
    """Exception raised for exceeded limits"""
    def __init__(self, message="Limit exceeded (Unknown)"):
        super().__init__(message)

launch_site = environment.Environment(config.LAUNCH_SITE_ALTITUDE, config.WIND_MODEL)

def get_drift_data(DROGUE_DIAMETER,MAIN_DIAMETER,APOGEE_ALTITUDE,MAIN_ALTITUDE,ROCKET_MASS):
    # Opening characteristics
    main_opening_characteristics = parachute.ParachuteOpeningCharacteristics(config.MAIN_FILL_CHAR_FUNCTION, config.MAIN_T_FILL)
    drogue_opening_characteristics = parachute.ParachuteOpeningCharacteristics(config.DROGUE_FILL_CHAR_FUNCTION, config.DROGUE_T_FILL)

    # drogue
    drogue_radius = DROGUE_DIAMETER/2
    drogue = parachute.Parachute(config.DROGUE_DRAG_COEFF, drogue_radius, ROCKET_MASS, drogue_opening_characteristics)

    # main
    main_radius = MAIN_DIAMETER/2
    main = parachute.Parachute(config.MAIN_DRAG_COEFF, main_radius, ROCKET_MASS, main_opening_characteristics)
    # For proper outputting

    main_radius.set_unit(config.OUTPUT_UNITS)

    # Calculate drift

    drift_drogue = drogue.get_drift(config.ANALYSIS_TIMESTEP, APOGEE_ALTITUDE, MAIN_ALTITUDE, launch_site, m.Measurement(0).per(m.UTime.SECOND), 0, [], parachute.DriftMonteCarloParameters(0), main)
    main_deploy_velocity = drift_drogue.v_list[len(drift_drogue.v_list) - 1]
    drift_main = main.get_drift(config.ANALYSIS_TIMESTEP, MAIN_ALTITUDE, m.Measurement(0), launch_site, m.Measurement(main_deploy_velocity).per(m.UTime.SECOND), drift_drogue.time, [drogue])

    total_drift = drift_drogue.drift + drift_main.drift

    total_drift.set_unit(config.DRIFT_UNITS)

    return np.array([drift_drogue , drift_main])

def knots_to_mph(knots):
    return knots * 1.15078

def estimate_air_density(alt_ft):
    """
    Estimate air density using an exponential decay model.
    """
    alt_m = alt_ft * 0.3048
    if alt_m > 25000:
        return 0.04008 * np.exp(-alt_m / 6341.62)
    else:
        return 1.225 * np.exp(-alt_m / 8500)

def process_wind_data(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    data = {}
    start_reading = False

    for line in lines:
        line = line.strip()
        if not start_reading:
            if line.startswith("ftAGL"):
                start_reading = True
            continue

        if not line or line.startswith("Wind"):
            continue

        parts = line.split()
        if len(parts) < 4:
            continue

        alt = int(parts[0])
        direction = np.abs(180 - int(parts[1]))
        speed_kts = float(parts[2])
        temp = float(parts[3])  # parsed but not used

        speed_mph = round(knots_to_mph(speed_kts), 2)
        density = round(estimate_air_density(alt), 4)

        if alt not in data:
            data[alt] = {'count': 1, 'speed': speed_mph, 'dir': direction, 'rho': density}
        else:
            d = data[alt]
            d['count'] += 1
            d['speed'] = (d['speed'] * (d['count'] - 1) + speed_mph) / d['count']
            d['dir'] = (d['dir'] * (d['count'] - 1) + direction) / d['count']
            d['rho'] = (d['rho'] * (d['count'] - 1) + density) / d['count']

    # Build level_n variables and query_altitude_list
    levels = []
    sorted_altitudes = sorted(data.keys(), reverse=True)
    for idx, alt in enumerate(sorted_altitudes):
        d = data[alt]
        level_data = [
            alt,
            round(d['speed'], 2),
            int(round(d['dir'])),
            round(d['rho'], 4)
        ]
        globals()[f"level_{idx+1}"] = level_data
        levels.append(level_data)

    return levels

def merge_levels(website_levels, textfile_levels):
    merged = {}

    # Add website levels
    for alt, speed, direction, rho in website_levels:
        merged[alt] = {'count': 1, 'speed': speed, 'dir': direction, 'rho': rho}

    # Add or average textfile levels
    for alt, speed, direction, rho in textfile_levels:
        if alt in merged:
            d = merged[alt]
            d['count'] += 1
            d['speed'] = (d['speed'] * (d['count'] - 1) + speed) / d['count']
            d['dir'] = (d['dir'] * (d['count'] - 1) + direction) / d['count']
            d['rho'] = (d['rho'] * (d['count'] - 1) + rho) / d['count']
        else:
            merged[alt] = {'count': 1, 'speed': speed, 'dir': direction, 'rho': rho}

    # Convert back to list format and sort by descending altitude
    final_levels = []
    for alt in sorted(merged.keys(), reverse=True):
        d = merged[alt]
        final_levels.append([
            alt,
            round(d['speed'], 2),
            int(round(d['dir'])),
            round(d['rho'], 4)
        ])
    return final_levels

def Drift_Approx(drogue_result: parachute.DriftAnalysisResult, main_result: parachute.DriftAnalysisResult,typesim, mass, maind):
    total_timestamp_list = drogue_result.ts_list + main_result.ts_list
    total_alt_list = drogue_result.alt_list + main_result.alt_list

    # Altitude and Time are sorted together
    total_alt_list_array = np.array(total_alt_list)
    total_timestamp_list_array = np.array(total_timestamp_list)
    sorted_indices = np.argsort(total_alt_list_array)
    sorted_total_alt_list = total_alt_list_array[sorted_indices]
    sorted_total_timestamp_list = total_timestamp_list_array[sorted_indices]
        
    # START POS VECTOR CODE

    # Alt Levels to measure at and wind velocity/direction [alt,wvel,wdir] alt=ft, wvel=mph, wdir=degrees (north zero)
    level_1 = [120000, 26, 90, 0.003996]
    level_2 = [98000, 26, 90, 0.01841]
    level_3 = [45000, 50, 95, 0.1948]
    level_4 = [39000, 53, 95, 0.4135]
    level_5 = [34000, 55, 130, 0.4135]
    level_6 = [30000, 47, 130, 0.4671]
    level_7 = [24000, 43, 130, 0.5900]
    level_8 = [18000, 31, 135, 0.7364]
    level_9 = [14000, 17, 135, 0.8194]
    level_10 = [10000, 8, 100, 0.9093]
    level_11 = [6400, 12, 50, 1.007]
    level_12 = [5000, 12, 25, 1.007]
    level_13 = [3000, 11, 20, 1.112]
    level_14 = [2500, 9, 15, 1.112]
    level_15 = [2000, 9, 15, 1.112]
    level_16 = [330, 12, 15, 1.225]
    level_17 = [0, 9, 5, 1.225]

    windycom_levels = [level_1,level_2,level_3,level_4,level_5,level_6,level_7,level_8,level_9,level_10,level_11,level_12,level_13,level_14,level_15,level_16,level_17]

    # you need to download wind data from https://windsaloft.us/ at the long/lat of FAR

    textfile_levels = process_wind_data("Drift-Analysis/winds_35.35,-117.81_2300Z.txt")
    query_altitude_list = merge_levels(windycom_levels, textfile_levels)

    position_array = np.array([0.0,0.0])
    pos_array_list = []

    for level in range(len(query_altitude_list) -1):

        # Query altitude value ft to meters
        query_altitude = query_altitude_list[level][0]/3.281
        query_altitude_next = query_altitude_list[level+1][0]/3.281

        # Find Time corresponding to query_altitude
        corresponding_time = np.interp(query_altitude, sorted_total_alt_list, sorted_total_timestamp_list)
        corresponding_time_next = np.interp(query_altitude_next, sorted_total_alt_list, sorted_total_timestamp_list)

        # Find Velocity corresponding to Time =NOT NECESSARY=
        # corresponding_velocity = np.interp(corresponding_time, total_timestamp_list, total_vel_list)
        # corresponding_velocity_next = np.interp(corresponding_time_next, total_timestamp_list, total_vel_list)

        # Time in level chunk
        time_in_chunk = corresponding_time_next - corresponding_time

        # Convert windspeed from mph to m/s
        wvel = ((query_altitude_list[level+1][1] + query_altitude_list[level][1])/2)*0.44704

        # Drag and drift calculations, Cd is a heavy estimate based on a couple different papers

        Cd = 1
        rho = ((query_altitude_list[level+1][3] + query_altitude_list[level][3])/2)
        Area = (maind.m()**2)*(np.pi/4)

        # effctive horizontal velocity relates to windspeed and air density AND time spent to get up to a terminal horizontal velocity
        k =  (rho * Cd * Area)/(2 * mass.kg())
        v_effective = wvel * (1-(1/(k*wvel*time_in_chunk+1)))

        drift = time_in_chunk*v_effective*3.28084
        #drift = time_in_chunk*wvel*3.28094

        i = np.sin(np.radians(((query_altitude_list[level+1][2] + query_altitude_list[level][2])/2)))
        j = np.cos(np.radians(((query_altitude_list[level+1][2] + query_altitude_list[level][2])/2)))
        position_array+= (drift)*np.array([i,j])
        vector_insert = (drift)*np.array([i,j])

        pos_array_list += [[vector_insert[0],vector_insert[1]]]

        # print(f"Time corresponding to Altitude={query_altitude}: {corresponding_time}")
        # print(f"Velocity corresponding to Time={corresponding_time}: {corresponding_velocity}")

    overland_distance = np.linalg.norm(position_array)/5280

    print()
    print()
    print("====================================================================")
    print()
    print(f"Type of simulation: {typesim}")
    print(f"Overland distance: {overland_distance} miles")
    print()
    print("====================================================================")
    print()
    
    return (pos_array_list , overland_distance)

sustainer_nominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_SUSTAINER,config.MAIN_DIAMETER_SUSTAINER,config.APOGEE_ALTITUDE_SUSTAINER,config.MAIN_ALTITUDE,config.ROCKET_MASS_SUSTAINER)
sustainer_nominal_drift_approx_posvecs = Drift_Approx(sustainer_nominal_drift_values[0],sustainer_nominal_drift_values[1],"SUS NOM",config.ROCKET_MASS_SUSTAINER,config.MAIN_DIAMETER_SUSTAINER)

sustainer_offnominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_SUSTAINER,config.MAIN_DIAMETER_SUSTAINER,config.APOGEE_ALTITUDE_SUSTAINER,config.APOGEE_ALTITUDE_SUSTAINER-config.APOGEE_OFFSET,config.ROCKET_MASS_SUSTAINER)
sustainer_offnominal_drift_approx_posvecs = Drift_Approx(sustainer_offnominal_drift_values[0],sustainer_offnominal_drift_values[1],"SUS OFFNOM",config.ROCKET_MASS_SUSTAINER,config.MAIN_DIAMETER_SUSTAINER)

booster_nominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_BOOSTER,config.MAIN_DIAMETER_BOOSTER,config.APOGEE_ALTITUDE_BOOSTER,config.MAIN_ALTITUDE,config.ROCKET_MASS_BOOSTER)
booster_nominal_drift_approx_posvecs = Drift_Approx(booster_nominal_drift_values[0],booster_nominal_drift_values[1],"BOO NOM",config.ROCKET_MASS_BOOSTER,config.MAIN_DIAMETER_BOOSTER)

booster_offnominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_BOOSTER,config.MAIN_DIAMETER_BOOSTER,config.APOGEE_ALTITUDE_BOOSTER,config.APOGEE_ALTITUDE_BOOSTER-config.APOGEE_OFFSET,config.ROCKET_MASS_BOOSTER)
booster_offnominal_drift_approx_posvecs = Drift_Approx(booster_offnominal_drift_values[0],booster_offnominal_drift_values[1],"BOO OFFNOM",config.ROCKET_MASS_BOOSTER,config.MAIN_DIAMETER_BOOSTER)

#print(sustainer_offnominal_drift_approx_posvecs[0]) # this will print an array of points (feet from FAR site), folowed by the overland distance (miles)

four_scenarios_posvecs = np.array([sustainer_nominal_drift_approx_posvecs[0],
                                   sustainer_offnominal_drift_approx_posvecs[0],
                                   booster_nominal_drift_approx_posvecs[0],
                                   booster_offnominal_drift_approx_posvecs[0]]) # all 4 scenarios for one wind speed/direction input

distances = np.array([sustainer_nominal_drift_approx_posvecs[1],
                                   sustainer_offnominal_drift_approx_posvecs[1],
                                   booster_nominal_drift_approx_posvecs[1],
                                   booster_offnominal_drift_approx_posvecs[1]])