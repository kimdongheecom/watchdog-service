from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
from app.domain.controlloer.news_controller import NewsController

router = APIRouter()
logger = logging.getLogger("news_main")
news_controller = NewsController()

@router.post("/search", response_model=None)
async def news(request: Request):
    data = await request.json()
    company_name = data.get("company_name")
    logger.info(f"Received company_name: {company_name}")
    result = news_controller.get_news()
    return JSONResponse(content=result)
    