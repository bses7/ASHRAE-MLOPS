import pandas as pd
import numpy as np
from src.common.logger import get_logger

class FeatureEngineer:
    """
    Handles domain-specific feature engineering for the ASHRAE dataset.
    Extracts temporal features and applies log transformation to the target.
    """

    def __init__(self):
        self.logger = get_logger("FeatureEngineer")

    def engineer(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main entry point for engineering features."""
        self.logger.info("Starting Feature Engineering on joined data...")

        # 1. Temporal Features (Crucial for Energy patterns)
        df = self._add_time_features(df)

        # 2. Target Engineering (Log Transformation)
        # Meter readings often have high variance; log(1+x) stabilizes this
        if 'meter_reading' in df.columns:
            df = self._apply_log_transform(df)

        self.logger.info(f"Feature engineering complete. Columns: {list(df.columns)}")
        return df

    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts hour, day of week, and weekend flags."""
        self.logger.debug("Extracting weekend features from timestamp...")

        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        df['dayofweek'] = df['timestamp'].dt.dayofweek.astype(np.int8)

        df['is_weekend'] = (df['dayofweek'] >= 5).astype(np.int8)

        df.drop(columns=['dayofweek'], inplace=True)

        return df

    def _apply_log_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies log1p to meter_reading to normalize skewed distributions."""
        self.logger.debug("Applying log1p transformation to target...")
        df['meter_reading'] = np.log1p(df['meter_reading']).astype(np.float32)
        return df