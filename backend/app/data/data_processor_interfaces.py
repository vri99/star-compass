from typing import Protocol, TypedDict

type ConstellationLines = dict[str, list[list[int]]]
type ConstellationNames = dict[str, str]
type FlatStarIds = set[int]


class StarData(TypedDict):
    hip: int
    proper: str
    ra: float
    dec: float
    mag: float


class ConstellationEntry(TypedDict):
    stars: list[StarData]
    star_count: int
    full_name: str
    lines: list[list[int]]


type ConstellationDict = dict[str, ConstellationEntry]

type ConstellationData = tuple[ConstellationLines, ConstellationNames, FlatStarIds, ConstellationDict]


class DataProcessorInterface(Protocol):
    __HYG_file_path: str
    __constellation_names_file: str
    __constellation_lines_file: str
    _constellation_data_file: str
    __MAX_MAGNITUDE: float

    def _process_dat_constellation_list(self) -> ConstellationNames: ...

    def _process_dat_constellation_lines(self) -> ConstellationLines: ...

    def _process_csv_constellations(
        self,
        constellation_lines: ConstellationLines,
        constellation_names: ConstellationNames,
        flat_star_ids: FlatStarIds,
    ) -> ConstellationDict: ...

    def _transform_star_ids_into_set(self, constellation_stars_dict: ConstellationLines) -> FlatStarIds: ...

    def _get_processed_constellation_data(
        self,
    ) -> ConstellationData: ...

    def generate_data_file(self) -> None: ...
