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


def Drift_Approx(drogue_result: parachute.DriftAnalysisResult, main_result: parachute.DriftAnalysisResult,typesim):
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
    level_1 = [120000, 26, 170]
    level_2 = [98000, 26, 170]
    level_3 = [45000, 125, 90]
    level_4 = [39000, 102, 90]
    level_5 = [34000, 101, 90]
    level_6 = [30000, 79, 90]
    level_7 = [24000, 61, 90]
    level_8 = [18000, 57, 85]
    level_9 = [14000, 41, 87]
    level_10 = [10000, 26, 95]
    level_11 = [6400, 14, 90]
    level_12 = [5000, 5, 60]
    level_13 = [3000, 1, 0]
    level_14 = [2500, 2, 195]
    level_15 = [2000, 2, 190]
    level_16 = [330, 1, 225]
    level_17 = [0, 1, 205]

    query_altitude_list = [level_1,level_2,level_3,level_4,level_5,level_6,level_7,level_8,level_9,level_10,level_11,level_12,level_13,level_14,level_15,level_16,level_17]

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

        # Convert windspeed from mph to fps
        wvel = ((query_altitude_list[level+1][1] + query_altitude_list[level][1])/2)*1.467

        drift = time_in_chunk*wvel

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
sustainer_nominal_drift_approx_posvecs = Drift_Approx(sustainer_nominal_drift_values[0],sustainer_nominal_drift_values[1],"SUS NOM")

sustainer_offnominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_SUSTAINER,config.MAIN_DIAMETER_SUSTAINER,config.APOGEE_ALTITUDE_SUSTAINER,config.APOGEE_ALTITUDE_SUSTAINER-config.APOGEE_OFFSET,config.ROCKET_MASS_SUSTAINER)
sustainer_offnominal_drift_approx_posvecs = Drift_Approx(sustainer_offnominal_drift_values[0],sustainer_offnominal_drift_values[1],"SUS OFFNOM")

booster_nominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_BOOSTER,config.MAIN_DIAMETER_BOOSTER,config.APOGEE_ALTITUDE_BOOSTER,config.MAIN_ALTITUDE,config.ROCKET_MASS_BOOSTER)
booster_nominal_drift_approx_posvecs = Drift_Approx(booster_nominal_drift_values[0],booster_nominal_drift_values[1],"BOO NOM")

booster_offnominal_drift_values = get_drift_data(config.DROGUE_DIAMETER_BOOSTER,config.MAIN_DIAMETER_BOOSTER,config.APOGEE_ALTITUDE_BOOSTER,config.APOGEE_ALTITUDE_BOOSTER-config.APOGEE_OFFSET,config.ROCKET_MASS_BOOSTER)
booster_offnominal_drift_approx_posvecs = Drift_Approx(booster_offnominal_drift_values[0],booster_offnominal_drift_values[1],"BOO OFFNOM")

#print(sustainer_offnominal_drift_approx_posvecs[0]) # this will print an array of points (feet from FAR site), folowed by the overland distance (miles)

four_scenarios_posvecs = np.array([sustainer_nominal_drift_approx_posvecs[0],
                                   sustainer_offnominal_drift_approx_posvecs[0],
                                   booster_nominal_drift_approx_posvecs[0],
                                   booster_offnominal_drift_approx_posvecs[0]]) # all 4 scenarios for one wind speed/direction input

distances = np.array([sustainer_nominal_drift_approx_posvecs[1],
                                   sustainer_offnominal_drift_approx_posvecs[1],
                                   booster_nominal_drift_approx_posvecs[1],
                                   booster_offnominal_drift_approx_posvecs[1]])