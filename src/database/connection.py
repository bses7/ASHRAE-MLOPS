import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

class DBClient:
    """Manages connectivity to MariaDB ColumnStore."""
    
    def __init__(self, config: dict):
        self.uri = f"{config['dialect']}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        self._engine: Engine | None = None
        self.logger = logging.getLogger(__name__)

    def get_engine(self) -> Engine:
        if self._engine is None:
            try:
                # local_infile=1 in query string and connect_args is required for Bulk Load
                self._engine = create_engine(
                    f"{self.uri}?local_infile=1", 
                    pool_pre_ping=True, 
                    echo=False,
                    connect_args={'local_infile': True}
                )
                self.logger.info("Connected to MariaDB ColumnStore (Bulk Load Enabled).")
            except Exception as e:
                self.logger.error(f"Failed to connect to database: {e}")
                raise
        return self._engine