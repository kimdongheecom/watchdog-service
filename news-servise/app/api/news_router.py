from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
from app.domain.controlloer.news_controller import NewsController

router = APIRouter()
logger = logging.getLogger("news_main")
news_controller = NewsController()

@router.post("/", response_model=None)
async def news(request: Request):
    result = news_controller.preprocess()
    return JSONResponse(content=result)
    