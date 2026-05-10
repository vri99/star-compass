from dataclasses import dataclass

from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.schemas.requst_responce_schema import SkyResponse
from backend.app.schemas.star_constellation_schema import ConstellationSchema, StarSchema
from backend.app.services.service_interfaces import (
    ObserverContext,
    SkyCalculatorInterface,
    SkyMapperServiceInterface,
)
from pandas import DataFrame


@dataclass
class SkyMapperService(SkyMapperServiceInterface):
    """Orchestrates sky data retrieval and transformation into a structured API response."""

    observer_context: ObserverContext
    __sky_calculator: SkyCalculatorInterface
    __constellation_repository: ConstellationRepositoryInterface

    def _get_constellations_by_names(self, observer_context: ObserverContext) -> DataFrame:
        """Determine visible constellations for the observer and return them as a DataFrame."""
        visible_constellation_names_set: set[str] = self.__sky_calculator.get_visible_constellation_names(
            observer_context
        )

        return self.__constellation_repository.get_constellations_by_names(visible_constellation_names_set)

    def _get_stars_with_alt_az(
        self, observer_context: ObserverContext, constellations: DataFrame
    ) -> DataFrame:
        """Fetch stars for the visible constellations and compute their alt/az positions."""
        stars = self.__constellation_repository.get_stars_by_constellation(constellations)
        ra, dec = self.__constellation_repository.get_ra_dec_values(stars)

        # convert equatorial coordinates to observer-relative horizontal coordinates
        alt, az = self.__sky_calculator.convert_icrs_into_alt_az(observer_context, ra, dec)

        return self.__constellation_repository.update_stars_with_alt_az(stars, alt, az)

    def _convert_data_into_response(
        self, constellations: DataFrame, stars: DataFrame
    ) -> tuple[list[ConstellationSchema], list[StarSchema]]:
        """Serialize constellation and star DataFrames into schema-validated response objects."""

        # rename DataFrame columns to match the schema field names before unpacking
        cons_list_dict: list[dict] = self.__constellation_repository.df_to_dict(constellations, {"con": "id"})
        stars_list_dict: list[dict] = self.__constellation_repository.df_to_dict(
            constellations, {"proper": "name", "con": "constellation_name"}
        )

        constellations_list: list[ConstellationSchema] = [ConstellationSchema(**c) for c in cons_list_dict]
        stars_list: list[StarSchema] = [StarSchema(**s) for s in stars_list_dict]

        return constellations_list, stars_list

    def build_response(self, observer_context: ObserverContext) -> SkyResponse:
        """Build a complete SkyResponse for the observer's location and time."""
        constellations: DataFrame = self._get_constellations_by_names(observer_context)
        stars: DataFrame = self._get_stars_with_alt_az(observer_context, constellations)

        constellations_response, stars_response = self._convert_data_into_response(constellations, stars)

        return SkyResponse(
            astronomy_time=observer_context.astronomy_time_for_location,
            stars=stars_response,
            constellations=constellations_response,
        )
