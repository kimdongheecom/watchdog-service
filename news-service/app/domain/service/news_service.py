from collections import Counter
import requests
from bs4 import BeautifulSoup
import logging
from wordcloud import WordCloud # 워드클라우드 임포트
import matplotlib # matplotlib 임포트
matplotlib.use('Agg') # GUI 백엔드 비활성화
import matplotlib.pyplot as plt # pyplot 임포트 (폰트 경로 지정 등에 사용될 수 있음)
import io # 바이트 스트림 처리를 위해 임포트
import base64 # 이미지를 base64로 인코딩하기 위해 임포트

logger = logging.getLogger("news_service")

# 한글 폰트 경로 (Dockerfile에 설치된 경로에 맞게 조정 필요)
# Dockerfile에서 fonts-nanum을 설치했다면 일반적으로 아래 경로 중 하나에서 찾을 수 있습니다.
# 실제 경로는 Docker 이미지 내부에서 `fc-list :lang=ko` 명령 등으로 확인 가능합니다.
FONT_PATH = 'app/static/fonts/NanumGothic.ttf' # 폰트 경로를 프로젝트 내부 경로로 변경

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
        
        # 제목 요소 찾기
        items = soup.select("span[class='sds-comps-text sds-comps-text-ellipsis-1 sds-comps-text-type-headline1']")
        logger.info(f"🎃✨🎉Items: {len(items)}")
        
        # 부모 요소를 탐색하여 링크 추출
        news_list = []
        for item in items[:5]:  # 상위 5개 뉴스만 추출
            title = item.get_text(strip=True)
            
            # 제목 요소의 부모 중에서 a 태그 찾기
            parent_element = item.parent
            while parent_element and parent_element.name != 'a' and parent_element.name != 'html':
                parent_element = parent_element.parent
            
            link = None
            if parent_element and parent_element.name == 'a':
                link = parent_element.get('href')
                logger.info(f"🔗 링크 추출 성공: {link}")
            else:
                logger.warning(f"⚠️ 링크를 찾을 수 없음: {title}")
            
            news_list.append({
                "title": title,
                "link": link
            })
        
        logger.info(f"🎃✨🎉🎊 News List: {news_list}")

        # 링크만 추출해서 리스트로 정리
        links = [news['link'] for news in news_list if news.get('link')]
        print("🔗 추출된 링크 목록:")
        for link in links:
            print(link)

        return {
            "company": company_name,
            "news": news_list
        }



    def get_news_content(self, url: str) -> str:
        """각 뉴스 링크에서 본문 크롤링"""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content.decode('utf-8', 'replace'), "html.parser") # utf-8 디코딩 명시

            # 네이버 뉴스 본문 선택자 (다양한 구조에 대응)
            # 우선순위: #articleBodyContents (구버전), #dic_area (일반), article (HTML5 시맨틱 태그)
            content_selectors = [
                '#articleBodyContents',
                '#dic_area',
                'article#dic_area', # 좀 더 명확한 선택
                'div.article_body', # 다른 언론사 포맷
                'div.newsct_body', # 다른 언론사 포맷
                'article'
            ]
            article = None
            for selector in content_selectors:
                article = soup.select_one(selector)
                if article:
                    break
            
            content = ""
            if article:
                # 불필요한 태그 제거 (광고, 관련뉴스 등)
                tags_to_remove = ['script', 'style', 'iframe', 'footer', 'header', 'aside', '.link_news', '.promotion', '.journalist_info']
                for tag_selector in tags_to_remove:
                    for unwanted_tag in article.select(tag_selector):
                        unwanted_tag.decompose()
                content = article.get_text(separator="\n", strip=True)
            else:
                content = "본문 추출 실패 (선택자 불일치)"
            
            # logger.info(f"📄 URL '{url}' 본문 추출 결과: {content[:200]}...") # 너무 길어서 일부만 로깅
            return content

        except requests.Timeout:
            logger.error(f"❌ 뉴스 본문 크롤링 시간 초과: {url}")
            return "본문 크롤링 시간 초과"
        except Exception as e:
            logger.error(f"❌ 뉴스 본문 크롤링 중 오류 ({url}): {str(e)}")
            return f"본문 크롤링 오류: {str(e)}"

    def analyze_esg_keywords(self, contents: list) -> dict:
        """뉴스 본문 리스트에서 ESG 키워드 등장 빈도 분석"""
        esg_keywords_path = "app/domain/service/esg_keywords.txt" # 경로 수정
        try:
            with open(esg_keywords_path, "r", encoding="utf-8") as file:
                esg_keywords = [line.strip() for line in file.readlines() if line.strip()]
            logger.info(f"🔑 ESG 키워드 {len(esg_keywords)}개 불러오기 성공: {esg_keywords_path}")
        except FileNotFoundError:
            logger.error(f"❌ ESG 키워드 파일({esg_keywords_path})을 찾을 수 없습니다.")
            return {"error": f"ESG 키워드 파일({esg_keywords_path})을 찾을 수 없습니다."}


        combined_text = " ".join(contents)
        if not combined_text.strip():
            logger.warning("⚠️ 분석할 텍스트 내용이 없습니다.")
            return {}
            
        word_freq = Counter()

        for word in esg_keywords:
            count = combined_text.count(word)
            if count > 0:
                word_freq[word] = count
        
        logger.info(f"📊 ESG 키워드 빈도 분석 완료: {dict(word_freq)}")
        return dict(word_freq)

    def generate_wordcloud_image(self, word_freq: dict) -> str:
        """
        단어 빈도수 데이터를 기반으로 워드클라우드 이미지를 생성하고
        Base64로 인코딩된 문자열을 반환합니다.
        """
        if not word_freq:
            logger.info("워드클라우드 생성을 위한 데이터가 없습니다.")
            return "" # 빈 문자열 또는 에러 메시지/기본 이미지 Base64 반환 가능

        try:
            # WordCloud 객체 생성
            # Mac에서 Brew로 fontconfig 설치 시 /opt/homebrew/etc/fonts/conf.d 경로에 폰트 설정이 있을 수 있음
            # Dockerfile에 지정된 폰트 경로를 사용해야 합니다.
            wc = WordCloud(
                font_path=FONT_PATH,
                width=800,
                height=400,
                background_color="white",
                max_words=100 # 표시할 최대 단어 수
            ).generate_from_frequencies(word_freq)

            # 이미지 객체로 변환 후 바이트 스트림에 저장
            img_byte_arr = io.BytesIO()
            wc.to_image().save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Base64로 인코딩
            img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
            logger.info("🖼️ 워드클라우드 이미지 생성 및 Base64 인코딩 성공")
            return img_base64
        except Exception as e:
            # 폰트 경로 문제 발생 시 여기서 에러 로깅 가능
            logger.error(f"❌ 워드클라우드 이미지 생성 실패: {str(e)}")
            logger.error(f"ℹ️ 사용된 폰트 경로: {FONT_PATH}")
            # 폰트 파일을 찾을 수 없는 경우 OSError: cannot open resource 발생 가능
            if "cannot open resource" in str(e) or "No such file or directory" in str(e):
                 logger.error("🆘 폰트 파일을 찾을 수 없습니다. Dockerfile에 폰트가 올바르게 설치되었는지, FONT_PATH가 정확한지 확인하세요.")
            return "" # 또는 에러 처리에 맞는 값 반환