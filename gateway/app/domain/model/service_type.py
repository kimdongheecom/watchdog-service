from enum import Enum
import os


class ServiceType(str, Enum):
    NEWS = "news"

# ✅ 환경 변수에서 서비스 URL 가져오기
NEWS_SERVICE_URL = os.getenv("NEWS_SERVICE_URL")


SERVICE_URLS = {
    ServiceType.NEWS: NEWS_SERVICE_URL,
}