from typing import Protocol

import numpy as np
import numpy.typing as npt
import pandas as pd
from backend.app.data.data_processor_interfaces import ConstellationDict


class ConstellationRepositoryInterface(Protocol):
    def get_all_constellations(self) -> pd.DataFrame: ...

    def get_constellations_by_names(self, constellation_names: set[str]) -> pd.DataFrame: ...

    def update_alt_az(
        self,
        alt: npt.NDArray[np.float64],
        az: npt.NDArray[np.float64],
    ) -> None: ...

    def get_ra_dec_values(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...

    def get_alt_az_values(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]: ...

    def filter_alt_above_zero_stars(self) -> pd.DataFrame: ...

    def get_converted_constellation_dict(self) -> ConstellationDict: ...
