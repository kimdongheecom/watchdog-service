from app.domain.service.news_service import NewsService
import logging

logger = logging.getLogger(__name__) # news_main 대신 __name__ 사용 권장

class NewsController:
    def __init__(self):
        self.news_service = NewsService()

    def get_news(self, company_name: str):
        # 1. 뉴스 정보 및 본문 가져오기 (get_news가 본문까지 가져오도록 수정됨)
        news_data_with_content = self.news_service.get_news(company_name)
        
        if "error" in news_data_with_content:
            logger.error(f"뉴스 데이터 가져오기 실패: {news_data_with_content['error']}")
            return news_data_with_content # 에러가 있다면 그대로 반환

        news_list = news_data_with_content.get("news", [])

        # 2. 본문만 추출해서 리스트로 구성
        # 이제 news_list 각 아이템에 'content'가 이미 포함되어 있음
        contents = [item.get("content", "") for item in news_list if item.get("content")]
        
        if not contents:
            logger.warning("분석할 뉴스 본문 내용이 없습니다.")
            # 빈 contents로 분석 시도 또는 특정 응답 반환
            esg_analysis = {}
            wordcloud_image_base64 = ""
        else:
            # 3. ESG 키워드 분석
            esg_analysis = self.news_service.analyze_esg_keywords(contents)

            # 4. 워드클라우드 이미지 생성 (분석된 키워드 빈도 기반)
            wordcloud_image_base64 = self.news_service.generate_wordcloud_image(esg_analysis)

        # 5. ESG 분석 결과 및 워드클라우드 이미지 포함한 응답 생성
        return {
            "company": company_name,
            "news": news_list, # 제목, 링크, 본문 포함
            "esg_analysis": esg_analysis,
            "wordcloud_image": wordcloud_image_base64 # base64 인코딩된 이미지 문자열
        }
