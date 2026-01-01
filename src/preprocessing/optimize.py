import pandas as pd
import numpy as np
import re
import gc 
from src.common.logger import get_logger
from src.preprocessing.base import BaseDataAssembler

class Optimizer(BaseDataAssembler):
    """
    Handles high-performance assembly.
    Optimized for low-memory environments (VirtualBox/Docker).
    """

    def __init__(self):
        self.logger = get_logger("ASHRAETransformer")

    def reduce_mem_usage(self, df: pd.DataFrame, use_float16: bool = False) -> pd.DataFrame:
        """
        Memory optimization with modern Pandas type checking and logging.
        """
        start_mem = df.memory_usage().sum() / 1024**2
        self.logger.info(f"Memory optimization pass started. Current: {start_mem:.2f} MB")
        
        for col in df.columns:
            col_type = df[col].dtype
            
            # Use modern checks to avoid DeprecationWarnings
            if pd.api.types.is_datetime64_any_dtype(col_type) or \
               isinstance(col_type, pd.CategoricalDtype):
                continue
            
            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                
                if str(col_type)[:3] == "int":
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)  
                else:
                    if use_float16 and c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
        
        end_mem = df.memory_usage().sum() / 1024**2
        self.logger.info(f"Final memory: {end_mem:.2f} MB (Reduced by {100 * (start_mem - end_mem) / start_mem:.1f}%)")
        return df

    def process(self, df_power_meter, df_building, df_weather):
        """
        Executes merge with aggressive garbage collection to prevent 'Killed' status.
        """
        self.logger.info("Starting Processing Stage...")

        # Optimize initial data
        df_power_meter = self.reduce_mem_usage(df_power_meter)

        # First Merge
        self.logger.info("Merging Energy and Building data...")
        df_train = df_power_meter.merge(
            df_building, 
            on='building_id', 
            how='left'
        )
        
        # Clear original power meter to save RAM
        del df_power_meter
        gc.collect()

        # Casting logic
        self.logger.info("Applying explicit type casting...")
        df_train['year_built'] = df_train['year_built'].fillna(-1) 
        df_train = df_train.astype({
            'building_id': 'int16',
            'meter': 'int8',
            'site_id': 'int8',
            'square_feet': 'int32',
            'year_built': 'int16'
        })
        df_train['primary_use'] = df_train['primary_use'].astype('category')

        df_weather = self.reduce_mem_usage(df_weather)

        # Second Merge: Chunked Weather
        self.logger.info("Performing chunked merge with weather data (500 splits)...")
        chunks = []
        for chunk in np.array_split(df_train, 500):
            merged = chunk.merge(df_weather, on=['site_id', 'timestamp'], how='left')
            chunks.append(merged)
        
        # Free memory from the intermediate df_train before concat
        del df_train
        gc.collect()

        self.logger.info("Concatenating chunks...")
        df_train = pd.concat(chunks, ignore_index=True)
        
        # Free the list of chunks immediately!
        del chunks
        gc.collect()

        # Final cleanup
        df_train.columns = [re.sub(r'[\s\-]+', '_', col.lower().strip()) for col in df_train.columns]
        df_train = self.reduce_mem_usage(df_train)

        return df_train