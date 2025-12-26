import logging
from sqlalchemy import text, inspect
from src.database.connection import DBClient

logger = logging.getLogger(__name__)

class SchemaManager:
    """Creates ColumnStore tables. """

    def __init__(self, db_client: DBClient):
        self.engine = db_client.get_engine()

    def create_production_tables(self):
        """
        Creates the Star Schema tables. 
        """
        logger.info("Verifying ColumnStore Production Schema...")
        
        # Define the exact SQL for each table (Cleanest possible syntax)
        table_definitions = {
            "fact_energy_usage": """
                CREATE TABLE `fact_energy_usage` (
                    `building_id` INT,
                    `meter` INT,
                    `timestamp` DATETIME,
                    `meter_reading` FLOAT,
                    `ingested_at` DATETIME
                ) ENGINE=ColumnStore;
            """,
            "dim_building": """
                CREATE TABLE `dim_building` (
                    `building_id` INT,
                    `site_id` INT,
                    `primary_use` VARCHAR(255),
                    `square_feet` INT,
                    `year_built` INT,
                    `floor_count` INT,
                    `ingested_at` DATETIME
                ) ENGINE=ColumnStore;
            """,
            "dim_weather": """
                CREATE TABLE `dim_weather` (
                    `site_id` INT,
                    `timestamp` DATETIME,
                    `air_temperature` FLOAT,
                    `cloud_coverage` FLOAT,
                    `dew_temperature` FLOAT,
                    `precip_depth_1_hr` FLOAT,
                    `sea_level_pressure` FLOAT,
                    `wind_direction` FLOAT,
                    `wind_speed` FLOAT,
                    `datetime` DATETIME,
                    `day` INT,
                    `month` INT,
                    `week` INT,
                    `ingested_at` DATETIME
                ) ENGINE=ColumnStore;
            """
        }

        # Use SQLAlchemy Inspector to check what tables already exist
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()

        try:
            with self.engine.begin() as conn:
                conn.execute(text("USE ashrae_db"))
                
                for table_name, ddl_query in table_definitions.items():
                    if table_name in existing_tables:
                        logger.info(f"Table '{table_name}' already exists. Skipping creation.")
                    else:
                        logger.info(f"Creating table '{table_name}'...")
                        conn.execute(text(ddl_query))
                        
            logger.info("ColumnStore Star Schema is synchronized.")
        except Exception as e:
            logger.error(f"Failed to create ColumnStore tables: {e}")
            raise