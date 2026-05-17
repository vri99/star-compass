from typing import cast

from pandas import DataFrame

from backend.app.data.data_processor_interfaces import ConstellationDict, StarDict
from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.types import NpFloat


class ConstellationRepository(ConstellationRepositoryInterface):
    """Singleton repository that loads constellation and star data into memory on first instantiation."""

    _instance = None
    _df: DataFrame = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # load static datasets once — avoids re-reading on every request
            cls.df_constellations, cls.df_stars = cls.__prepare_dataframe()

        return cls._instance

    @staticmethod
    def __prepare_dataframe() -> tuple[DataFrame, DataFrame]:
        """Load raw constellation/star dicts into DataFrames with normalized index columns."""
        from backend.app.data.files.constellation_data import CONSTELLATIONS, STARS

        print("\nData Loading...")

        constellation_data: DataFrame = DataFrame.from_dict(
            cast(ConstellationDict, CONSTELLATIONS), orient="index"
        )

        star_data: DataFrame = DataFrame.from_dict(cast(StarDict, STARS), orient="index")

        # reset_index promotes dict keys to a column; rename gives it a domain-meaningful name
        return constellation_data.reset_index().rename(
            columns={"index": "con"}
        ), star_data.reset_index().rename(columns={"index": "hip"})

    def get_constellations_by_names(self, constellation_names: set[str]) -> DataFrame:
        """Return a filtered copy of the constellations DataFrame matching the given name set."""
        return self.df_constellations[self.df_constellations["con"].isin(constellation_names)].copy()

    def flat_star_lines_list(self, constellations: DataFrame) -> set[str]:
        """Return all star ids (hip) that belong to any of the given star list (lines)
        in the constellations DataFrame."""
        return set(constellations["lines"].explode().explode().astype(str))

    def get_stars_by_constellation(self, constellations: DataFrame) -> DataFrame:
        """Return all stars that belong to any of the given star list in the constellations DataFrame."""
        set_of_star_ids_of_constellation: set[str] = self.flat_star_lines_list(constellations)

        return self.df_stars[self.df_stars["hip"].isin(set_of_star_ids_of_constellation)].copy()

    def get_ra_dec_values(self, stars: DataFrame) -> tuple[NpFloat, NpFloat]:
        """Extract right ascension and declination arrays from the stars DataFrame."""
        return stars["ra"].to_numpy(), stars["dec"].to_numpy()

    def update_stars_with_alt_az(self, stars: DataFrame, alt, az) -> DataFrame:
        """Attach rounded altitude/azimuth values to the stars DataFrame in-place."""
        stars["alt"] = alt.round(3)
        stars["az"] = az.round(3)

        return stars

    def df_to_dict(self, data: DataFrame, rename_columns: dict[str, str]) -> list[dict]:
        """Rename columns and convert the DataFrame to a list of row dicts."""
        return data.rename(columns=rename_columns).to_dict(orient="records")
