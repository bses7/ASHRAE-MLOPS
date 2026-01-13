from abc import ABC, abstractmethod
import pandas as pd
from typing import Any

class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, y_true: Any, y_pred: Any) -> dict:
        pass

class BaseExplainer(ABC):
    @abstractmethod
    def explain(self, model: Any, data_row: pd.Series) -> Any:
        pass