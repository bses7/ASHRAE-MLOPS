import pandas as pd
import logging
from sqlalchemy import text
from src.database.connection import DBClient
from src.schemas.raw_schemas import RAW_DATA_TYPES

class InferenceLogger:
    """
    Handles logging of real-time API inferences to MariaDB.
    Automatically creates the logging table based on the unified schema.
    """

    TYPE_MAP = {
        "int8": "TINYINT",
        "int32": "INT",
        "float32": "FLOAT",
        "category": "VARCHAR(255)"
    }

    def __init__(self, db_client: DBClient):
        self.engine = db_client.get_engine()
        self.table_name = "inference_logs"
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Creates the inference_logs table if it does not exist using raw_schemas."""
        schema = RAW_DATA_TYPES["inference"]
        column_defs = []
        
        for col, dtype in schema.items():
            sql_type = self.TYPE_MAP.get(str(dtype), "VARCHAR(255)")
            column_defs.append(f"`{col}` {sql_type}")
        
        # Add an automatic timestamp for lineage
        column_defs.append("`logged_at` DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        create_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {', '.join(column_defs)}
        ) ENGINE=InnoDB;
        """
        
        with self.engine.begin() as conn:
            conn.execute(text(create_query))

    def log_inference(self, input_data: dict, prediction: float):
        """
        Saves a single inference event to the database.
        """
        try:
            log_entry = {**input_data, "meter_reading": prediction}
            df = pd.DataFrame([log_entry])
            
            schema = RAW_DATA_TYPES["inference"]
            for col, dtype in schema.items():
                if col in df.columns:
                    target_type = "object" if dtype == "category" else dtype
                    df[col] = df[col].astype(target_type)

            with self.engine.begin() as conn:
                df.to_sql(
                    name=self.table_name,
                    con=conn,
                    if_exists="append",
                    index=False
                )
        except Exception as e:
            logging.error(f"Failed to log inference: {e}")