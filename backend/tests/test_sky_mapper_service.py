import pytest

from backend.app.repository.constellation_repository import ConstellationRepository
from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.services.service_interfaces import (
    ObserverContext,
    SkyCalculatorInterface,
    SkyMapperServiceInterface,
)
from backend.app.services.sky_calculator_service import SkyCalculatorService
from backend.app.services.sky_mapper_service import SkyMapperService
from backend.tests.test_fixtures import (
    KYIV_LAT,
    KYIV_LON,
    LST_EXPECTED,
    MOCK_STARS_SPRING_KYIV,
    MOCK_STARS_SPRING_NORTH_POLE,
    MOCK_STARS_WINTER_KYIV,
    NORTH_POLE_LAT,
    NORTH_POLE_LON,
    SOUTH_POLE_LAT,
    SOUTH_POLE_LON,
    SPRING_EVENING,
    WINTER_EVENING,
)


@pytest.fixture
def observer_ctx() -> ObserverContext:
    return ObserverContext(SPRING_EVENING, KYIV_LON, KYIV_LAT)


@pytest.fixture(scope="class")
def sky_mapper_service() -> SkyMapperServiceInterface:
    sky_calculator: SkyCalculatorInterface = SkyCalculatorService()
    constellation_repository: ConstellationRepositoryInterface = ConstellationRepository()

    return SkyMapperService(sky_calculator, constellation_repository)


class TestSkyCalculatorService:
    def test_get_constellations_by_names(
        self, observer_ctx: ObserverContext, sky_mapper_service: SkyMapperServiceInterface
    ) -> None:
        pass
