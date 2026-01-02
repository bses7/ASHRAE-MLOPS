from src.database.connection import DBClient
from src.database.db_reader import DatabaseReader
from src.validation.data_validator import DataValidator
from src.preprocessing.optimize import Optimizer
from src.common.logger import get_logger
from src.preprocessing.preprocessing import MLPreprocessor  
from src.preprocessing.feature_engineering import FeatureEngineer   
from src.common.redis_client import RedisClient
import gc
import pandas as pd
import joblib
import numpy as np
from src.schemas.raw_schemas import RAW_DATA_TYPES
from pathlib import Path

logger = get_logger("PreprocessingOrchestrator")

class PreprocessingStage:
    def __init__(self, config: dict):
        self.db_client = DBClient(config['db'])
        
        self.reader = DatabaseReader(self.db_client, config['db'])
        
        self.validator = DataValidator()
        self.transformer = Optimizer()
        self.ml_prep = MLPreprocessor() 
        self.redis_client = RedisClient(config['redis'])
        self.feature_eng = FeatureEngineer()
        self.config = config

    def run(self):
        logger.info("--- PREPROCESSING STAGE START ---")
        
        df_energy = self.reader.read_fact_table("fact_energy_usage")
        df_building = self.reader.read_dim_table("dim_building")
        df_weather = self.reader.read_dim_table("dim_weather")
        
        if not self.validator.validate_ingested_data(df_energy, df_building, df_weather):
            raise ValueError("Data Validation Failed. Check Great Expectations Data Docs.")

        df_joined = self.transformer.process(df_energy, df_building, df_weather)

        del df_energy, df_building, df_weather
        gc.collect()

        df_engineered = self.feature_eng.engineer(df_joined)

        del df_joined
        gc.collect()

        self._save_monitoring_reference(df_engineered)

        X, y = self.ml_prep.prepare_ml_features(df_engineered)

        del df_engineered
        gc.collect()    

        joblib.dump(self.ml_prep, "saved_models/preprocessor.joblib")

        # X_train, X_test, y_train, y_test = self.ml_prep.split_data(X, y)

        logger.info("Caching split data in Redis...")

        self.redis_client.store_dataframe(X, "ashrae_pipeline_X_train")
        self.redis_client.store_dataframe(pd.DataFrame(y, columns=['target']), "ashrae_pipeline_y_train")

        # self.redis_client.store_dataframe(X_test, "X_test")
        # self.redis_client.store_dataframe(pd.DataFrame(y_test, columns=['target']), "y_test")

        del X, y
        gc.collect()

        return
    
    def _save_monitoring_reference(self, df: pd.DataFrame):
        """Saves a clean sample for Evidently AI monitoring."""
        logger.info("Generating reference dataset for monitoring...")
        ref_path = self.config['monitoring']['reference_data_path']
        
        # 1. Select the columns we need for monitoring
        monitor_cols = list(RAW_DATA_TYPES["inference"].keys())
        available_cols = [c for c in monitor_cols if c in df.columns]
        
        # 2. Take a slightly larger sample than needed, then drop NaNs
        # This ensures the final 500 rows are 100% complete
        df_ref = df[available_cols].sample(n=min(len(df), 2000), random_state=42).copy()
        
        # Drop rows where critical features are still NaN (like year_built or cloud_coverage)
        df_ref.dropna(inplace=True)
        
        # Final trim to exactly the sample size you want
        sample_size = self.config['monitoring']['sample_size']
        df_ref = df_ref.head(sample_size)

        # 3. Inverse Log Transform
        if 'meter_reading' in df_ref.columns:
            df_ref['meter_reading'] = np.expm1(df_ref['meter_reading'].astype(np.float64)).astype(np.float32)

        try:
            df_ref.to_parquet(str(ref_path), index=False, engine="pyarrow")
            logger.info(f"Reference data (size: {len(df_ref)}) saved successfully to {ref_path}")
        except Exception as e:
            logger.error(f"Failed to save reference parquet: {e}")
            csv_fallback = str(ref_path).replace(".parquet", ".csv")
            df_ref.to_csv(csv_fallback, index=False)
            logger.warning(f"Saved fallback reference CSV to {csv_fallback}")

def run_preprocessing_stage(config: dict):
    stage = PreprocessingStage(config)
    return stage.run()