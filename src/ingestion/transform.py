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
        df["datetime"] = pd.to_datetime(df["timestamp"])
        df["day"] = df["datetime"].dt.day
        df["month"] = df["datetime"].dt.month
        df["week"] = df["datetime"].dt.isocalendar().week.astype("int16")

        df = df.set_index(['site_id', 'day', 'month'])
        columns_to_impute = ['air_temperature', 'cloud_coverage', 'dew_temperature',
                             'precip_depth_1_hr', 'sea_level_pressure', 
                             'wind_direction', 'wind_speed']

        for col in columns_to_impute:
            if col not in df.columns: continue
            # Efficient transform-based imputation
            df[col] = df[col].fillna(df.groupby(['site_id', 'day', 'month'])[col].transform('mean'))

        return df.reset_index()

    def _transform_building_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Match schema: drop floor_count, fill year_built
        if 'floor_count' in df.columns:
            df = df.drop(columns=['floor_count'])
        if 'year_built' in df.columns:
            df['year_built'] = df['year_built'].fillna(-999).astype(np.int16)
        return df