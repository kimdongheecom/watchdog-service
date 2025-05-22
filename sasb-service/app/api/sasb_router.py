from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
from app.domain.controller.sasb_controller import SasbController
from app.domain.model.sasb_schema import SasbRequest

router = APIRouter()
logger = logging.getLogger("sasb_main")
sasb_controller = SasbController()

@router.post("/search")
async def sasb(req: SasbRequest):
    logger.info(f"🔍 기업명 수신: {req.company_name}")
    result = sasb_controller.get_sasb(req.company_name)
    return JSONResponse(content=result)
    