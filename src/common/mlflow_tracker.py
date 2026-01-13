import mlflow
import mlflow.lightgbm
import pandas as pd
from typing import Dict, Any, Optional
from src.common.logger import get_logger
from mlflow.models import infer_signature

class MLflowTracker:
    """
    MLflow experiment tracking.
    """
    def __init__(self, config: Dict[str, Any]):
        self.logger = get_logger("MLflowTracker")
        self.cfg = config['mlflow']
        
        mlflow.set_tracking_uri(self.cfg['tracking_uri'])
        mlflow.set_experiment(self.cfg['experiment_name'])
        
    def start_run(self, run_name: Optional[str] = None):
        """Starts a new MLflow run."""
        return mlflow.start_run(run_name=run_name)

    def log_metadata(self, params: Dict[str, Any], metrics: Dict[str, Any]):
        """Logs multiple parameters and metrics at once."""
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        self.logger.info("Metadata logged to MLflow.")

    def log_model(self, model: Any, model_type: str = "lightgbm", input_example=None):
        """Logs the model to the MLflow Registry."""
        if model_type == "lightgbm":
            signature = None
            if input_example is not None:
                signature = infer_signature(input_example, model.predict(input_example))

            mlflow.lightgbm.log_model(
                lgb_model=model,
                artifact_path="model",
                registered_model_name=self.cfg['model_name'],
                input_example=input_example,
                signature=signature
            )

        self.logger.info(
            f"Model logged to MLflow Registry as '{self.cfg['model_name']}'"
        )

    def log_artifact(self, local_path: str):
        """Uploads a local file (like model.pkl) to MLflow."""
        mlflow.log_artifact(local_path)
        self.logger.info(f"Artifact {local_path} uploaded to MLflow.")