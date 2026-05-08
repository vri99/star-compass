from dataclasses import dataclass

from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.schemas.requst_responce_schema import SkyResponse
from backend.app.services.service_interfaces import (
    ObserverContext,
    SkyCalculatorInterface,
    SkyMapperServiceInterface,
)
from pandas import DataFrame


@dataclass
class SkyMapperService(SkyMapperServiceInterface):
    __sky_calculator: SkyCalculatorInterface
    __constellation_repository: ConstellationRepositoryInterface

    def _get_constellations_by_names(self, observer_context: ObserverContext) -> DataFrame:
        visible_constellation_names_set: set[str] = self.__sky_calculator.get_visible_constellation_names(
            observer_context
        )

        return self.__constellation_repository.get_constellations_by_names(visible_constellation_names_set)

    def build_response(self, observer_context: ObserverContext) -> SkyResponse:
        pass