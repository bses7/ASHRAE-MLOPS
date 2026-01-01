import pandas as pd
import numpy as np
import re
from src.common.logger import get_logger

class DataTransformer:
    def __init__(self):
        self.logger = get_logger("DataTransformer")

    def transform(self, df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        # Only lowercase/snake_case naming
        df = self._standardize_column_names(df)

        if entity_name == "weather":
            return self._transform_weather_data(df)
        elif entity_name == "building":
            return self._transform_building_data(df)
        
        return df

    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [re.sub(r'[\s\-]+', '_', col.lower().strip()) for col in df.columns]
        return df

    def _transform_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Implements specific imputation rules for weather data:
        - Mean: temperature, dew, wind_direction, wind_speed
        - Mean + Forward Fill: cloud_coverage, sea_level, precipitation
        """
        self.logger.info("Transforming weather data: Using column-specific imputation...")

        df["datetime"] = pd.to_datetime(df["timestamp"])
        df["day"] = df["datetime"].dt.day
        df["month"] = df["datetime"].dt.month
        df["week"] = df["datetime"].dt.isocalendar().week.astype("int16")

        df = df.set_index(['site_id', 'day', 'month'])

        mean_cols = ['air_temperature', 'dew_temperature', 'wind_direction', 'wind_speed']
        for col in mean_cols:
            if col in df.columns:
                filler = df.groupby(['site_id', 'day', 'month'])[col].mean().to_frame(col)
                df.update(filler, overwrite=False)

        ffill_cols = ['cloud_coverage', 'sea_level_pressure', 'precip_depth_1_hr']
        for col in ffill_cols:
            if col in df.columns:
                filler = df.groupby(['site_id', 'day', 'month'])[col].mean().ffill().to_frame(col)
                df.update(filler, overwrite=False)

        self.logger.info("Weather imputation complete.")
        return df.reset_index()

    def _transform_building_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'floor_count' in df.columns:
            df = df.drop(columns=['floor_count'])
        if 'year_built' in df.columns:
            df['year_built'] = df['year_built'].fillna(-999).astype(np.int16)
        return df