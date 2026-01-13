import mlflow
import pandas as pd
import numpy as np
from src.common.redis_client import RedisClient
from src.common.mlflow_tracker import MLflowTracker
from src.evaluation.explainer import LimeExplainer
from src.common.logger import get_logger

class EvaluationStage:
    def __init__(self, config: dict):
        self.logger = get_logger("EvaluationOrchestrator")
        self.config = config
        self.redis_client = RedisClient(config['redis'])
        self.tracker = MLflowTracker(config)

    def run(self):
        self.logger.info("--- STARTING MODEL EVALUATION & XAI STAGE ---")

        X_test = self.redis_client.load_dataframe("ashrae_pipeline_X_train").iloc[:1000] 
        
        mlflow.set_tracking_uri(self.config['mlflow']['tracking_uri'])
        model_uri = f"models:/{self.config['mlflow']['model_name']}/latest"
        model = mlflow.lightgbm.load_model(model_uri)

        explainer = LimeExplainer(training_data=X_test.head(500), feature_names=X_test.columns.tolist())

        sample_row = X_test.head(1)
        
        with self.tracker.start_run(run_name="Model_Explainability_LIME"):
            html_path = explainer.explain_prediction(model, sample_row, "sample_prediction")
            
            self.tracker.log_artifact(html_path)
            self.logger.info("LIME explanation logged to MLflow artifacts.")

        self.logger.info("--- EVALUATION STAGE COMPLETE ---")

def run_evaluation_stage(config: dict):
    stage = EvaluationStage(config)
    stage.run()