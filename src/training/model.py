import lightgbm as lgb
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, median_absolute_error
from src.training.base import BaseModel
from src.common.logger import get_logger

class LGBMModel(BaseModel):
    """
    LightGBM implementation optimized for K-Fold cross-validation.
    """
    def __init__(self):
        self.logger = get_logger("LGBMModel")
        self.model = None

    def train(self, X_train, y_train, X_val, y_val, params):
        """Trains a single fold."""
        lgb_train = lgb.Dataset(X_train, label=y_train)
        lgb_eval = lgb.Dataset(X_val, label=y_val, reference=lgb_train)

        model = lgb.train(
            params,
            lgb_train,
            num_boost_round=1000, 
            valid_sets=[lgb_train, lgb_eval],
            valid_names=['train', 'eval'],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=500)
            ]
        )
        return model

    def predict(self, model, X):
        """Predicts using a specific fold model."""
        return model.predict(X, num_iteration=model.best_iteration)

    def save_model(self, model, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)
        self.logger.info(f"Fold model saved locally at: {path}")

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