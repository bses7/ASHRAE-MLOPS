import time
from src.common.redis_client import RedisClient
from src.training.model import LGBMModel
from src.common.mlflow_tracker import MLflowTracker # Use the new file
from src.common.logger import get_logger

class TrainingStage:
    def __init__(self, config: dict):
        self.logger = get_logger("TrainingOrchestrator")
        self.config = config
        self.redis_client = RedisClient(config['redis'])
        self.model_wrapper = LGBMModel()
        self.tracker = MLflowTracker(config) # Initialize Tracker

    def run(self):
        self.logger.info("--- STARTING TRACKED TRAINING ---")

        # 1. Load Data
        X_train = self.redis_client.load_dataframe("X_train")
        X_test = self.redis_client.load_dataframe("X_test")
        y_train = self.redis_client.load_dataframe("y_train").iloc[:, 0]
        y_test = self.redis_client.load_dataframe("y_test").iloc[:, 0]

        if self.config['training']['use_sample']:
            size = self.config['training']['sample_size']
            X_train, y_train = X_train.iloc[:size], y_train.iloc[:size]

        # 2. Hyperparameters
        params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': 'rmse',
            'learning_rate': 0.3,
            'verbosity': -1
        }

        # 3. Tracked Execution
        with self.tracker.start_run(run_name="LGBM_Training_Run"):
            
            # Train
            start_time = time.time()
            self.model_wrapper.train(X_train, y_train, X_test, y_test, params)
            duration = time.time() - start_time

            # Evaluate
            y_pred = self.model_wrapper.predict(X_test)
            metrics = self.model_wrapper.evaluate(y_test, y_pred)
            metrics["training_duration"] = round(duration, 2)

            # --- USING THE SEPARATE MLFLOW FILE ---
            # Log Params & Metrics
            self.tracker.log_metadata(params=params, metrics=metrics)
            
            # Save and Log Artifact
            model_path = self.config['training']['model_save_path']
            self.model_wrapper.save_model(model_path)
            self.tracker.log_artifact(model_path)
            
            # Log Model to Registry
            self.tracker.log_model(self.model_wrapper.model, model_type="lightgbm")

            self.logger.info(f"Training Stage Complete. R2: {metrics['R2']}")

        return metrics

def run_training_stage(config: dict):
    stage = TrainingStage(config)
    return stage.run()