import joblib
import mlflow
import os
import pandas as pd
import numpy as np
from src.common.config_loader import load_yaml_config
from src.preprocessing.preprocessing import MLPreprocessor

class ModelService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        config = load_yaml_config("configs/pipeline_config.yaml")
        model_path = config['training']['model_save_path']
        prep_path = "saved_models/preprocessor.joblib"

        if os.path.exists(prep_path):
            self._preprocessor = joblib.load(prep_path)
            print(f"--- Preprocessor loaded from {prep_path} ---")
        else:
            self._preprocessor = MLPreprocessor()
        
        try:
            mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
            model_uri = f"models:/{config['mlflow']['model_name']}/latest"
            self._model = mlflow.lightgbm.load_model(model_uri)
            print(f"--- Model loaded from MLflow Registry: {model_uri} ---")
        except Exception as e:
            print(f"MLflow load failed, falling back to local path: {e}")
            self._model = joblib.load(model_path)
            print(f"--- Model loaded from local path: {model_path} ---")

    def predict(self, input_data: dict) -> float:
        df = pd.DataFrame([input_data])

        print("The dataframe", df.columns)

        # df['primary_use'] = df['primary_use'].astype('category') 
        df = df.drop(columns=['hour'], inplace=False) 

        df_processed = self._preprocessor.prepare_inference_features(df)

       ## Needs Changing

        print("Model expected features:", self._model.feature_name())
        print("DataFrame actual features:", df_processed.columns.tolist())

        print("Processed Dataframe:", df_processed)

        log_prediction = self._model.predict(df_processed)

        final_prediction = np.expm1(log_prediction[0])

        return float(max(0, final_prediction))