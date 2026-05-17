import pytest
from pandas import DataFrame

from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.services.service_interfaces import (
    ObserverContext,
    SkyCalculatorInterface, SkyMapperServiceInterface,
)
from backend.app.services.sky_mapper_service import SkyMapperService
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


@pytest.fixture(scope="class")
def observer_ctx() -> ObserverContext:
    """Provide a default Kyiv spring-evening observer context for the test class."""
    return ObserverContext(SPRING_EVENING, KYIV_LON, KYIV_LAT)


class TestSkyMapperService:
    """Tests for SkyMapperService - verifies the full sky mapping pipeline end-to-end."""

    @pytest.mark.parametrize(
        "observer_context",
        [
            ObserverContext(SPRING_EVENING, KYIV_LON, KYIV_LAT),
            ObserverContext(AUTUMN_MORNING, KYIV_LON, KYIV_LAT),
            ObserverContext(WINTER_EVENING, NORTH_POLE_LON, NORTH_POLE_LAT),
            ObserverContext(SPRING_EVENING, SOUTH_POLE_LON, NORTH_POLE_LAT),
        ],
    )
    # fixtures: sky_calculator, constellation_repository - see conftest.py
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

    # fixtures: constellation_repository, sky_mapper_service - see conftest.py
    def test_all_required_stars_present(
            self,
            observer_ctx: ObserverContext,
            constellation_repository: ConstellationRepositoryInterface,
            sky_mapper_service: SkyMapperServiceInterface
    ) -> None:
        constellations: DataFrame = sky_mapper_service._get_constellations_by_names(observer_ctx)
        set_of_star_ids: set[str] = constellation_repository.flat_star_lines_list(constellations)

        stars: DataFrame = constellation_repository.get_stars_by_constellation(constellations)

        existing_star_ids: set[str] = set(stars["hip"].astype(str))
        missing_star_ids: set[str] = set_of_star_ids - existing_star_ids

        allowed_missing_ratio = 0.01
        actual_ratio = len(missing_star_ids) / len(existing_star_ids)

        print(f"Missing stars ({len(missing_star_ids)}): {missing_star_ids}")
        assert actual_ratio <= allowed_missing_ratio, f"Too many missing stars ({len(missing_star_ids)}): {missing_star_ids}"

    # fixtures: sky_mapper_service - see conftest.py
    def test_build_response(self, observer_ctx, sky_mapper_service: SkyMapperService) -> None:
        assert sky_mapper_service.build_response(observer_ctx) is not None
