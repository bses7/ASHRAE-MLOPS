import pandas as pd
import numpy as np
import re
from datetime import datetime
from src.common.logger import get_logger

class DataTransformer:
    """
    Transformation part of ETL.
    1. lowercase snake_case.
    2. lineage metadata timestamp
    3. weather data transformations
    """

    def __init__(self):
        self.logger = get_logger("DataTransformer")

    def transform(self, df: pd.DataFrame, entity_name: str) -> pd.DataFrame:
        """
        global cleaning and metadata to chunks.
        """
        if df is None or df.empty:
            return df

        df = self._standardize_column_names(df)

        df = self._add_lineage_metadata(df)

        if entity_name == "weather":
            return self._transform_weather_data(df)
        elif entity_name == "train":
            return self._transform_train_data(df)
        elif entity_name == "building":
            return self._transform_building_data(df)
        
        return df

    def _add_lineage_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """timestamp of when the data was processed by the pipeline"""
        df['ingested_at'] = datetime.now()
        return df

    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """lowercase snake_case column names"""
        original_cols = df.columns.tolist()
        clean_cols = [
            re.sub(r'[\s\-]+', '_', col.lower().strip()) 
            for col in original_cols
        ]
        df.columns = clean_cols
        return df

    def _transform_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """site-day-month mean imputation for weather"""
        self.logger.info("Transforming weather data: Imputing missing values...")

        df["datetime"] = pd.to_datetime(df["timestamp"])
        df["day"] = df["datetime"].dt.day
        df["month"] = df["datetime"].dt.month
        df["week"] = df["datetime"].dt.isocalendar().week.astype("int16")

        df = df.set_index(['site_id', 'day', 'month'])

        columns_to_impute = [
            'air_temperature', 'cloud_coverage', 'dew_temperature',
            'precip_depth_1_hr', 'sea_level_pressure', 
            'wind_direction', 'wind_speed'
        ]
        needs_ffill = ['cloud_coverage', 'sea_level_pressure', 'precip_depth_1_hr']

        for col in columns_to_impute:
            if col not in df.columns: continue
                
            group_filler = df.groupby(['site_id', 'day', 'month'])[col].mean()
            if col in needs_ffill:
                group_filler = group_filler.ffill()

            filler_df = pd.DataFrame(group_filler, columns=[col])
            df.update(filler_df, overwrite=False)

        return df.reset_index()

    def _transform_train_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """energy data transformation"""
        return df

    def _transform_building_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """building data transformation"""
        return df