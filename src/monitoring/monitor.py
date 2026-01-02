import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
from src.database.connection import DBClient
from src.common.logger import get_logger
from pathlib import Path

class ModelMonitor:
    def __init__(self, config: dict):
        self.logger = get_logger("ModelMonitor")
        self.config = config
        self.db_client = DBClient(config['db'])
        self.ref_path = Path(config['monitoring']['reference_data_path'])

    def _load_reference_data(self) -> pd.DataFrame:
        """Loads reference data from Parquet or CSV."""
        if self.ref_path.exists() and self.ref_path.suffix == '.parquet':
            return pd.read_parquet(self.ref_path)
        
        csv_path = self.ref_path.with_suffix('.csv')
        if csv_path.exists():
            return pd.read_csv(csv_path)
        
        raise FileNotFoundError(f"Reference data not found at {self.ref_path}")

    def generate_html_report(self) -> str:
        self.logger.info("Generating Model Health Report...")

        try:
            # 1. Load Data
            reference_df = self._load_reference_data()
            query = "SELECT * FROM inference_logs ORDER BY logged_at DESC LIMIT 5000"
            current_df = pd.read_sql(query, con=self.db_client.get_engine())

            if current_df.empty:
                return "<html><body><h1>No data collected yet.</h1></body></html>"

            # 2. Alignment & Data Cleaning
            # We must make the types IDENTICAL and remove metadata
            for df in [reference_df, current_df]:
                # Drop non-feature/ID columns
                cols_to_drop = ['id', 'logged_at', 'timestamp', 'datetime', 'ingested_at']
                df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
                
                # FIX: Convert categories to strings. 
                # Evidently handles strings as categorical data automatically.
                if 'primary_use' in df.columns:
                    df['primary_use'] = df['primary_use'].astype(str)

                # Ensure all numeric data is float64 to avoid type mismatches
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = df[numeric_cols].astype(float)

            # 3. Setup Report
            report = Report(metrics=[
                DataQualityPreset(),
                DataDriftPreset(),
                TargetDriftPreset()
            ])

            # 4. Run Analysis
            self.logger.info(f"Comparing {len(reference_df)} reference vs {len(current_df)} current samples")
            
            # Use 'column_mapping=None' to let Evidently infer types from strings/floats
            report.run(reference_data=reference_df, current_data=current_df)
            
            return report.get_html()

        except Exception as e:
            self.logger.error(f"Failed to generate monitoring report: {e}", exc_info=True)
            return f"<html><body><h1>Monitoring Error</h1><p>{str(e)}</p></body></html>"