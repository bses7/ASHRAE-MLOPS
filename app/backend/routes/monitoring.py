from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from src.monitoring.monitor import ModelMonitor
from src.common.config_loader import load_yaml_config

router = APIRouter(prefix="/api/v1/monitoring", tags=["Model Monitoring"])

config = load_yaml_config("configs/pipeline_config.yaml")

@router.get("/report", response_class=HTMLResponse)
async def get_model_monitoring_report():
    """
    Generates and serves a real-time Evidently AI health dashboard.
    """
    monitor = ModelMonitor(config)
    html_report = monitor.generate_html_report()
    return HTMLResponse(content=html_report, status_code=200)