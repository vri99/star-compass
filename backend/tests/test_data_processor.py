import pytest
from backend.app.data.data_processor import DataProcessor
from backend.app.data.data_processor_interfaces import ConstellationData


@pytest.fixture(scope="class")
def data_processor():
    return DataProcessor()


@pytest.fixture(scope="class")
def constellation_data(data_processor: DataProcessor) -> ConstellationData:
    return data_processor._get_processed_constellation_data()


class TestDataProcessor:
    def test_all_87_constellation_present(
        self,
        constellation_data: ConstellationData,
    ) -> None:
        *_, constellation_dict = constellation_data

        assert len(constellation_dict) == 87

    def test_constellation_contains_all_stars(
        self,
        constellation_data: ConstellationData,
    ) -> None:
        con_lines, _, flat_ids, _ = constellation_data

        for lines in con_lines.values():
            flat_lines: list[int] = [item for sublist in lines for item in sublist]

            assert set(flat_lines).issubset(flat_ids), (
                f"lines contain unknown HIP IDs: {set(flat_lines) - flat_ids}"
            )
