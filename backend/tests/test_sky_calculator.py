from datetime import datetime

import pytest
from astropy.coordinates import EarthLocation, SkyCoord  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]
from backend.app.services.sky_calculator_service import SkyCalculatorService

KYIV_LON = 0.0
KYIV_LAT = 90.0
TEST_DATE = datetime(2026, 7, 29, 21, 0, 0)


@pytest.fixture
def sky_calculator() -> SkyCalculatorService:
    return SkyCalculatorService(TEST_DATE, KYIV_LON, KYIV_LAT)


class TestSkyCalculator:
    def test_convert_user_loc_to_astropy_loc(self, sky_calculator: SkyCalculatorService) -> None:
        loc: EarthLocation = sky_calculator._convert_user_loc_to_astropy_loc()

        assert isinstance(loc, EarthLocation)

    def test_convert_date_to_astropy_time(self, sky_calculator: SkyCalculatorService):
        time: Time = sky_calculator._convert_date_to_astropy_time()

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

    def test_build_ICRS_frame(self, sky_calculator: SkyCalculatorService) -> None:

        icrs_frame: SkyCoord = sky_calculator._build_ICRS_frame()

        assert isinstance(icrs_frame, SkyCoord)
        assert icrs_frame.frame.name == "icrs"

    @pytest.mark.parametrize(
        "lat,lon,expected",
        [
            (90.0, 0.0, {"Ursa Minor"}),
            (-90.0, 0.0, {"Crux"}),
            (50.4, 30.5, {"Boötes"}),  # kyiv
        ],
    )
    def test_get_visible_constellations(self, lon, lat, expected) -> None:
        sky_calculator: SkyCalculatorService = SkyCalculatorService(TEST_DATE, lon, lat)

        constellations: set[str] = sky_calculator.get_visible_constellations()

        assert expected.issubset(constellations)
