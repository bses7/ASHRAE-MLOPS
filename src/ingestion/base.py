from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator, Any
import pandas as pd

@dataclass(frozen=True)
class IngestionMetrics:
    """
    Standardizes the metadata
    """
    entity_name: str
    rows_processed: int
    execution_time_seconds: float
    status: str 

class BaseReader(ABC):
    """
    Class for reading data from any source.
    Ensures all readers implement a chunked reading strategy.
    """
    
    @abstractmethod
    def read_chunks(self) -> Generator[pd.DataFrame, None, None]:
        """
        Yield DataFrames in chunks to maintain memory efficiency.
        """
        pass

    @property
    @abstractmethod
    def schema_definition(self) -> dict[str, Any]:
        """
        Return the mapping of column names to data types.
        """
        pass


class BaseWriter(ABC):
    """
    Class for writing data to any sink (MariaDB, Snowflake, etc.).
    """

    @abstractmethod
    def write_chunk(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Logic to write a single dataframe chunk to the destination.
        """
        pass

    @abstractmethod
    def truncate_table(self, table_name: str) -> None:
        """
        Logic to clear the table to ensure ingestion idempotency.
        """
        pass