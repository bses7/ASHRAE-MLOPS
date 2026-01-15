import joblib
import mlflow
import os
import pandas as pd
import numpy as np
import requests
import time
from typing import Dict, Any
from src.common.config_loader import load_yaml_config
from src.preprocessing.preprocessing import MLPreprocessor
from src.monitoring.collector import InferenceLogger
from src.database.connection import DBClient
from src.preprocessing.feature_engineering import FeatureEngineer

class ModelService:
    _instance = None
    _model_cache: Dict[str, Any] = {} 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config = load_yaml_config("configs/pipeline_config.yaml")
        self.model_name = self.config['mlflow']['model_name']
        self.tracking_uri = self.config['mlflow']['tracking_uri']
        self.local_model_path = self.config['training']['model_save_path']
        prep_path = "saved_models/preprocessor.joblib"

        self._preprocessor = joblib.load(prep_path) if os.path.exists(prep_path) else MLPreprocessor()
        self._feature_eng = FeatureEngineer()

        try:
            db_client = DBClient(self.config['db'])
            self.inference_logger = InferenceLogger(db_client)
        except Exception as e:
            self.inference_logger = None
            print(f"--- Warning: DB Logging Offline: {e} ---")
        
        mlflow.set_tracking_uri(self.tracking_uri)

    def _get_model(self, version: str = "latest"):
        """
        PRIORITY LOGIC:
        1. Internal RAM Cache
        2. MLflow Registry (Remote)
        3. Local .pkl file (Fallback)
        """
        if version in self._model_cache:
            return self._model_cache[version]

        try:
            requests.get(self.tracking_uri, timeout=2)
            
            model_version_tag = "latest" if version == "latest" else version
            model_uri = f"models:/{self.model_name}/{model_version_tag}"
            
            print(f"--- [PRIORITY] Fetching model from MLflow: {model_uri} ---")
            model = mlflow.lightgbm.load_model(model_uri)
            
            self._model_cache[version] = model
            return model

        except Exception as e:
            print(f"--- MLflow unavailable or version not found ({e}). Trying Local fallback... ---")

        if os.path.exists(self.local_model_path):
            print(f"--- [FALLBACK] Loading model from local disk: {self.local_model_path} ---")
            model = joblib.load(self.local_model_path)
            self._model_cache[version] = model
            return model
        
        raise FileNotFoundError(f"Critical: Model version {version} not found in MLflow or at {self.local_model_path}")

    def predict(self, input_data: dict, version: str = "latest") -> float:
        model = self._get_model(version)

        used_version = version 

        input_data.pop('model_version', None)
        df = pd.DataFrame([input_data])

        if 'hour' in input_data:
            df['timestamp'] = pd.to_datetime(f"2025-{input_data['month']}-{input_data['day']} {input_data['hour']}:00:00")
            df = self._feature_eng.engineer(df)

        df_processed = self._preprocessor.prepare_inference_features(df)

        log_prediction = model.predict(df_processed)
        final_prediction = float(np.expm1(log_prediction[0]))
        final_prediction = max(0, final_prediction)

        if self.inference_logger:
            input_data['meter_reading'] = final_prediction
            if 'is_weekend' in df.columns:
                input_data['is_weekend'] = int(df['is_weekend'].iloc[0])
            self.inference_logger.log_inference(input_data, final_prediction, version=used_version)

        return final_prediction

    def get_detailed_metadata(self) -> dict:
        """API metadata endpoint logic."""
        try:
            client = mlflow.tracking.MlflowClient()
            versions = client.search_model_versions(f"name='{self.model_name}'")
            
            version_list = []
            for v in versions:
                try:
                    run = client.get_run(v.run_id)
                    version_list.append({
                        "version": v.version,
                        "stage": v.current_stage,
                        "rmse": f"{run.data.metrics.get('avg_rmse', 0):.2f} kWh",
                        "accuracy": f"{(run.data.metrics.get('avg_r2', 0) * 100):.1f}%",
                        "last_updated": v.last_updated_timestamp
                    })
                except: continue

            return {"status": "online", "versions": version_list}
        except Exception as e:
            return {"status": "offline", "error": str(e)}