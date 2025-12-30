import joblib
import mlflow
import os
import pandas as pd
from src.common.config_loader import load_yaml_config

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
        
        # Priority 1: Load from MLflow Registry
        try:
            mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
            model_uri = f"models:/{config['mlflow']['model_name']}/latest"
            self._model = mlflow.lightgbm.load_model(model_uri)
            print(f"--- Model loaded from MLflow Registry: {model_uri} ---")
        except Exception as e:
            # Priority 2: Fallback to local .pkl
            print(f"MLflow load failed, falling back to local path: {e}")
            self._model = joblib.load(model_path)
            print(f"--- Model loaded from local path: {model_path} ---")

    def predict(self, input_data: dict) -> float:
        # Convert dictionary to DataFrame (as model expects 2D input)
        df = pd.DataFrame([input_data])
        
        # Note: If your model requires specific encoding (LabelEncoding), 
        # it should be handled here or inside the saved model pipeline.
        prediction = self._model.predict(df)
        return float(prediction[0])