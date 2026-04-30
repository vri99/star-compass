from typing import Protocol

class StarInterface(Protocol):
    # absolute coordinates of a star in the universe regardless of the viewer
    _ra: float # Right Ascension (longitude) 0°–360°
    _dec: float # Declination (latitude) -90°–+90°

    # relative coordinates, depending on the location and time of the observer
    _alt: float # altitude - 0°=horizon, 90°=zenith.
    _az: float # azimuth - 0°=north, 90°=east, 180°=south, 270°=west

    # logarithmic brightness scale
    _mag: float #magnitude

    _name: str

    # Convert data to DTO
    def to_response(self) -> dict: ...