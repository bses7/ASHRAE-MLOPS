import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.common.logger import get_logger
import gc

class MLPreprocessor:
    """
    Extreme Memory-Optimized Feature Engineering.
    Uses In-Place modifications and Column-by-Column scaling to prevent OOM.
    """

    def __init__(self, target_column: str = "meter_reading"):
        self.logger = get_logger("MLPreprocessor")
        self.target_column = target_column
        self.scaler_map = {} # Store scalers for each column

    def prepare_ml_features(self, df: pd.DataFrame):
        """
        Transforms the dataframe IN-PLACE. Does not create copies.
        """
        self.logger.info("Starting Extreme Memory-Optimized Feature Engineering...")

        # 1. Extract Target as a standalone Numpy array (Float32)
        y = df[self.target_column].values.astype('float32')
        self.logger.info("Target extracted.")

        # 2. Drop columns IN-PLACE to save RAM
        drop_cols = [self.target_column, 'timestamp', 'datetime']
        for col in drop_cols:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
        gc.collect()

        # 3. Handle Categorical Features (Using codes directly - No Strings!)
        categorical_cols = df.select_dtypes(include=['category', 'object']).columns.tolist()
        for col in categorical_cols:
            self.logger.info(f"Encoding categorical: {col}")
            # Use pandas codes instead of sklearn LabelEncoder to avoid string conversion
            if isinstance(df[col].dtype, pd.CategoricalDtype):
                df[col] = df[col].cat.codes.astype('int16')
            else:
                df[col] = pd.Categorical(df[col]).codes.astype('int16')
            gc.collect()

        # 4. Handle Numeric Features (Column-by-Column Scaling)
        # Scaling everything at once creates a massive Float64 temporary matrix.
        # We scale one column at a time to keep the RAM footprint tiny.
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        for col in numeric_cols:
            if col in categorical_cols: continue # Already handled
            
            self.logger.info(f"Scaling numeric: {col}")
            scaler = StandardScaler()
            # We reshape to (-1, 1) as required by sklearn, but only for one column
            df[col] = scaler.fit_transform(df[[col]].values.astype('float32')).astype('float32')
            self.scaler_map[col] = scaler
            gc.collect()

        self.logger.info(f"Feature engineering complete. In-memory shape: {df.shape}")
        return df, y

    def split_data(self, X: pd.DataFrame, y: np.ndarray, test_size=0.2):
        """
        Splits data. Since X is the optimized dataframe, we split it directly.
        """
        self.logger.info(f"Performing final split on 20M rows...")
        
        # train_test_split will create copies, but since our types are 
        # now all int16 and float32, the total size is ~1.2GB.
        # 1.2GB (X) + 0.9GB (X_train) + 0.3GB (X_test) = 2.4GB. 
        # This SHOULD fit in your RAM now.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.logger.info(f"Split successful. Train: {X_train.shape}, Test: {X_test.shape}")
        return X_train, X_test, y_train, y_test