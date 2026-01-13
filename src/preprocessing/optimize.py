import pandas as pd
import numpy as np
import re
import gc 
from src.common.logger import get_logger
from src.preprocessing.base import BaseDataAssembler

class Optimizer(BaseDataAssembler):
    """
    Optimization for low-memory environments.
    """

    def __init__(self):
        self.logger = get_logger("ASHRAETransformer")

    def reduce_mem_usage(self, df: pd.DataFrame, use_float16: bool = False) -> pd.DataFrame:
        """
        Memory optimization with Pandas type checking and logging.
        """
        start_mem = df.memory_usage().sum() / 1024**2
        self.logger.info(f"Memory optimization pass started. Current: {start_mem:.2f} MB")
        
        for col in df.columns:
            col_type = df[col].dtype
            
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

    # def process(self, df_power_meter, df_building, df_weather):
    #     """
    #     Executes merge
    #     """
    #     self.logger.info("Starting Processing Stage...")

    #     df_power_meter = self.reduce_mem_usage(df_power_meter)

    #     self.logger.info("Merging Energy and Building data...")
    #     df_train = df_power_meter.merge(
    #         df_building, 
    #         left_on='building_id',right_on='building_id',how='left'
    #     )
        
    #     del df_power_meter
    #     gc.collect()

    #     self.logger.info("Applying explicit type casting...")
    #     # df_train['year_built'] = df_train['year_built'].fillna(-1) 
    #     df_train = df_train.astype({
    #         'building_id': 'int16',
    #         'meter': 'int8',
    #         'site_id': 'int8',
    #         'square_feet': 'int32',
    #         'year_built': 'int16'
    #     })
    #     df_train['primary_use'] = df_train['primary_use'].astype('category')

    #     df_weather = self.reduce_mem_usage(df_weather)

    #     self.logger.info("Performing chunked merge with weather data (500 splits)...")
    #     df_train_list = []

    #     for chunk in np.array_split(df_train, 500):
    #         df_train_list.append(
    #             chunk.merge(df_weather, on=['site_id', 'timestamp'], how='left')
    #         )
    #         del chunk
    #         gc.collect()

    #     df_train = pd.concat(df_train_list, ignore_index=True)
    #     del df_train_list
    #     gc.collect()

    #     df_train = df_train.dropna()

    #     # self.logger.info("Concatenating chunks...")
    #     # df_train = pd.concat(chunks, ignore_index=True)
        
    #     # del chunks
    #     # gc.collect()

    #     df_train.columns = [re.sub(r'[\s\-]+', '_', col.lower().strip()) for col in df_train.columns]
    #     df_train = self.reduce_mem_usage(df_train)

    #     return df_train

    def process(self, df_power_meter, df_building, df_weather):
        self.logger.info("Starting High-Efficiency Processing Stage...")

        # 1. Optimize Building Data (Small)
        df_building['primary_use'] = df_building['primary_use'].astype('category')
        df_building = self.reduce_mem_usage(df_building, use_float16=True)
        
        df_weather['timestamp'] = pd.to_datetime(df_weather['timestamp'])
    
        df_weather = df_weather.set_index(['site_id', 'timestamp'])
        df_weather = self.reduce_mem_usage(df_weather, use_float16=True)

        df_power_meter['timestamp'] = pd.to_datetime(df_power_meter['timestamp'])
        df_power_meter = self.reduce_mem_usage(df_power_meter, use_float16=True)

     
        self.logger.info("Mapping Building data...")
        df_building = df_building.set_index('building_id')
        
        df_train = df_power_meter.join(df_building, on='building_id', how='left')
        
        del df_power_meter, df_building
        gc.collect()

        self.logger.info("Joining Weather data...")
        df_train = df_train.join(df_weather, on=['site_id', 'timestamp'], how='left')
        
        del df_weather
        gc.collect()

        self.logger.info("Cleaning up...")
        df_train.dropna(inplace=True)
        
        df_train.columns = [re.sub(r'[\s\-]+', '_', col.lower().strip()) for col in df_train.columns]
        
        df_train = self.reduce_mem_usage(df_train, use_float16=True)

        return df_train