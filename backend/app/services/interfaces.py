from typing import Protocol
from datetime import datetime

from astropy.time import Time # type: ignore[import-untyped]
from astropy.coordinates import EarthLocation, ICRS  # type: ignore[import-untyped]
from astropy.units import Quantity

from backend.app.models.star_model import StarModel
from backend.app.schemas.star_constellation_schema import StarSchema

class SkyCalculatorInterface(Protocol):
    date: datetime
    longitude: float
    latitude: float

    def __convert_user_loc_to_astropy_loc(self, longitude: float, latitude: float, date: datetime ) -> EarthLocation: ...

    def __convert_date_to_astropy_time(self, date: datetime) -> Time: ...

    def __convert_to_deg(self, quantity_array: list[float]) -> list[Quantity]: ...

    def convert_meshgrid_into_ICRS(self, altitude: tuple[float, float], azimuth: tuple[float, float]) -> ICRS: ...

    def __generate_sky_2d_meshgrid(self) -> list[tuple[float]]: ...

class SkyTransformerInterface(Protocol):

    def transform(self, model: StarModel) -> StarSchema: ...