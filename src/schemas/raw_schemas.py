from typing import Dict

RAW_DATA_TYPES: Dict[str, Dict] = {
    "train": {
        "building_id": "int32",
        "meter": "int8",
        "timestamp": "datetime64[ns]",
        "meter_reading": "float32"
    },
    "building": {
        "site_id": "int8",
        "building_id": "int32",
        "primary_use": "category",
        "square_feet": "int32",
        "year_built": "float32",
        "floor_count": "float32"
    },
    "weather": {
        "site_id": "int8",
        "timestamp": "datetime64[ns]",
        "air_temperature": "float32",
        "cloud_coverage": "float32",
        "dew_temperature": "float32",
        "precip_depth_1_hr": "float32",
        "sea_level_pressure": "float32",
        "wind_direction": "float32",
        "wind_speed": "float32"
    }
}