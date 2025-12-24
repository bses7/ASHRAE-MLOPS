import pandas as pd
import logging
from src.database.connection import DBClient
from src.ingestion.base import BaseWriter

class StagingWriter(BaseWriter):
    """Direct-to-Database writer using standard Pandas to_sql logic."""

    def __init__(self, db_client: DBClient):
        self.engine = db_client.get_engine()
        self.logger = logging.getLogger(__name__)

    def truncate_table(self, table_name: str) -> None:
        pass

    def write_chunk(self, df: pd.DataFrame, table_name: str, is_first_chunk: bool = False) -> None:
        """
        Matches the simplified Iris example.
        First chunk uses 'replace' to create the table, subsequent chunks use 'append'.
        """
        try:
            mode = 'replace' if is_first_chunk else 'append'
            
            with self.engine.connect() as conn:
                df.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists=mode,
                    index=False,
                    chunksize=10000 
                )
        except Exception as e:
            self.logger.error(f"Error writing to table {table_name}: {e}")
            raise