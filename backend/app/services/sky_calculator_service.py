from datetime import datetime

import numpy as np
import numpy.typing as npt
from astropy import units as u
from astropy.coordinates import (  # type: ignore[import-untyped]
    ICRS,
    AltAz,
    EarthLocation,
    SkyCoord,
)
from astropy.time import Time  # type: ignore[import-untyped]
from astropy.units import Quantity
from backend.app.services.interfaces import SkyCalculatorInterface


class SkyCalculatorService(SkyCalculatorInterface):
    def __init__(self, date: datetime, longitude: float, latitude: float) -> None:
        self.date = date
        self.longitude = longitude
        self.latitude = latitude

    def _convert_user_loc_to_astropy_loc(self) -> EarthLocation:
        """Convert a user's location into Astropy's EarthLocation Class."""
        return EarthLocation(lon=self.longitude, lat=self.latitude, height=0)

    def _convert_date_to_astropy_time(self) -> Time:
        """Convert a user's datetime into Astropy's Time Class in ISO format."""
        return Time(self.date, format="datetime", scale="utc")

    def _convert_to_deg(self, num_array: npt.NDArray[np.float64]) -> list[Quantity]:
        """Convert 2D array of sky points into 1D array of astropy units."""
        """E.g. [[10.0, 45.0], [90.0, 180.0]] >> [10., 45., 90., 180.] deg"""
        return np.ravel(num_array) * u.deg

    def _convert_meshgrid_into_ICRS(
        self, alt_grid: npt.NDArray[np.float64], az_grid: npt.NDArray[np.float64]
    ) -> ICRS:
        """Convert alt/az meshgrid into 'International Celestial Reference System' equatorial coordinates for a given location and time."""  # noqa: E501
        # flatten grids and attach degree units
        alt_grid_into_deg: list[Quantity] = self._convert_to_deg(alt_grid)
        az_grid_into_deg: list[Quantity] = self._convert_to_deg(az_grid)

        # convert user input into astropy-compatible types
        user_location: EarthLocation = self._convert_user_loc_to_astropy_loc()
        user_time: Time = self._convert_date_to_astropy_time()

        # build a coordinate object in the Altitude-Azimuth frame (Horizontal coordinates)
        alt_az_cords = SkyCoord(
            alt=alt_grid_into_deg,
            az=az_grid_into_deg,
            frame=AltAz(
                location=user_location,
                obstime=user_time,
            ),
        )

        # convert Horizontal coordinates into Equatorial coordinates (Right Ascension/Declination)
        return alt_az_cords.transform_to("icrs")

    def _generate_sky_2d_meshgrid(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Generate a 2D meshgrid of altitude and azimuth values covering the visible sky."""
        # 0° to 360° - full compass
        azimuths: npt.NDArray[np.float64] = np.linspace(0, 360, 20, dtype=np.float64)

        # 10° to 90° - excludes horizon
        altitudes: npt.NDArray[np.float64] = np.linspace(10, 90, 10, dtype=np.float64)

        # alt_grid - sky is divided on 10 heights, az_grid - sky is divided on 20 directions
        # = 200 sky points
        alt_grid, az_grid = np.meshgrid(altitudes, azimuths)

        return alt_grid, az_grid
