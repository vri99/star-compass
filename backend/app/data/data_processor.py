import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from backend.app.data.data_processor_interfaces import (
    ConstellationData,
    ConstellationDict,
    ConstellationLines,
    ConstellationNames,
    DataProcessorInterface,
    FlatStarIds,
)

BASE_DIR = Path(__file__).parent


class DataProcessor(DataProcessorInterface):
    __HYG_file_path: str = BASE_DIR / "files" / "hyg_v42.csv"
    __constellation_names_file_path: str = BASE_DIR / "files" / "constellation_names.dat"
    __constellation_lines_file_path: str = BASE_DIR / "files" / "constellation_lines_simplified.dat"
    _constellation_data_file_path: str = BASE_DIR / "files" / "constellation_data.py"

    __MAX_MAGNITUDE: float = 5.0

    def __init__(self) -> None:
        pass

    def _process_dat_constellation_list(self) -> ConstellationNames:
        """Parse constellation names file and return a mapping of 3 char id to full name."""
        df: DataFrame = pd.read_csv(
            self.__constellation_names_file_path,
            sep="\\s+",
            usecols=[0, 1],
            index_col=0,
            comment="#",
            header=None,
        )
        # type: ignore[call-overload]

        # trim uid to 3 chars e.g. "And" from "Andromeda"
        df.index = df.index.str[:3]

        constellation_names: ConstellationNames = df[1].to_dict()

        return constellation_names

    def _process_dat_constellation_lines(self) -> ConstellationLines:
        """Parse constellation lines file and return a mapping of full name
        to list of star id groups to be connected."""
        data: ConstellationLines = defaultdict(list)
        current_key: str = ""

        with open(self.__constellation_lines_file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("*"):
                    # extract constellation full name from header line
                    current_key = line.replace("*", "").strip()
                elif line.startswith("["):
                    # transform str into a list
                    hip_list: list[str] = json.loads(line)

                    # strip asterisks from star ids and convert to int
                    data[current_key].append([int(x.strip("*")) for x in hip_list])

        return data

    def _transform_star_ids_into_set(self, constellation_stars_dict: ConstellationLines) -> FlatStarIds:  # noqa: N802
        """Flatten nested star id groups into a single set of unique star ids."""

        flat_star_ids: FlatStarIds = set()

        for stars in constellation_stars_dict.values():
            for star_group in stars:
                flat_star_ids.update(star_group)

        return flat_star_ids

    def _filter_csv_constellations(
        self,
        flat_star_ids: FlatStarIds,
    ) -> DataFrame:
        """Filter HYG star catalog by constellation HIP (star) ids and a star magnitude (brightness),
        then group by constellation."""

        df = pd.read_csv(self.__HYG_file_path, usecols=["hip", "proper", "con", "ra", "dec", "mag"]).dropna(
            subset=["con", "hip"]
        )

        # keep only stars that belong to constellation lines and are bright enough
        df_cleaned = df.loc[df["hip"].isin(flat_star_ids) & (df["mag"] < self.__MAX_MAGNITUDE)]
        # "hip" column is floating by default. Convert into int
        df_cleaned["hip"] = df_cleaned["hip"].astype(int)

        return df_cleaned

    def _get_processed_constellation_data(
        self,
    ) -> ConstellationData:
        """Orchestrate all processing steps and return a complete constellation dataset."""
        constellation_lines: ConstellationLines = self._process_dat_constellation_lines()
        constellation_names: ConstellationNames = self._process_dat_constellation_list()

        # for efficient CSV filtering
        flat_star_ids: FlatStarIds = self._transform_star_ids_into_set(constellation_lines)

        filtered_data: DataFrame = self._filter_csv_constellations(flat_star_ids)

        constellation_dict: ConstellationDict = self._combine_data_into_constellation_dict(
            filtered_data, constellation_lines, constellation_names
        )

        return (
            constellation_lines,
            constellation_names,
            flat_star_ids,
            constellation_dict,
        )

    def _combine_data_into_constellation_dict(
        self,
        df: DataFrame,
        constellation_lines: ConstellationLines,
        constellation_names: ConstellationNames,
    ) -> ConstellationDict:
        # map data for each constellation
        constellation_dict: ConstellationDict = {  # type: ignore[arg-type]
            str(con): {
                "stars": group.fillna("").to_dict("records"),
                "star_count": len(group),
                "full_name": constellation_names[con.upper()],
                "lines": constellation_lines[constellation_names[con.upper()]],
            }
            # group stars by constellation it belongs to
            for con, group in df.groupby("con")
        }

        return constellation_dict

    def _delete_file(self, file_path: Path) -> None:
        """Delete the specified file path."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.exists():
            file_path.unlink()

    def generate_data_file(self) -> None:
        """Generate a Python dictionary data file from processed constellation data."""

        data_file_path: Path = Path(self._constellation_data_file_path)

        if not data_file_path.exists():
            # unpack only the final dict, discard intermediate data
            *_, constellation_dict = self._get_processed_constellation_data()

            # check if parent directory exists
            data_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(data_file_path, "w", encoding="utf-8") as f:
                f.write("# WARNING: This is auto-generated file. Do not edit.\n")
                f.write("CONSTELLATIONS_DATA = ")

                f.write(json.dumps(constellation_dict, indent=4, ensure_ascii=False))
                f.write("\n")
