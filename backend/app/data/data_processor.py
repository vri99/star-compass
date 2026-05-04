import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from backend.app.data.data_processor_interfaces import (
    ConstellationData,
    ConstellationDict,
    ConstellationLines,
    ConstellationNames,
    DataProcessorInterface,
    FlatStarIds,
)
from pandas import DataFrame

BASE_DIR = Path(__file__).parent


class DataProcessor(DataProcessorInterface):
    __constellation_names_file_path: str = BASE_DIR / "files" / "constellation_names.dat"
    __constellation_lines_file_path: str = BASE_DIR / "files" / "constellation_lines_simplified.dat"
    __constellation_data_file_path: str = BASE_DIR / "files" / "constellation_data.py"
    __HYG_file_path: str = BASE_DIR / "files" / "hyg_v42.csv"

    def __init__(self) -> None:
        pass

    def _process_dat_constellation_list(self) -> ConstellationNames:
        df: DataFrame = pd.read_csv(
            self.__constellation_names_file_path,
            sep="\\s+",
            usecols=[0, 1],
            index_col=0,
            comment="#",
            header=None,
        )
        df.index = df.index.str[:3]

        constellation_names: ConstellationNames = df[1].to_dict()

        return constellation_names

    def _process_dat_constellation_lines(self) -> ConstellationLines:
        data: ConstellationLines = defaultdict(list)
        current_key: str = ""

        with open(self.__constellation_lines_file_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("*"):
                    # remove excessive symbols from constellation name
                    current_key = line.replace("*", "").strip()
                elif line.startswith("["):
                    # transform str into a list
                    hip_list: list[str] = json.loads(line)

                    # remove all * from star_ids and add it to the list
                    data[current_key].append([int(x.strip("*")) for x in hip_list])

        return data

    def _transform_star_ids_into_set(self, constellation_stars_dict: ConstellationLines) -> FlatStarIds:  # noqa: N802

        flat_star_ids: FlatStarIds = set()

        for stars in constellation_stars_dict.values():
            for star_group in stars:
                flat_star_ids.update(star_group)

        return flat_star_ids

    def _get_processed_constellation_data(
        self,
    ) -> ConstellationData:
        constellation_lines: ConstellationLines = self._process_dat_constellation_lines()
        constellation_names: ConstellationNames = self._process_dat_constellation_list()
        flat_star_ids: FlatStarIds = self._transform_star_ids_into_set(constellation_lines)

        constellation_dict: ConstellationDict = self._process_csv_constellations(
            constellation_lines, constellation_names, flat_star_ids
        )

        return (
            constellation_lines,
            constellation_names,
            flat_star_ids,
            constellation_dict,
        )

    def _process_csv_constellations(
        self,
        constellation_lines: ConstellationLines,
        constellation_names: ConstellationNames,
        flat_star_ids: FlatStarIds,
    ) -> ConstellationDict:
        df = pd.read_csv(self.__HYG_file_path, usecols=["hip", "proper", "con", "ra", "dec", "mag"]).dropna(
            subset=["con", "hip"]
        )

        df_cleaned = df[df["hip"].isin(flat_star_ids) & (df["mag"] < 5)]

        # TODO: Define typing

        df_cleaned["hip"] = df_cleaned["hip"].astype(int)

        grouped = df_cleaned.groupby("con")

        constellation_dict: ConstellationDict = {
            con: {
                "stars": group.drop(columns="con").fillna("").to_dict("records"),
                "star_count": len(group),
                "full_name": constellation_names[con.upper()],
                "lines": constellation_lines[constellation_names[con.upper()]],
            }
            for con, group in grouped
        }

        return constellation_dict

    def generate_data_file(self) -> None:
        data_file_path: Path = Path(self.__constellation_data_file_path)

        if not data_file_path.exists():
            *_, constellation_dict = self._get_processed_constellation_data()

            data_file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(data_file_path, "w", encoding="utf-8") as f:
                f.write("# WARNING: This is auto-generated file. Do not edit.\n")
                f.write("CONSTELLATIONS_DATA = ")

                f.write(json.dumps(constellation_dict, indent=4, ensure_ascii=False))
                f.write("\n")
        else:
            pass


if __name__ == "__main__":
    dp = DataProcessor()

    dp.generate_data_file()
