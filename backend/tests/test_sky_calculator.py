from datetime import datetime

import pytest
from astropy.coordinates import EarthLocation
from astropy.time import Time
from backend.app.services.sky_calculator_service import SkyCalculatorService

KYIV_LON = 50.450001
KYIV_LAT = 30.523333
TEST_DATE = datetime(2026, 4, 29, 21, 0, 0)


@pytest.fixture
def sky_calculator():
    return SkyCalculatorService(TEST_DATE, KYIV_LON, KYIV_LAT)


class TestSkyCalculator:
    def test_convert_user_loc_to_astropy_loc(self, sky_calculator: SkyCalculatorService):
        loc: EarthLocation = sky_calculator._convert_user_loc_to_astropy_loc()

        assert isinstance(loc, EarthLocation)

    def test_convert_date_to_astropy_time(self, sky_calculator: SkyCalculatorService):
        time: Time = sky_calculator._convert_date_to_astropy_time()

        assert isinstance(time, Time)

    def test_generate_sky_2d_meshgrid(self, sky_calculator):
        alt_grid, az_grid = sky_calculator._generate_sky_2d_meshgrid()

        # correct shape: 20 azimuths x 10 altitudes
        assert alt_grid.shape == (20, 10)
        assert az_grid.shape == (20, 10)

        # altitude range 10°–90°
        assert alt_grid.min() == 10.0
        assert alt_grid.max() == 90.0

        # azimuth range 0°–360°
        assert az_grid.min() == 0.0
        assert az_grid.max() == 360.0
