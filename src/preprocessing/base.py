from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Tuple
import pandas as pd
import numpy as np

@dataclass(frozen=True)
class PreprocessingMetrics:
    """
    Standardizes observability for the preprocessing stage.
    Helps track data loss and memory efficiency across runs.
    """
    stage_name: str
    input_rows: int
    output_rows: int
    memory_reduction_percentage: float
    execution_time_seconds: float
    status: str

class BaseDataAssembler(ABC):
    """
    Interface for merging and memory-optimizing raw dataframes.
    """
    @abstractmethod
    def process(self, 
                df_power_meter: pd.DataFrame, 
                df_building: pd.DataFrame, 
                df_weather: pd.DataFrame) -> pd.DataFrame:
        pass

class BaseMLPreprocessor(ABC):
    """
    Interface for mathematical feature engineering (scaling, encoding).
    """
    @abstractmethod
    def prepare_ml_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        pass

    @abstractmethod
    def split_data(self, 
                   X: pd.DataFrame, 
                   y: np.ndarray, 
                   test_size: float) -> Tuple[Any, Any, Any, Any]:
        pass