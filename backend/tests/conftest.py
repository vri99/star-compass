"""Session-scoped fixtures shared across all test modules."""

import pytest

from backend.app.data.data_processor import DataProcessor
from backend.app.data.data_processor_interfaces import DataProcessorInterface
from backend.app.repository.constellation_repository import ConstellationRepository
from backend.app.repository.repository_interfaces import ConstellationRepositoryInterface
from backend.app.services.service_interfaces import (
    SkyCalculatorInterface,
    SkyMapperServiceInterface,
)
from backend.app.services.sky_calculator_service import SkyCalculatorService
from backend.app.services.sky_mapper_service import SkyMapperService


@pytest.fixture(scope="session")
def data_processor() -> DataProcessorInterface:
    """Provide a shared DataProcessor instance for the entire test session."""
    return DataProcessor()


@pytest.fixture(scope="session")
def constellation_repository() -> ConstellationRepositoryInterface:
    """Provide the singleton ConstellationRepository loaded once per test session."""
    return ConstellationRepository()


@pytest.fixture(scope="session")
def sky_calculator() -> SkyCalculatorService:
    """Provide a shared SkyCalculatorService instance for the entire test session."""
    return SkyCalculatorService()


@pytest.fixture(scope="session")
def sky_mapper_service(
    sky_calculator: SkyCalculatorInterface,
    constellation_repository: ConstellationRepositoryInterface,
) -> SkyMapperServiceInterface:
    """Assemble a SkyMapperService with all dependencies for integration testing."""
    return SkyMapperService(sky_calculator, constellation_repository)
