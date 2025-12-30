from src.database.connection import DBClient
from src.database.db_reader import DatabaseReader
from src.validation.data_validator import DataValidator
from src.preprocessing.optimize import Optimizer
from src.common.logger import get_logger
from src.preprocessing.preprocessing import MLPreprocessor   
from src.common.redis_client import RedisClient
import gc
import pandas as pd

logger = get_logger("PreprocessingOrchestrator")

class PreprocessingStage:
    def __init__(self, config: dict):
        # 1. Initialize the shared DBClient
        self.db_client = DBClient(config['db'])
        
        # 2. Pass DBClient and raw config to the Reader
        self.reader = DatabaseReader(self.db_client, config['db'])
        
        self.validator = DataValidator()
        self.transformer = Optimizer()
        self.ml_prep = MLPreprocessor() 
        self.redis_client = RedisClient(config['redis'])

    def run(self):
        logger.info("--- PREPROCESSING STAGE START ---")
        
        # Fetch data
        df_energy = self.reader.read_fact_table("fact_energy_usage")
        df_building = self.reader.read_dim_table("dim_building")
        df_weather = self.reader.read_dim_table("dim_weather")
        
        # Validate
        if not self.validator.validate_ingested_data(df_energy, df_building, df_weather):
            raise ValueError("Data Validation Failed. Check Great Expectations Data Docs.")

        # Preprocess
        df_joined = self.transformer.process(df_energy, df_building, df_weather)

        del df_energy, df_building, df_weather
        gc.collect()

        X, y = self.ml_prep.prepare_ml_features(df_joined)

        X_train, X_test, y_train, y_test = self.ml_prep.split_data(X, y)

        logger.info("Caching split data in Redis...")

        self.redis_client.store_dataframe(X_train, "X_train")
        self.redis_client.store_dataframe(pd.DataFrame(y_train, columns=['target']), "y_train")

        self.redis_client.store_dataframe(X_test, "X_test")
        self.redis_client.store_dataframe(pd.DataFrame(y_test, columns=['target']), "y_test")

        return X_train, X_test, y_train, y_test

def run_preprocessing_stage(config: dict):
    stage = PreprocessingStage(config)
    return stage.run()