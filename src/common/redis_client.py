import redis
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import io
from src.common.logger import get_logger

class RedisClient:
    """
    Handles high-performance storage and retrieval of DataFrames using Redis.
    Uses PyArrow for Parquet serialization to preserve memory-optimized schemas.
    """

    def __init__(self, redis_config: dict):
        self.logger = get_logger("RedisClient")
        try:
            self.client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=False  # Crucial: We are storing binary bytes
            )
            # Test connection
            self.client.ping()
            self.logger.info(f"Connected to Redis at {redis_config['host']}:{redis_config['port']}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise

    def store_dataframe(self, df: pd.DataFrame, key: str):
        """
        Serializes a DataFrame to Parquet and stores it in Redis.
        """
        try:
            self.logger.info(f"Serializing DataFrame to Parquet for Redis key: {key}")
            
            # Convert Pandas to PyArrow Table
            table = pa.Table.from_pandas(df)
            
            # Write to a buffer in Parquet format
            buf = io.BytesIO()
            pq.write_table(table, buf)
            
            # Store binary data in Redis
            self.client.set(key, buf.getvalue())
            self.logger.info(f"Successfully stored {len(df)} rows in Redis at key: {key}")
            
        except Exception as e:
            self.logger.error(f"Error storing DataFrame in Redis: {e}")
            raise

    def load_dataframe(self, key: str) -> pd.DataFrame:
        """
        Retrieves binary Parquet data from Redis and deserializes it to a DataFrame.
        """
        try:
            self.logger.info(f"Retrieving binary data from Redis key: {key}")
            retrieved_data = self.client.get(key)
            
            if retrieved_data is None:
                raise KeyError(f"Key '{key}' not found in Redis.")

            # Read Parquet from binary buffer
            buffer_reader = pa.BufferReader(retrieved_data)
            retrieved_table = pq.read_table(buffer_reader)
            
            df = retrieved_table.to_pandas()
            self.logger.info(f"Successfully retrieved {len(df)} rows from Redis key: {key}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading DataFrame from Redis: {e}")
            raise