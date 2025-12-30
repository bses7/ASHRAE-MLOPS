import lightgbm as lgb
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, median_absolute_error
from src.training.base import BaseModel
from src.common.logger import get_logger

class LGBMModel(BaseModel):
    def __init__(self):
        self.logger = get_logger("LGBMModel")
        self.model = None

    def train(self, X_train, y_train, X_val, y_val, params):
        self.logger.info("Starting LightGBM Training...")
        
        lgb_train = lgb.Dataset(X_train, label=y_train)
        lgb_eval = lgb.Dataset(X_val, label=y_val, reference=lgb_train)

        self.model = lgb.train(
            params,
            lgb_train,
            num_boost_round=500,
            valid_sets=[lgb_train, lgb_eval],
            valid_names=['train', 'eval'],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=50)
            ]
        )
        return self.model

    def predict(self, X):
        return self.model.predict(X, num_iteration=self.model.best_iteration)

    def save_model(self, path: str):
        """Saves the model locally using joblib."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        self.logger.info(f"Model saved locally at: {path}")

    def evaluate(self, y_true, y_pred):
        """Calculates regression metrics for MLflow logging."""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        med_ae = median_absolute_error(y_true, y_pred)

        return {
            "RMSE": round(float(rmse), 4),
            "MSE": round(float(mse), 4),
            "MAE": round(float(mae), 4),
            "R2": round(float(r2), 4),
            "Median_AE": round(float(med_ae), 4)
        }