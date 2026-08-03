from dataclasses import dataclass

@dataclass
class RocketConfig:

    launch_site_latitude: float

    launch_site_longitude: float

    altitude_timestep: float

    susainter_csv_filename: str

    sustainer_mass: float

    sustainer_parachute_cd: float

    sustainer_parachute_diameter: float

    sustainer_reef_ratio: float
    """If `None` then the sustainer is not reefed"""

    sustainer_main_deploy_altitude: float

    booster_csv_filename: str

    booster_mass: float

    booster_parachute_cd: float

    booster_parachute_diameter: float

    booster_reef_ratio: float
    """If `None` then the booster is not reefed"""

    booster_main_deploy_altitude: float

    apogee_offset: float