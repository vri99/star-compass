from typing import TypedDict


class ConstellationModel(TypedDict):
    full_name: str
    lines: list[list[int]]


class StarModel(TypedDict):
    # The Hipparchus star catalogue
    # hip: int

    # star name
    proper: str

    # constellation name
    con: str

    # absolute coordinates of a star in the universe regardless of the viewer
    ra: float  # Right Ascension (longitude) 0°–360°
    dec: float  # Declination (latitude) -90°–+90°

    # relative coordinates, depending on the location and time of the observer
    alt: float  # altitude - 0°=horizon, 90°=zenith.
    az: float  # azimuth - 0°=north, 90°=east, 180°=south, 270°=west

    # logarithmic brightness scale
    mag: float  # magnitude
