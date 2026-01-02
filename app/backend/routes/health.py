from fastapi import APIRouter
from app.backend.services.model_service import ModelService


router = APIRouter(tags=["System"])

@router.get("/health")
def health_check():
    return {"status": "online", "model_version": "LGBM-v1"}

@router.get("/metadata")
def get_metadata():
    service = ModelService()
    return service.get_model_metadata()