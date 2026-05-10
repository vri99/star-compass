import pytest
from pandas import DataFrame

from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.services.service_interfaces import (
    ObserverContext,
    SkyCalculatorInterface,
)
from backend.tests.test_fixtures import (
    AUTUMN_MORNING,
    KYIV_LAT,
    KYIV_LON,
    NORTH_POLE_LAT,
    NORTH_POLE_LON,
    SOUTH_POLE_LON,
    SPRING_EVENING,
    WINTER_EVENING,
)


class TestSkyCalculatorService:
    @pytest.mark.parametrize(
        "observer_context",
        [
            ObserverContext(SPRING_EVENING, KYIV_LON, KYIV_LAT),
            ObserverContext(AUTUMN_MORNING, KYIV_LON, KYIV_LAT),
            ObserverContext(WINTER_EVENING, NORTH_POLE_LON, NORTH_POLE_LAT),
            ObserverContext(SPRING_EVENING, SOUTH_POLE_LON, NORTH_POLE_LAT),
        ],
    )
    def test_get_constellations_by_names_match_all_constellations(
        self,
        observer_context: ObserverContext,
        sky_calculator: SkyCalculatorInterface,
        constellation_repository: ConstellationRepositoryInterface,
    ) -> None:
        visible_constellation_names_set: set[str] = sky_calculator.get_visible_constellation_names(
            observer_context
        )

        constellations_from_df: DataFrame = constellation_repository.get_constellations_by_names(
            visible_constellation_names_set
        )

        assert len(visible_constellation_names_set) == len(constellations_from_df)


# TODO: показник світлового забруднення на фронтенд
