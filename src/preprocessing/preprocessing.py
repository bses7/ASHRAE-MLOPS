import pandas as pd
import numpy as np
import gc

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.common.logger import get_logger


class MLPreprocessor:

    def __init__(self, target_column: str = "meter_reading"):
        self.logger = get_logger("MLPreprocessor")
        self.target_column = target_column

        self.scaler_map = {}          
        self.category_maps = {}      

        self.categorical_cols = []
        self.numeric_scaled_cols = []
        self.feature_columns_ = None

        # Constants
        self.exclude_numeric_cols = {'site_id', 'building_id', 'meter'}
        self.drop_cols = {'timestamp', 'datetime', 'year_built'}

    def prepare_ml_features(self, df: pd.DataFrame):
        """
        Fits encoders/scalers and captures column metadata.
        """
        self.logger.info("Starting Training Feature Engineering (In-Place)")

        y = df[self.target_column].values.astype('float32')
        df.drop(columns=[self.target_column], inplace=True)

        for col in self.drop_cols:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
        gc.collect()

        self.categorical_cols = df.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()

        for col in self.categorical_cols:
            self.logger.info(f"Encoding categorical: {col}")

            codes, uniques = pd.factorize(df[col], sort=True)
            df[col] = codes.astype('int16')

            self.category_maps[col] = {val: i for i, val in enumerate(uniques)}
            gc.collect()

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        for col in numeric_cols:
            if col in self.categorical_cols:
                continue
            if col in self.exclude_numeric_cols:
                continue

            self.logger.info(f"Scaling numeric: {col}")

            scaler = StandardScaler()
            df[col] = scaler.fit_transform(
                df[[col]].values.astype('float32')
            ).astype('float32')

            self.scaler_map[col] = scaler
            self.numeric_scaled_cols.append(col)
            gc.collect()

        self.feature_columns_ = df.columns.tolist()

        self.logger.info(
            f"Training features ready. Total features: {len(self.feature_columns_)}"
        )

        return df, y


    def prepare_inference_features(self, df: pd.DataFrame):
        """
        Used during INFERENCE.
        Applies PRE-FITTED encoders/scalers.
        """
        if self.feature_columns_ is None:
            raise RuntimeError("Preprocessor has not been fitted.")

        self.logger.info("Starting Inference Feature Engineering")

        drop_cols = self.drop_cols | {self.target_column}
        for col in drop_cols:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)

        for col in self.categorical_cols:
            if col in df.columns:
                mapping = self.category_maps[col]
                df[col] = (
                    df[col]
                    .astype(str)
                    .map(mapping)
                    .fillna(-1)
                    .astype('int16')
                )
            else:
                df[col] = -1

        for col in self.numeric_scaled_cols:
            if col in df.columns:
                scaler = self.scaler_map[col]
                df[col] = scaler.transform(
                    df[[col]].values.astype('float32')
                ).astype('float32')
            else:
                df[col] = 0.0

        df = df.reindex(columns=self.feature_columns_, fill_value=0)

        self.logger.info("Inference preprocessing completed successfully")
        return df