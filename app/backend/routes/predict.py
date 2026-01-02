from fastapi import APIRouter, HTTPException
from app.backend.schemas.request_schema import PredictionInput, PredictionOutput
from app.backend.services.model_service import ModelService

router = APIRouter(prefix="/api/v1", tags=["Inference"])
model_service = ModelService()

@router.post("/predict", response_model=PredictionOutput)
async def predict(data: PredictionInput):
    try:
        result = model_service.predict(data.dict())
        return PredictionOutput(meter_reading=result)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))