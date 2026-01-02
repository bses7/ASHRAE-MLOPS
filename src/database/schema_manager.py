import logging
from sqlalchemy import text, inspect
from src.database.connection import DBClient

logger = logging.getLogger(__name__)

class SchemaManager:
    """Creates ColumnStore tables if they do not exist."""

    def __init__(self, db_client: DBClient):
        self.engine = db_client.get_engine()

    def create_production_tables(self):
        logger.info("Verifying ColumnStore Production Schema...")
        
        table_definitions = {
            "fact_energy_usage": """
                CREATE TABLE IF NOT EXISTS `fact_energy_usage` (
                    `building_id` INT,
                    `meter` INT,
                    `timestamp` DATETIME,
                    `meter_reading` FLOAT
                ) ENGINE=ColumnStore;
            """,
            "dim_building": """
                CREATE TABLE IF NOT EXISTS `dim_building` (
                    `building_id` INT,
                    `site_id` INT,
                    `primary_use` VARCHAR(255),
                    `square_feet` INT,
                    `year_built` INT
                ) ENGINE=ColumnStore;
            """,
            "dim_weather": """
                CREATE TABLE IF NOT EXISTS `dim_weather` (
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
                    `week` INT
                ) ENGINE=ColumnStore;
            """
        }

        with self.engine.connect() as conn:
            for table_name, ddl_query in table_definitions.items():
                logger.debug(f"Ensuring table exists: {table_name}")
                conn.execute(text(ddl_query))
            # conn.commit()
        logger.info("Schema verification complete.")