import lime
import lime.lime_tabular
import pandas as pd
import numpy as np
from pathlib import Path
from src.common.logger import get_logger

class LimeExplainer:
    def __init__(self, training_data: pd.DataFrame, feature_names: list):
        self.logger = get_logger("LimeExplainer")
        self.feature_names = feature_names
        
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=training_data.values,
            feature_names=self.feature_names,
            class_names=['meter_reading'],
            mode='regression',
            verbose=False
        )

    def explain_prediction(self, model, data_row: pd.DataFrame, report_name: str):
        """
        Explains a single prediction and saves it as an HTML artifact.
        """
        self.logger.info(f"Generating LIME explanation for {report_name}...")
        
        instance = data_row.values[0]

        predict_fn = lambda x: model.predict(x)

        exp = self.explainer.explain_instance(
            instance, 
            predict_fn, 
            num_features=10
        )

        report_path = Path(f"reports/evaluation/lime_{report_name}.html")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        exp.save_to_file(str(report_path))
        
        return str(report_path)