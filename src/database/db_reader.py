import pandas as pd
import connectorx as cx
from src.common.logger import get_logger
from src.database.connection import DBClient

class DatabaseReader:
    """
    Handles high-speed data retrieval from MariaDB.
    Uses ConnectorX for heavy fact tables and SQLAlchemy for dimension tables.
    """

    def __init__(self, db_client: DBClient, db_config: dict):
        self.logger = get_logger("DatabaseReader")
        self.db_client = db_client
        
        # ConnectorX requires a raw 'mysql://' protocol (it does not use the pymysql dialect)
        self.cx_uri = (
            f"mysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

    def read_fact_table(self, table_name: str) -> pd.DataFrame:
        """Reads large tables at high speed using Rust-based ConnectorX."""
        self.logger.info(f"Retrieving {table_name}")
        try:
            query = f"SELECT * FROM {table_name}"
            # ConnectorX is significantly faster for 20M+ rows
            return cx.read_sql(self.cx_uri, query)
        except Exception as e:
            self.logger.error(f"ConnectorX failed to read {table_name}: {e}")
            raise

    def read_dim_table(self, table_name: str) -> pd.DataFrame:
        """Reads dimension tables using the standard SQLAlchemy engine from DBClient."""
        self.logger.info(f"Retrieving {table_name}")
        try:
            # We reuse the engine created in connection.py
            engine = self.db_client.get_engine()
            return pd.read_sql(table_name, con=engine)
        except Exception as e:
            self.logger.error(f"SQLAlchemy failed to read {table_name}: {e}")
            raise