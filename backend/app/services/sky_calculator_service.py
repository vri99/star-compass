from datetime import datetime

import numpy as np
import numpy.typing as npt
from astropy import units as u
from astropy.coordinates import (  # type: ignore[import-untyped]
    AltAz,
    EarthLocation,
    SkyCoord,
    get_constellation,
)
from astropy.time import Time  # type: ignore[import-untyped]
from astropy.units import Quantity
from backend.app.services.service_interfaces import ObserverContext, SkyCalculatorInterface


class SkyCalculatorService(SkyCalculatorInterface):
    def _convert_to_deg(self, num_array: npt.NDArray[np.float64]) -> list[Quantity]:
        """Convert 2D array of sky points into 1D array of astropy units."""
        """E.g. [[10.0, 45.0], [90.0, 180.0]] >> [10., 45., 90., 180.] deg"""
        return np.ravel(num_array) * u.deg

    def _build_ICRS_frame(self, ctx: ObserverContext) -> SkyCoord:  # noqa: N802
        """Convert alt/az meshgrid into 'International Celestial Reference System' equatorial coordinates for
        a given location and time."""

        # get predefined visible sky grids
        alt_grid, az_grid = self._sky_2d_meshgrid

        # flatten grids and attach degree units
        alt_grid_into_deg: list[Quantity] = self._convert_to_deg(alt_grid)
        az_grid_into_deg: list[Quantity] = self._convert_to_deg(az_grid)

        # convert user input into astropy-compatible types
        user_location: EarthLocation = ctx.user_location_on_earth
        user_time: Time = ctx.user_date_to_earth_time

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

    @property
    def _sky_2d_meshgrid(
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

    def get_visible_constellations(self, ctx: ObserverContext) -> set[str]:
        """Get all visible constellations for the user location."""
        icrs_frame: SkyCoord = self._build_ICRS_frame(ctx)

        # get list of visible constellations for given frame of coordinates
        visible_constellations: npt.NDArray[np.str_] = get_constellation(icrs_frame, short_name=True)

        # convert numpy str_ type into set unique constellation names
        return {str(x).strip().upper() for x in visible_constellations}

    def convert_icrs_into_az_alt(
        self,
        ctx: ObserverContext,
        star_ra_list: npt.NDArray[np.float64],
        star_dec_list: npt.NDArray[np.float64],
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Convert star coordinates from ICRS (ra/dec) to horizontal system (alt/az) for the observer."""
        # build sky coordinates from equatorial ra/dec arrays
        cords: SkyCoord = SkyCoord(ra=star_ra_list * u.deg, dec=star_dec_list * u.deg, frame="icrs")

        # define observer-relative frame using location and time
        alt_az_frame: AltAz = AltAz(
            obstime=ctx.user_date_to_earth_time,
            location=ctx.user_location_on_earth,
        )

        # transform equatorial coordinates to horizontal
        transformed_star_cords: AltAz = cords.transform_to(alt_az_frame)

        return transformed_star_cords.alt.deg, transformed_star_cords.az.deg
