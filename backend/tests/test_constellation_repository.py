import pytest


@pytest.mark.dependency(depends=["TestDataProcessor"])
class TestConstellationRepository:
    pass