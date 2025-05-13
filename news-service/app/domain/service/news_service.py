import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("news_service")

class NewsService:
    def __init__(self):
        pass

    def get_news(self, company_name: str):
        base_url = "https://search.naver.com/search.naver"
        params = {
            "where": "news",
            "ie": "utf8",
            "sm": "nws_hty",
            "query": company_name
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            response = requests.get(base_url, headers=headers, params=params)
            logger.info(f"🎃✨🎉🎊 Response: {response.text}")
            response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        except requests.RequestException as e:
            logger.error(f"❌ 네이버 뉴스 요청 실패: {str(e)}")
            return {"error": f"네이버 뉴스 요청 실패: {str(e)}"}

        soup = BeautifulSoup(response.text, "html.parser")
        logger.info(f"🎃✨🎉🎊 Soup: {soup}")
        items = soup.select("a.n6AJosQA40hUOAe_Vplg")
        logger.info(f"🎃✨🎉�� Items: {items}")

        news_list = []
        for item in items[:5]:  # 상위 5개 뉴스만 추출
            title = item.get_text(strip=True)
            link = item.get("href")
            news_list.append({
                "title": title,
                "link": link
            })
        logger.info(f"🎃✨🎉🎊 News List: {news_list}")

        return {
            "company": company_name,
            "news": news_list
        }
