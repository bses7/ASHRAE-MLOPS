import joblib
import mlflow
import os
import pandas as pd
import requests 
import numpy as np
from src.common.config_loader import load_yaml_config
from src.preprocessing.preprocessing import MLPreprocessor
from src.monitoring.collector import InferenceLogger
from src.database.connection import DBClient

class ModelService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config = load_yaml_config("configs/pipeline_config.yaml")
        model_path = self.config['training']['model_save_path']
        prep_path = "saved_models/preprocessor.joblib"

        if os.path.exists(prep_path):
            self._preprocessor = joblib.load(prep_path)
            print(f"--- Preprocessor loaded from {prep_path} ---")
        else:
            self._preprocessor = MLPreprocessor()

        self.inference_logger = None
        try:
            db_client = DBClient(self.config['db'])
            self.inference_logger = InferenceLogger(db_client)
            print("--- Inference Logger initialized and connected to MariaDB ---")
        except Exception as e:
            print(f"--- WARNING: Inference Logger failed to initialize: {e} ---")
            print("--- Service will continue without database logging ---")
        
        tracking_uri = self.config['mlflow']['tracking_uri']
        mlflow.set_tracking_uri(tracking_uri)
        
        os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = "5" 

        model_loaded = False

        try:
            print(f"Checking MLflow connection at {tracking_uri}...")
            requests.get(tracking_uri, timeout=2) 
            
            model_uri = f"models:/{self.config['mlflow']['model_name']}/latest"
            self._model = mlflow.lightgbm.load_model(model_uri)
            print(f"--- Model loaded from MLflow Registry ---")
            model_loaded = True
        except Exception as e:
            print(f"--- MLflow unreachable or error: {e} ---")

        if not model_loaded:
            print(f"--- Attempting local fallback: {model_path} ---")
            if os.path.exists(model_path):
                self._model = joblib.load(model_path)
                print(f"--- Model loaded from local path success ---")
            else:
                raise FileNotFoundError(f"Critical Error: No model found at {model_path} or MLflow.")

    def predict(self, input_data: dict) -> float:
        df = pd.DataFrame([input_data])

        print("The dataframe", df.columns)

        # df['primary_use'] = df['primary_use'].astype('category') 
        df = df.drop(columns=['hour'], inplace=False) 

        df_processed = self._preprocessor.prepare_inference_features(df)

    #    ## Needs Changing

    #     print("Model expected features:", self._model.feature_name())
    #     print("DataFrame actual features:", df_processed.columns.tolist())

        print("Processed Dataframe:", df_processed)

        log_prediction = self._model.predict(df_processed)

        final_prediction = float(np.expm1(log_prediction[0]))
        final_prediction = max(0, final_prediction)

        input_data['meter_reading'] = final_prediction
        
        if self.inference_logger is not None:
            try:
                input_data['meter_reading'] = final_prediction
                self.inference_logger.log_inference(input_data, final_prediction)
            except Exception as e:
                print(f"--- Error during runtime logging: {e} ---")
        else:
            pass

        return final_prediction
    
    def get_model_metadata(self) -> dict:
        """Fetches metadata from MLflow, falls back gracefully if unreachable"""
        try:
            tracking_uri = self.config['mlflow']['tracking_uri']
            requests.get(tracking_uri, timeout=2)
            
            client = mlflow.tracking.MlflowClient(tracking_uri=tracking_uri)
            model_name = self.config['mlflow']['model_name']
            
            latest_versions = client.get_latest_versions(model_name, stages=["None", "Staging", "Production"])
            
            if not latest_versions:
                return {"status": "offline", "reason": "No registered versions found"}

            latest = latest_versions[0]
            run = client.get_run(latest.run_id)
            metrics = run.data.metrics

            return {
                "status": "online",
                "version": f"v{latest.version}",
                "rmse": f"{metrics.get('rmse', 0):.2f} kWh",
                "accuracy": f"{(metrics.get('accuracy', 1) * 100):.1f}%", 
                "last_updated": latest.last_updated_timestamp,
            }
        except Exception as e:
            print(f"--- Metadata fetch failed: {e} ---")
            return {"status": "offline"}