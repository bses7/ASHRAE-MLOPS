import pandas as pd
import numpy as np
from src.common.logger import get_logger
import gc

class FeatureEngineer:
    """
    Extracts temporal features and applies log transformation to the target.
    """

    def __init__(self):
        self.logger = get_logger("FeatureEngineer")

    def engineer(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Starting Feature Engineering on joined data...")

        df = self._add_time_features(df)

        if 'meter_reading' in df.columns:
            df = self._apply_log_transform(df)

        self.logger.info(f"Feature engineering complete. Columns: {list(df.columns)}")
        return df

    def _add_time_features(self, df):
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'], cache=True)

        dow = df['timestamp'].dt.dayofweek.astype(np.int8)
        df['is_weekend'] = (dow >= 5).astype(np.int8)

        del dow
        gc.collect()

        return df

    def _apply_log_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies log1p to meter_reading."""
        self.logger.debug("Applying log1p transformation to target...")
        df['meter_reading'] = np.log1p(df['meter_reading']).astype(np.float32)
        return df