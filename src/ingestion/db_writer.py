import pandas as pd
import logging
from sqlalchemy import text
from src.database.connection import DBClient
from src.ingestion.base import BaseWriter

class StagingWriter(BaseWriter):
    """Appends data into existing ColumnStore tables."""

    def __init__(self, db_client: DBClient):
        self.engine = db_client.get_engine()
        self.logger = logging.getLogger(__name__)

    def truncate_table(self, table_name: str) -> None:
        """Clears the table for idempotency."""
        self.logger.info(f"Truncating table {table_name}...")
        with self.engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE `ashrae_db`.`{table_name}`"))

    def write_chunk(self, df: pd.DataFrame, table_name: str, is_first_chunk: bool = False) -> None:
        """
        Appends a chunk to the table.
        is_first_chunk is no longer needed for 'replace' since we use truncate.
        """
        try:
            with self.engine.connect() as conn:
                df.to_sql(
                    name=table_name,
                    con=conn,
                    schema='ashrae_db',
                    if_exists='append', 
                    index=False,
                    method='multi',
                    chunksize=100000 
                )
        except Exception as e:
            self.logger.error(f"Error loading data into {table_name}: {e}")
            raise