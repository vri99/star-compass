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


# SkyService.build_response(date, lon, lat)  ← оркестратор
#     ↓
# 1. SkyCalculatorService.get_visible_constellation_names()
#     ↓
# 2. ConstellationRepository.get_constellations_by_names()
#     ↓
# 3. ConstellationRepository.get_ra_dec_values()
#     ↓
# 4. SkyCalculatorService.convert_icrs_into_az_alt()
#     ↓
# 5. ConstellationRepository.update_alt_az()
#     ↓
# 6. ConstellationRepository.get_converted_constellation_dict()
#     ↓
# 7. SkyMapperService.to_schema()  ← тільки конвертація в DTO
#     ↓
# SkyResponse
