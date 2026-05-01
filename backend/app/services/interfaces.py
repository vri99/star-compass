from datetime import datetime
from typing import Protocol

import numpy as np
import numpy.typing as npt
from astropy.coordinates import ICRS, EarthLocation  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]
from astropy.units import Quantity
from backend.app.models.star_model import StarModel
from backend.app.schemas.star_constellation_schema import StarSchema


class SkyCalculatorInterface(Protocol):
    date: datetime
    longitude: float
    latitude: float

    def _convert_user_loc_to_astropy_loc(self) -> EarthLocation: ...

    def _convert_date_to_astropy_time(self) -> Time: ...

    def _convert_to_deg(self, num_array: npt.NDArray[np.float64]) -> list[Quantity]: ...

    def _convert_meshgrid_into_ICRS(  # noqa: N802
        self, alt_grid: npt.NDArray[np.float64], az_grid: npt.NDArray[np.float64]
    ) -> ICRS: ...

    def _generate_sky_2d_meshgrid(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...


class SkyTransformerInterface(Protocol):
    def _transform_model(self, model: StarModel) -> StarSchema: ...
