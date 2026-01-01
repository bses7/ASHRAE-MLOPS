import pandas as pd
import connectorx as cx
from src.common.logger import get_logger
from src.database.connection import DBClient

class DatabaseReader:
    """
    Handles data retrieval from MariaDB.
    """

    def __init__(self, db_client: DBClient, db_config: dict):
        self.logger = get_logger("DatabaseReader")
        self.db_client = db_client
        
        self.cx_uri = (
            f"mysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

    def read_fact_table(self, table_name: str) -> pd.DataFrame:
        """Reads large tables at high speed"""
        self.logger.info(f"Retrieving {table_name}")
        try:
            query = f"SELECT * FROM {table_name}"
            return cx.read_sql(self.cx_uri, query)
        except Exception as e:
            self.logger.error(f"ConnectorX failed to read {table_name}: {e}")
            raise

    def read_dim_table(self, table_name: str) -> pd.DataFrame:
        """Reads dimension tables"""
        self.logger.info(f"Retrieving {table_name}")
        try:
            engine = self.db_client.get_engine()
            return pd.read_sql(table_name, con=engine)
        except Exception as e:
            self.logger.error(f"SQLAlchemy failed to read {table_name}: {e}")
            raise