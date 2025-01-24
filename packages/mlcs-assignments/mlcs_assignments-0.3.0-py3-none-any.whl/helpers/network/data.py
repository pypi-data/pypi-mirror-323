from typing import Protocol
from dataclasses import dataclass

import os
import pandas as pd


class DataMapper(Protocol):
    def __call__(self, data: pd.DataFrame) -> pd.DataFrame:
        """Performs some transformation on the data."""
        ...


@dataclass(frozen=True)
class DataLoader:
    data_by_filename: dict[str, pd.DataFrame]

    @staticmethod
    def for_directory(directory: str) -> "DataLoader":
        return DataLoader(
            data_by_filename={
                filename: pd.read_csv(f"{directory}/{filename}")
                for filename in os.listdir(directory)
            }
        )

    def statistics(self) -> pd.DataFrame:
        return self.combine().describe()

    def one(self) -> pd.DataFrame:
        return next(iter(self.data_by_filename.values()))

    def map(self, mapper: DataMapper) -> "DataLoader":
        return DataLoader(
            data_by_filename={
                filename: mapper(data)
                for filename, data in self.data_by_filename.items()
            }
        )

    def combine(self) -> pd.DataFrame:
        return pd.concat(self.data_by_filename.values())
