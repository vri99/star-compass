from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import numpy as np
import numpy.typing as npt
from astropy.coordinates import EarthLocation, Longitude, SkyCoord  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]
from astropy.units import Quantity  # type: ignore[import-untyped]
from backend.app.schemas.requst_responce_schema import SkyResponse
from backend.app.schemas.star_constellation_schema import ConstellationSchema, StarSchema
from pandas import DataFrame


@dataclass
class ObserverContext:
    date: datetime
    longitude: float
    latitude: float

    @property
    def user_location_on_earth(self) -> EarthLocation:
        """Convert a user's location into Astropy's EarthLocation Class."""
        return EarthLocation(lon=self.longitude, lat=self.latitude, height=0)

    @property
    def user_date_to_earth_time(self) -> Time:
        """Convert a user's datetime into Astropy's Time Class in ISO format."""
        return Time(self.date, format="datetime", scale="utc")

    @property
    def astronomy_time_for_location(self) -> float:
        """Return Local Sidereal Time (LST) in degrees for the observer's location and time."""

        time: Time = self.user_date_to_earth_time
        earth_location: EarthLocation = self.user_location_on_earth

        # Local Sidereal Time defines which part of the sky is currently overhead
        astronomy_time: Longitude = time.sidereal_time("mean", earth_location)

        return astronomy_time.deg


class SkyCalculatorInterface(Protocol):
    def _convert_to_deg(self, num_array: npt.NDArray[np.float64]) -> list[Quantity]: ...

    def convert_icrs_into_az_alt(
        self,
        ctx: ObserverContext,
        star_ra_list: npt.NDArray[np.float64],
        star_dec_list: npt.NDArray[np.float64],
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...

    def _build_ICRS_frame(  # noqa: N802
        self,
        ctx: ObserverContext,
    ) -> SkyCoord: ...

    def get_visible_constellation_names(self, ctx: ObserverContext) -> set[str]: ...

    @property
    def _sky_2d_meshgrid(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...


class SkyMapperServiceInterface(Protocol):
    def _get_constellations_by_names(self, observer_context: ObserverContext) -> DataFrame: ...

    def build_response(self, observer_context: ObserverContext) -> SkyResponse: ...

    def build_constellation_schema(self) -> list[ConstellationSchema]: ...

    def build_star_schema(self) -> StarSchema: ...

    def update_stars_with_alt_az(self) -> StarSchema: ...
