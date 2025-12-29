import pandas as pd
import numpy as np
from typing import Generator, Any
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import is_categorical_dtype

from src.common.logger import get_logger
from src.ingestion.base import BaseReader
from src.schemas.raw_schemas import RAW_DATA_TYPES

class CSVIngestor(BaseReader):
    """
    Handles memory-efficient reading of CSV files with dual-pass optimization:
    1. Schema Enforcement (via RAW_DATA_TYPES)
    2. Dynamic Downcasting (via _reduce_mem_usage)
    """

    def __init__(self, file_path: str, file_key: str, batch_size: int = 500000): 
        self.file_path = file_path
        self.file_key = file_key
        self.batch_size = batch_size
        self._dtypes = RAW_DATA_TYPES[self.file_key]
        self.logger = get_logger("CSVIngestor")

    @property
    def schema_definition(self) -> dict[str, Any]:
        """Implementation of BaseReader property."""
        return self._dtypes

    def _reduce_mem_usage(self, df: pd.DataFrame, use_float16: bool = False) -> pd.DataFrame:
        """
        Iterates through columns and modifies data types to reduce memory footprint.
        """
        start_mem = df.memory_usage().sum() / 1024**2
        
        for col in df.columns:
            if is_datetime(df[col]) or is_categorical_dtype(df[col]):
                continue
                
            col_type = df[col].dtype
            
            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                
                if str(col_type)[:3] == "int":
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)  
                else:
                    if use_float16 and c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
            else:
                pass

        end_mem = df.memory_usage().sum() / 1024**2
        self.logger.debug(
            f"Mem usage: {start_mem:.2f}MB -> {end_mem:.2f}MB "
            f"({100 * (start_mem - end_mem) / start_mem:.1f}% reduction)"
        )
        return df

    def read_chunks(self) -> Generator[pd.DataFrame, None, None]:
        """Reads CSV in chunks to handle 20M+ rows without OOM."""
        self.logger.info(f"Starting chunked read for {self.file_path}")
        
        try:
            date_cols = [k for k, v in self._dtypes.items() if "datetime" in str(v)]
            
            reader = pd.read_csv(
                self.file_path,
                chunksize=self.batch_size,
                dtype={k: v for k, v in self._dtypes.items() if k not in date_cols},
                parse_dates=date_cols
            )
            
            for i, chunk in enumerate(reader):
                optimized_chunk = self._reduce_mem_usage(chunk)
                
                yield optimized_chunk
                
                if i % 5 == 0:
                    self.logger.info(f"Processed batch {i+1} ({ (i+1) * self.batch_size } rows)...")
                    
        except FileNotFoundError:
            self.logger.error(f"Source file not found: {self.file_path}")
            raise