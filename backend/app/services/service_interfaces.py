from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import numpy as np
from astropy.coordinates import EarthLocation, Longitude, SkyCoord  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]
from astropy.units import Quantity  # type: ignore[import-untyped]
from backend.app.schemas.requst_responce_schema import SkyResponse
from backend.app.schemas.star_constellation_schema import ConstellationSchema, StarSchema
from backend.app.types import NpFloat
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

        return np.round(astronomy_time.deg, 3)


class SkyCalculatorInterface(Protocol):
    def _convert_to_deg(self, num_array: NpFloat) -> list[Quantity]: ...

    def convert_icrs_into_alt_az(
        self,
        ctx: ObserverContext,
        star_ra_list: NpFloat,
        star_dec_list: NpFloat,
    ) -> tuple[NpFloat, NpFloat]: ...

    def _build_ICRS_frame(  # noqa: N802
        self,
        ctx: ObserverContext,
    ) -> SkyCoord: ...

    def get_visible_constellation_names(self, ctx: ObserverContext) -> set[str]: ...

    @property
    def _sky_2d_meshgrid(
        self,
    ) -> tuple[NpFloat, NpFloat]: ...


class SkyMapperServiceInterface(Protocol):
    def _get_constellations_by_names(self, observer_context: ObserverContext) -> DataFrame: ...

    def _get_stars_with_alt_az(
        self, observer_context: ObserverContext, constellations: DataFrame
    ) -> DataFrame: ...

    def _convert_data_into_response(
        self, constellations: DataFrame, stars: DataFrame
    ) -> tuple[list[ConstellationSchema], list[StarSchema]]: ...

    def build_response(self, observer_context: ObserverContext) -> SkyResponse: ...
