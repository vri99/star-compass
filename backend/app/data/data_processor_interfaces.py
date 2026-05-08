from typing import Protocol

from pandas.core.interchange.dataframe_protocol import DataFrame

from backend.app.models.constellation_models import ConstellationModel

type ConstellationLines = dict[str, list[list[int]]]
type ConstellationNames = dict[str, str]
type FlatStarIds = set[int]

type ConstellationDict = dict[str, ConstellationModel]
type ConstellationData = tuple[ConstellationLines, ConstellationNames, FlatStarIds, ConstellationDict]


class DataProcessorInterface(Protocol):
    __HYG_file_path: str
    __constellation_names_file_path: str
    __constellation_lines_file_path: str
    _constellation_data_file_path: str
    __MAX_MAGNITUDE: float

    def _process_dat_constellation_list(self) -> ConstellationNames: ...

    def _process_dat_constellation_lines(self) -> ConstellationLines: ...

    def _filter_csv_constellations(
        self,
        flat_star_ids: FlatStarIds,
    ) -> DataFrame: ...

    def _combine_data_into_constellation_dict(
        self,
        df: DataFrame,
        constellation_lines: ConstellationLines,
        constellation_names: ConstellationNames,
    ) -> ConstellationDict: ...

    def _transform_star_ids_into_set(self, constellation_stars_dict: ConstellationLines) -> FlatStarIds: ...

    def _get_processed_constellation_data(
        self,
    ) -> ConstellationData: ...

    def generate_data_file(self) -> None: ...
