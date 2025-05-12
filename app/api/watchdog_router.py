from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
from app.domain.controlloer.watchdog_controller import WatchdogController

router = APIRouter()
logger = logging.getLogger("watchdog_main")
watchdog_controller = WatchdogController()

@router.post("/watchdog", response_model=None)
async def watchdog(request: Request):
    result = watchdog_controller.preprocess()
    return JSONResponse(content=result)
    