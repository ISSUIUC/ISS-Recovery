from io import StringIO
import os
import numpy as np
import pandas as pd

import ork_config as config

def meters_to_latlon(x_m, y_m):
    m_per_lon = config.M_PER_DEG_LAT * np.cos(np.radians(config.LATITUDE))
    return config.LATITUDE + y_m / config.M_PER_DEG_LAT, config.LONGITUDE + x_m / m_per_lon

def load_openrocket_csv(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Not found: '{filepath}'")

    with open(filepath, 'r') as f:
        lines = f.readlines()

    data_lines = [l for l in lines
                  if l.strip() and not l.strip().startswith('#')]

    df = pd.read_csv(
        StringIO(''.join(data_lines)),
        header=None,
        names=['time_s', 'alt_ft', 'lat', 'lon', 'mass_kg']
    )

    # Converting feet to meters
    df['alt_m'] = df['alt_ft'] * 0.3048

    m_per_lon       = config.M_PER_DEG_LAT * np.cos(np.radians(config.LATITUDE))
    df['x_east_m']  = (df['lon'] - config.LONGITUDE) * m_per_lon
    df['y_north_m'] = (df['lat'] - config.LATITUDE) * config.M_PER_DEG_LAT

    return df

def get_apogee_state(df, label):
    """Gets apogee state from OpenRocket CSV dataframe and prints it to console"""
    idx     = df['alt_m'].idxmax()
    row     = df.loc[idx]
    alt_m   = float(row['alt_m'])
    x_east  = float(row['x_east_m'])
    y_north = float(row['y_north_m'])

    print(f"  {label}: {alt_m:.0f} m AGL ({alt_m*3.281/1000:.2f} kft) "
          f"at t={float(row['time_s']):.1f}s  |  "
          f"pad offset {x_east:+.0f} m E, {y_north:+.0f} m N")
    
    return alt_m, x_east, y_north


if __name__ == "__main__":
    print("Loading OpenRocket CSVs...")
    sus_df = load_openrocket_csv(f"drift_analysis/ork/{config.SUSTAINER_CSV}")
    boo_df = load_openrocket_csv(f"drift_analysis/ork/{config.BOOSTER_CSV}")

    print(f"  Sustainer: {len(sus_df)} rows, "
        f"max alt {sus_df['alt_m'].max():.0f} m ({sus_df['alt_m'].max()*3.281/1000:.1f} kft), "
        f"flight time {sus_df['time_s'].max():.1f} s")
    
    print(f"  Booster  : {len(boo_df)} rows, "
        f"max alt {boo_df['alt_m'].max():.0f} m ({boo_df['alt_m'].max()*3.281/1000:.1f} kft), "
        f"flight time {boo_df['time_s'].max():.1f} s")

    print("\nApogee states:")
    sus_apogee_alt, sus_apo_x, sus_apo_y = get_apogee_state(sus_df, "Sustainer")
    boo_apogee_alt, boo_apo_x, boo_apo_y = get_apogee_state(boo_df, "Booster")