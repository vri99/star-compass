from typing import cast

import numpy as np
import numpy.typing as npt
import pandas as pd
from backend.app.data.data_processor_interfaces import ConstellationDict
from backend.app.data.files.constellation_data import CONSTELLATIONS_DATA
from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface


class ConstellationRepository(ConstellationRepositoryInterface):
    _instance = None
    _df: pd.DataFrame = None

    # Filter stars that are more than -5° below visible horizon
    __STAR_ALTITUDE_FILTER: int = -5

    # Singleton Class
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Load data into memory
            cls._df = cls.__prepare_dataframe()

        return cls._instance

    @staticmethod
    def __prepare_dataframe() -> pd.DataFrame:
        print("Data Loading...")

        return pd.DataFrame(cast(ConstellationDict, CONSTELLATIONS_DATA))

    def get_all_constellations(self) -> pd.DataFrame:
        return self._df.copy()

    def get_constellations_by_names(self, constellation_names: set[str]) -> pd.DataFrame:
        return self._df[self._df["con"].isin(constellation_names)].copy()

    def update_alt_az(self, alt: npt.NDArray[np.float64], az: npt.NDArray[np.float64]) -> None:

        self._df["az"] = az
        self._df["alt"] = alt

    def get_ra_dec_values(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        return self._df["ra"].values, self._df["dec"].values

    # TODO: DELETE?
    def get_alt_az_values(
        self,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        return self._df["alt"].values, self._df["az"].values

    def filter_alt_above_zero_stars(self) -> pd.DataFrame:
        return self._df[self._df["alt"] > self.__STAR_ALTITUDE_FILTER]

    def get_converted_constellation_dict(self) -> ConstellationDict:
        self.filter_alt_above_zero_stars()

        return self._df.to_dict("index")
