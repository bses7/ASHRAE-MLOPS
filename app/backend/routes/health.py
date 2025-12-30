from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/health")
def health_check():
    return {"status": "online", "model_version": "LGBM-v1"}