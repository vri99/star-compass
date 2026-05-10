import pytest

from backend.app.data.data_processor import DataProcessor
from backend.app.data.data_processor_interfaces import DataProcessorInterface
from backend.app.repository.constellation_repository import ConstellationRepository
from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.services.service_interfaces import SkyMapperServiceInterface
from backend.app.services.sky_calculator_service import SkyCalculatorService


@pytest.fixture(scope="session")
def data_processor() -> DataProcessorInterface:
    return DataProcessor()

@pytest.fixture(scope="session")
def constellation_repository() -> ConstellationRepository:
    return ConstellationRepository()


@pytest.fixture(scope="session")
def sky_calculator() -> SkyCalculatorService:
    return SkyCalculatorService()


@pytest.fixture(scope="session")
def sky_mapper_service(
    sky_calculator: SkyCalculatorService, constellation_repository: ConstellationRepositoryInterface
) -> SkyMapperServiceInterface:
    return SkyMapperService(sky_calculator, constellation_repository)
