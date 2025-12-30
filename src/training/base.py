from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd

class BaseModel(ABC):
    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: pd.DataFrame, y_val: pd.Series, params: Dict[str, Any]):
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> Any:
        pass

    @abstractmethod
    def save_model(self, path: str):
        pass