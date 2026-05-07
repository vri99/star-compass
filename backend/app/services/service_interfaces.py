from datetime import datetime
from typing import Protocol

import numpy as np
import numpy.typing as npt
from astropy.coordinates import EarthLocation, SkyCoord  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]
from astropy.units import Quantity  # type: ignore[import-untyped]


class SkyCalculatorInterface(Protocol):
    date: datetime
    longitude: float
    latitude: float

    @property
    def _user_location_on_earth(self) -> EarthLocation: ...

    @property
    def __user_date_to_earth_time(self) -> Time: ...

    def _convert_to_deg(self, num_array: npt.NDArray[np.float64]) -> list[Quantity]: ...

    def convert_icrs_into_az_alt(
        self,
        star_ra_list: npt.NDArray[np.float64],
        star_dec_list: npt.NDArray[np.float64],
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...

    def _build_ICRS_frame(  # noqa: N802
        self,
    ) -> SkyCoord: ...

    @property
    def _sky_2d_meshgrid(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...

    @property
    def astronomy_time_for_location(self) -> float: ...
