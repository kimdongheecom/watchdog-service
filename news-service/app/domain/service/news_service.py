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

# 🔧 [Selenium 관련 추가 import]
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

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
        
        link1 = links[0]
        content = self.crawl_with_selenium(link1)
        print("🔗 추출된 컨텐츠 내용:",content)

  
    
    def crawl_with_selenium(self, link: str) -> str:
        """Selenium을 이용한 뉴스 본문 동적 크롤링 (Docker 최적화)"""
        
        # ChromeDriver는 Docker 내부 PATH에 있거나, 명시적 경로 사용:
        CHROMEDRIVER_IN_CONTAINER_PATH = "/usr/bin/chromedriver" 

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")  # Docker에서 root로 실행 시 필수
        options.add_argument("--disable-dev-shm-usage")  # 제한된 리소스 문제 해결
        options.add_argument("--disable-gpu") # headless 모드에서 권장
        options.add_argument("--window-size=1920x1080") # 반응형 사이트에 도움될 수 있음
        
        # 이 User-Agent를 Dockerfile의 CHROME_VERSION과 일치시키면 좋음
        # 예: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Safari/537.36"
        # 간단하게 일반적인 것을 사용해도 무방:
        options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        
        # chromedriver가 PATH에 있다면 Service()에 executable_path가 필요 없을 수 있음
        # service = ChromeService()
        # 하지만 Docker 환경에서는 명시하는 것이 더 안전:
        service = ChromeService(executable_path=CHROMEDRIVER_IN_CONTAINER_PATH)
        
        driver = None # finally 블록을 위해 driver를 None으로 초기화
        try:
            driver = webdriver.Chrome(service=service, options=options)
            logger.info(f"🚀 Selenium WebDriver 시작됨. URL: {link}")
            driver.get(link)
            logger.info(f"🎇🎆🎋🎁 Selenium WebDriver 시작됨. URL: {link}")
            
            # JavaScript 로드 시간 부여, 필요에 따라 조정
            # time.sleep(3) # 복잡한 페이지에는 너무 짧을 수 있음
            # AJAX가 많은 사이트의 경우 WebDriverWait 필요할 수 있음
            driver.implicitly_wait(5) # 요소가 나타날 때까지 최대 5초 대기
            logger.info(f"🧶🧥🥽 Selenium WebDriver 시작됨. URL: {link}")

            # 뉴스 콘텐츠에 대한 일반적인 선택자 시도
            selectors = [
                'div#dic_area',             # 네이버 뉴스 일반
                'article#dic_area',         # 좀 더 구체적인 네이버 뉴스
                '#articleBodyContents',     # 구형 네이버 뉴스
                'div.article_body',         # 많은 뉴스 사이트 공통
                'div.newsct_article',       # 다른 일반적인 패턴
                'div.news_view',            # 또 다른 패턴
                'div#newsct_article',       # 특정 ID
                'section.article-view',     # 일반적인 section 태그
                'article',                  # 일반 HTML5 article 태그
                'main'                      # 일반 HTML5 main 태그
            ]
            logger.info(f"🎃✨🎉🎊 선택자 시도 중: {selectors[0]}")
            content_text = ""
            for i, selector in enumerate(selectors):
                try:
                    # logger.debug(f"선택자 시도 중 [{i+1}/{len(selectors)}]: '{selector}' (URL: {link})")
                    # 즉시 예외를 발생시키지 않고 존재 확인을 위해 find_elements 사용
                    elements = driver.find_elements("css selector", selector)
                    if elements:
                        # 발견된 첫 번째 요소에서 텍스트 가져오기 (주요 내용으로 가정)
                        # 일부 페이지는 여러 개가 일치할 수 있으며, 여기서는 비어있지 않은 첫 번째 것을 사용
                        for elem in elements:
                            elem_text = elem.text.strip()
                            if elem_text: # 비어있지 않은 텍스트 발견
                                content_text = elem_text
                                logger.info(f"✅ 내용 추출 성공 (선택자: '{selector}') (URL: {link})")
                                break # 내부 루프(elements) 탈출
                        if content_text:
                            break # 외부 루프(selectors) 탈출
                except Exception as e_select:
                    logger.warning(f"⚠️ 선택자 '{selector}' 사용 중 오류 또는 요소 없음 (URL {link}): {str(e_select)}")
            
            if not content_text:
                logger.warning(f"⁉️ 위 선택자들로 내용을 찾지 못했습니다 (URL: {link}). 페이지 전체 텍스트를 시도합니다.")
                # 대체: body에서 모든 텍스트 가져오기
                try:
                    content_text = driver.find_element("css selector", "body").text.strip()
                    if not content_text:
                         content_text = "[본문 내용 없음 - 모든 선택자 실패 및 body 비어있음]"
                except Exception as e_body:
                    logger.error(f"❌ Body 텍스트 추출 실패 (URL {link}): {str(e_body)}")
                    content_text = "[본문 내용 없음 - Body 접근 불가]"

            logger.info(f"🎃✨🎉🎊 최종 컨텐츠 텍스트: {content_text}")
            return content_text

        except Exception as e:
            logger.error(f"❌❌❌ Selenium 크롤링 중 심각한 오류 발생 ({link}): {str(e)}")
            # page_source = driver.page_source if driver else "드라이버 초기화 안됨"
            # logger.debug(f"오류 발생 시점의 페이지 소스 (처음 1000자):\n{page_source[:1000]}")
            return f"[Selenium 크롤링 오류]: {str(e)}"

        finally:
            if driver:
                driver.quit()
                logger.info(f"🧹 Selenium WebDriver 종료됨 (URL: {link})")

    # ... [get_news_content (정적), analyze_esg_keywords, generate_wordcloud_image 같은 다른 메소드들]
    # ... 워드클라우드 다시 활성화 시 FONT_PATH가 정확한지 확인



    # def get_news_content(self, url: str) -> str:
    #     """각 뉴스 링크에서 본문 크롤링"""
    #     try:
    #         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    #         response.raise_for_status()
    #         soup = BeautifulSoup(response.content.decode('utf-8', 'replace'), "html.parser") # utf-8 디코딩 명시

    #         # 네이버 뉴스 본문 선택자 (다양한 구조에 대응)
    #         # 우선순위: #articleBodyContents (구버전), #dic_area (일반), article (HTML5 시맨틱 태그)
    #         content_selectors = [
    #             '#articleBodyContents',
    #             '#dic_area',
    #             'article#dic_area', # 좀 더 명확한 선택
    #             'div.article_body', # 다른 언론사 포맷
    #             'div.newsct_body', # 다른 언론사 포맷
    #             'article'
    #         ]
    #         article = None
    #         for selector in content_selectors:
    #             article = soup.select_one(selector)
    #             if article:
    #                 break
            
    #         content = ""
    #         if article:
    #             # 불필요한 태그 제거 (광고, 관련뉴스 등)
    #             tags_to_remove = ['script', 'style', 'iframe', 'footer', 'header', 'aside', '.link_news', '.promotion', '.journalist_info']
    #             for tag_selector in tags_to_remove:
    #                 for unwanted_tag in article.select(tag_selector):
    #                     unwanted_tag.decompose()
    #             content = article.get_text(separator="\n", strip=True)
    #         else:
    #             content = "본문 추출 실패 (선택자 불일치)"
            
    #         # logger.info(f"📄 URL '{url}' 본문 추출 결과: {content[:200]}...") # 너무 길어서 일부만 로깅
    #         return content

    #     except requests.Timeout:
    #         logger.error(f"❌ 뉴스 본문 크롤링 시간 초과: {url}")
    #         return "본문 크롤링 시간 초과"
    #     except Exception as e:
    #         logger.error(f"❌ 뉴스 본문 크롤링 중 오류 ({url}): {str(e)}")
    #         return f"본문 크롤링 오류: {str(e)}"
            

    # def analyze_esg_keywords(self, contents: list) -> dict:
    #     """뉴스 본문 리스트에서 ESG 키워드 등장 빈도 분석"""
    #     esg_keywords_path = "app/domain/service/esg_keywords.txt" # 경로 수정
    #     try:
    #         with open(esg_keywords_path, "r", encoding="utf-8") as file:
    #             esg_keywords = [line.strip() for line in file.readlines() if line.strip()]
    #         logger.info(f"🔑 ESG 키워드 {len(esg_keywords)}개 불러오기 성공: {esg_keywords_path}")
    #     except FileNotFoundError:
    #         logger.error(f"❌ ESG 키워드 파일({esg_keywords_path})을 찾을 수 없습니다.")
    #         return {"error": f"ESG 키워드 파일({esg_keywords_path})을 찾을 수 없습니다."}


    #     combined_text = " ".join(contents)
    #     if not combined_text.strip():
    #         logger.warning("⚠️ 분석할 텍스트 내용이 없습니다.")
    #         return {}
            
    #     word_freq = Counter()

    #     for word in esg_keywords:
    #         count = combined_text.count(word)
    #         if count > 0:
    #             word_freq[word] = count
        
    #     logger.info(f"📊 ESG 키워드 빈도 분석 완료: {dict(word_freq)}")
    #     return dict(word_freq)

    # def generate_wordcloud_image(self, word_freq: dict) -> str:
    #     """
    #     단어 빈도수 데이터를 기반으로 워드클라우드 이미지를 생성하고
    #     Base64로 인코딩된 문자열을 반환합니다.
    #     """
    #     if not word_freq:
    #         logger.info("워드클라우드 생성을 위한 데이터가 없습니다.")
    #         return "" # 빈 문자열 또는 에러 메시지/기본 이미지 Base64 반환 가능

    #     try:
    #         # WordCloud 객체 생성
    #         # Mac에서 Brew로 fontconfig 설치 시 /opt/homebrew/etc/fonts/conf.d 경로에 폰트 설정이 있을 수 있음
    #         # Dockerfile에 지정된 폰트 경로를 사용해야 합니다.
    #         wc = WordCloud(
    #             font_path=FONT_PATH,
    #             width=800,
    #             height=400,
    #             background_color="white",
    #             max_words=100 # 표시할 최대 단어 수
    #         ).generate_from_frequencies(word_freq)

    #         # 이미지 객체로 변환 후 바이트 스트림에 저장
    #         img_byte_arr = io.BytesIO()
    #         wc.to_image().save(img_byte_arr, format='PNG')
    #         img_byte_arr = img_byte_arr.getvalue()

    #         # Base64로 인코딩
    #         img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
    #         logger.info("🖼️ 워드클라우드 이미지 생성 및 Base64 인코딩 성공")
    #         return img_base64
    #     except Exception as e:
    #         # 폰트 경로 문제 발생 시 여기서 에러 로깅 가능
    #         logger.error(f"❌ 워드클라우드 이미지 생성 실패: {str(e)}")
    #         logger.error(f"ℹ️ 사용된 폰트 경로: {FONT_PATH}")
    #         # 폰트 파일을 찾을 수 없는 경우 OSError: cannot open resource 발생 가능
    #         if "cannot open resource" in str(e) or "No such file or directory" in str(e):
    #              logger.error("🆘 폰트 파일을 찾을 수 없습니다. Dockerfile에 폰트가 올바르게 설치되었는지, FONT_PATH가 정확한지 확인하세요.")
    #         return "" # 또는 에러 처리에 맞는 값 반환