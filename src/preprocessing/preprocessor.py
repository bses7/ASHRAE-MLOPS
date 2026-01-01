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

def run_preprocessing_stage(config: dict):
    stage = PreprocessingStage(config)
    return stage.run()