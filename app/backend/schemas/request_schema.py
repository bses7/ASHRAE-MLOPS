from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    building_id: int = Field(..., example=10)
    meter: int = Field(..., example=0)
    site_id: int = Field(..., example=0)
    primary_use: str = Field(..., example="Education")
    square_feet: int = Field(..., example=50000)
    air_temperature: float = Field(..., example=22.5)
    cloud_coverage: float = Field(..., example=2.0)
    dew_temperature: float = Field(..., example=10.0)
    precip_depth_1_hr: float = Field(..., example=0.0)
    sea_level_pressure: float = Field(..., example=1012.0)
    wind_direction: float = Field(..., example=160.0)
    wind_speed: float = Field(..., example=4.0)
    day: int = Field(..., example=1)
    month: int = Field(..., example=5)
    week: int = Field(..., example=18)
    hour: int = Field(..., example=12)
    is_weekend: int = Field(..., example=0)

    model_version: str = Field(default="latest", description="The version of the model to use for inference")

class PredictionOutput(BaseModel):
    meter_reading: float
    status: str = "success"
    model_version: str = "latest"