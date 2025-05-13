
from app.domain.service.news_service import NewsService


class NewsController:
    def __init__(self):
        self.news_service = NewsService()

    def get_news(self):
        return self.news_service.get_news()
