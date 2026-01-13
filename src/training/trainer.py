import time
import numpy as np
from src.common.redis_client import RedisClient
from src.training.model import LGBMModel
from sklearn.model_selection import StratifiedKFold
from src.common.mlflow_tracker import MLflowTracker 
from src.common.logger import get_logger

class TrainingStage:
    def __init__(self, config: dict):
        self.logger = get_logger("TrainingOrchestrator")
        self.config = config
        self.redis_client = RedisClient(config['redis'])
        self.model_wrapper = LGBMModel()
        self.tracker = MLflowTracker(config) 

    def run(self):
        self.logger.info("--- STARTING TRACKED TRAINING ---")

        X = self.redis_client.load_dataframe("ashrae_pipeline_X_train")
        y = self.redis_client.load_dataframe("ashrae_pipeline_y_train").iloc[:, 0]

        if self.config['training']['use_sample']:
            size = self.config['training']['sample_size']
            X, y = X.iloc[:size], y.iloc[:size]

        print("TRAINING SIZE", X.shape)

        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

        strat_target = X['building_id']

        params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': 'rmse',
            'learning_rate': 0.3,
            'verbosity': -1
        }

        all_fold_metrics = []

        with self.tracker.start_run(run_name="ASHRAE_KFold_Training"):
            self.tracker.log_metadata(params=params, metrics={})

            for fold, (train_idx, val_idx) in enumerate(skf.split(X, strat_target), 1):
                self.logger.info(f"--- Processing Fold {fold} ---")
                
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

                fold_model = self.model_wrapper.train(X_train, y_train, X_val, y_val, params)

                y_pred = self.model_wrapper.predict(fold_model, X_val)
                metrics = self.model_wrapper.evaluate(y_val, y_pred)
                
                fold_logged_metrics = {f"F{fold}_{k}": v for k, v in metrics.items()}
                self.tracker.log_metadata(params={}, metrics=fold_logged_metrics)
                
                all_fold_metrics.append(metrics)
                self.logger.info(f"Fold {fold} RMSE: {metrics['RMSE']} | R2: {metrics['R2']}")

            avg_metrics = {
                "avg_rmse": np.mean([m['RMSE'] for m in all_fold_metrics]),
                "avg_mae": np.mean([m['MAE'] for m in all_fold_metrics]),
                "avg_r2": np.mean([m['R2'] for m in all_fold_metrics])
            }
            
            self.tracker.log_metadata(params={}, metrics=avg_metrics)
            
            model_path = self.config['training']['model_save_path']
            self.model_wrapper.save_model(fold_model, model_path)
            self.tracker.log_artifact(model_path)

            input_example = X_train.head(5)
            self.tracker.log_model(
                fold_model,
                model_type="lightgbm",
                input_example=input_example
            )

            self.logger.info(f"CV Training Complete. Average RMSE: {avg_metrics['avg_rmse']:.4f}")

        return avg_metrics


def run_training_stage(config: dict):
    stage = TrainingStage(config)
    return stage.run()