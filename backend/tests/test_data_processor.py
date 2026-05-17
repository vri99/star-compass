from pathlib import Path

import pytest

from backend.app.data.data_processor import DataProcessor
from backend.app.data.data_processor_interfaces import DataProcessorInterface


@pytest.mark.dependency()
class TestDataProcessor:
    """Validates that DataProcessor correctly parses and transforms raw constellation source files."""

    def test_file_is_created(self, data_processor: DataProcessor) -> None:
        data_file_path: Path = Path(data_processor._constellation_data_file_path)

        assert data_file_path.exists(), f"For some reason the file {data_file_path.name} has not been created"

    def test_all_88_constellation_present(
            self,
            data_processor: DataProcessorInterface,
    ) -> None:
        *_, data = data_processor._get_processed_constellation_data()
        constellation_dict, _ = data

        assert len(constellation_dict) == 88
