from datetime import datetime

import numpy as np
import numpy.typing as npt
import pytest
from astropy.coordinates import EarthLocation, SkyCoord  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]

from backend.app.services.service_interfaces import ObserverContext
from backend.app.services.sky_calculator_service import SkyCalculatorService
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

type NpFloat = npt.NDArray[np.float64]


@pytest.fixture
def observer_ctx() -> ObserverContext:
    return ObserverContext(SPRING_EVENING, KYIV_LON, KYIV_LAT)


@pytest.fixture
def sky_calculator() -> SkyCalculatorService:
    return SkyCalculatorService()


class TestSkyCalculator:
    def test_user_location_on_earth(self, observer_ctx: ObserverContext) -> None:
        loc: EarthLocation = observer_ctx.user_location_on_earth

        assert isinstance(loc, EarthLocation)

    def test__user_date_to_earth_time(self, observer_ctx: ObserverContext):
        time: Time = observer_ctx.user_date_to_earth_time

        assert isinstance(time, Time)

    def test_generate_sky_2d_meshgrid(self, sky_calculator) -> None:
        alt_grid, az_grid = sky_calculator._sky_2d_meshgrid

        # correct shape: 20 azimuths x 10 altitudes
        assert alt_grid.shape == (20, 10)
        assert az_grid.shape == (20, 10)

        # altitude range 10°–90°
        assert alt_grid.min() == 10.0
        assert alt_grid.max() == 90.0

        # azimuth range 0°–360°
        assert az_grid.min() == 0.0
        assert az_grid.max() == 360.0

    def test_build_ICRS_frame(  # noqa: N802
        self, sky_calculator: SkyCalculatorService, observer_ctx: ObserverContext
    ) -> None:

        icrs_frame: SkyCoord = sky_calculator._build_ICRS_frame(observer_ctx)

        assert isinstance(icrs_frame, SkyCoord)
        assert icrs_frame.frame.name == "icrs"

    @pytest.mark.parametrize(
        "lat,lon,expected",
        [
            (NORTH_POLE_LAT, NORTH_POLE_LON, {"UMI"}),
            (SOUTH_POLE_LAT, SOUTH_POLE_LON, {"CRU"}),
            (KYIV_LAT, KYIV_LON, {"BOO"}),
        ],
    )
    def test_get_visible_constellations(
        self, lon: float, lat: float, expected: set[str], sky_calculator: SkyCalculatorService
    ) -> None:
        observer_ctx: ObserverContext = ObserverContext(SPRING_EVENING, lon, lat)

        constellations: set[str] = sky_calculator.get_visible_constellations(observer_ctx)

        assert expected.issubset(constellations)

    @pytest.mark.parametrize(
        "lat,lon,date,stars",
        [
            (KYIV_LAT, KYIV_LON, SPRING_EVENING, MOCK_STARS_SPRING_KYIV),
            (NORTH_POLE_LAT, NORTH_POLE_LON, SPRING_EVENING, MOCK_STARS_SPRING_NORTH_POLE),
            (KYIV_LAT, KYIV_LON, WINTER_EVENING, MOCK_STARS_WINTER_KYIV),
        ],
        ids=["spring_kyiv", "spring_north_pole", "winter_kyiv"],
    )
    def test_convert_icrs_into_az_alt(
        self, lat: float, lon: float, date: datetime, stars: set[str], sky_calculator: SkyCalculatorService
    ) -> None:
        observer_ctx: ObserverContext = ObserverContext(date, lon, lat)

        ra: NpFloat = np.array([s[0] for s in stars])
        dec: NpFloat = np.array([s[1] for s in stars])
        expected_alt: NpFloat = np.array([s[2] for s in stars])
        expected_az: NpFloat = np.array([s[3] for s in stars])

        alt, az = sky_calculator.convert_icrs_into_az_alt(observer_ctx, ra, dec)

        assert alt == pytest.approx(expected_alt, abs=0.001)
        assert az == pytest.approx(expected_az, abs=0.001)

    @pytest.mark.parametrize("lat,lon,date,expected_lst_range", LST_EXPECTED)
    def test_astronomy_time_for_location(
        self,
        lat: float,
        lon: float,
        date: datetime,
        expected_lst_range: set[str],
    ) -> None:
        observer_ctx: ObserverContext = ObserverContext(date, lon, lat)

        result: float = observer_ctx.astronomy_time_for_location

        assert round(result, 4) == pytest.approx(expected_lst_range, abs=0.001)
