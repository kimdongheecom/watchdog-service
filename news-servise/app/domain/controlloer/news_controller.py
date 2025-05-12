
from app.domain.service.news_service import NewsService


class NewsController:
    def __init__(self):
        self.news_service = NewsService()

    def preprocess(self):
        return self.news_service.preprocess()
