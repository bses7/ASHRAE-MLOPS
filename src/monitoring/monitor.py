import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
from evidently import ColumnMapping
from src.database.connection import DBClient
from src.common.logger import get_logger
from pathlib import Path

class ModelMonitor:
    def __init__(self, config: dict):
        self.logger = get_logger("ModelMonitor")
        self.config = config
        self.db_client = DBClient(config['db'])
        self.ref_path = Path(config['monitoring']['reference_data_path'])

        self.report_dir = Path("src/monitoring/reports")
        self.report_dir.mkdir(parents=True, exist_ok=True)

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
            reference_df = self._load_reference_data()
            query = "SELECT * FROM inference_logs ORDER BY logged_at DESC LIMIT 5000"
            current_df = pd.read_sql(query, con=self.db_client.get_engine())

            if current_df.empty:
                return "<html><body><h1>No data collected yet.</h1></body></html>"

            for df in [reference_df, current_df]:
                cols_to_drop = ['id', 'logged_at', 'timestamp', 'datetime', 'ingested_at']
                df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
                
                cat_cols = ['primary_use', 'is_weekend', 'meter', 'site_id', 'week', 'month', 'day', 'hour']
                for col in cat_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(str)

                num_cols = df.select_dtypes(include=[np.number]).columns
                df[num_cols] = df[num_cols].astype(float)

            column_mapping = ColumnMapping()
            
            column_mapping.id = 'building_id'        
            column_mapping.target = 'meter_reading'    
            column_mapping.prediction = 'meter_reading' 
            
            column_mapping.numerical_features = [
                'air_temperature', 'cloud_coverage', 'dew_temperature', 
                'precip_depth_1_hr', 'sea_level_pressure', 'wind_direction', 
                'wind_speed', 'square_feet'
            ]

         
            column_mapping.categorical_features = [
                'primary_use', 'is_weekend', 'meter', 'site_id', 'week', 'month', 'day'
            ]

            report = Report(metrics=[
                DataQualityPreset(),
                DataDriftPreset(),
                TargetDriftPreset()
            ])

            self.logger.info("Running drift analysis with categorical-focused mapping...")
            report.run(
                reference_data=reference_df, 
                current_data=current_df,
                column_mapping=column_mapping 
            )

            report_path = self.report_dir / "latest_monitoring_report.html"
            report.save_html(str(report_path))
            
            return report.get_html()

        except Exception as e:
            self.logger.error(f"Failed to generate monitoring report: {e}", exc_info=True)
            return f"<html><body><h1>Monitoring Error</h1><p>{str(e)}</p></body></html>"