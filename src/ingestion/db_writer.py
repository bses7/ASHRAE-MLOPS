import pandas as pd
import logging
import os
from sqlalchemy import text
from src.database.connection import DBClient
from src.ingestion.base import BaseWriter

class StagingWriter(BaseWriter):
    def __init__(self, db_client: DBClient):
        self.engine = db_client.get_engine()
        self.logger = logging.getLogger("StagingWriter")

    def bulk_load_csv(self, file_path: str, table_name: str, columns: list):
        """High-performance bulk load for ColumnStore via LOAD DATA LOCAL INFILE."""
        abs_path = os.path.abspath(file_path)
        col_list = ", ".join([f"`{c}`" for c in columns])
        
        load_query = text(f"""
            LOAD DATA LOCAL INFILE '{abs_path}'
            INTO TABLE `{table_name}`
            FIELDS TERMINATED BY ',' 
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            ({col_list});
        """)
        
        self.logger.info(f"Executing Bulk Load for {table_name}...")
        with self.engine.connect() as conn:
            # ColumnStore works best with autocommit for bulk loads
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(load_query)

    def truncate_table(self, table_name: str) -> None:
        """Truncates table. If table doesn't exist, ignore the error."""
        self.logger.info(f"Clearing table {table_name}")
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"TRUNCATE TABLE `{table_name}`;"))
                conn.commit()
        except Exception as e:
            if "1146" in str(e): # Table doesn't exist error code
                self.logger.warning(f"Table {table_name} does not exist. Skipping truncate.")
            else:
                raise

    def write_chunk(self, df: pd.DataFrame, table_name: str) -> None:
        """Standard insert for dimension tables."""
        with self.engine.connect() as conn:
            df.to_sql(
                name=table_name,
                con=conn,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=5000 
            )