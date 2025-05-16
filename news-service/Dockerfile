# Python 3.12.7-slim 이미지 사용
FROM python:3.12.7-slim

WORKDIR /app

# apt-get install 중 프롬프트를 피하기 위해 DEBIAN_FRONTEND 설정
ENV DEBIAN_FRONTEND=noninteractive

# --- Chrome/ChromeDriver 설치 ---
# Chrome for Testing 버전 정의
# 최신 안정 버전은 https://googlechromelabs.github.io/chrome-for-testing/ 에서 확인하세요.
# 예시: 최근 버전 사용 (최신 안정 버전이 있다면 업데이트하세요)
ENV CHROME_VERSION="136.0.7103.114"

# Chrome 및 ChromeDriver 다운로드/설치를 위한 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chrome 실행에 필요한 핵심 라이브러리들
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libexpat1 \
    libgbm1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libasound2 \
    # 다운로드 및 압축 해제 도구
    wget \
    unzip \
    ca-certificates \
    # 기존 Dockerfile의 의존성
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    git \
    fontconfig \
    fonts-nanum \
    build-essential \
 && fc-cache -fv

# Google Chrome for Testing (브라우저) 설치
RUN echo "Installing Chrome for Testing version: ${CHROME_VERSION}" \
 && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip" -O chrome-linux64.zip \
 && unzip -q chrome-linux64.zip -d /opt \
 && rm chrome-linux64.zip \
 && ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome \
 && google-chrome --version # 설치 확인

# 일치하는 ChromeDriver for Testing 설치
RUN echo "Installing ChromeDriver for Testing version: ${CHROME_VERSION}" \
 && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O chromedriver-linux64.zip \
 && unzip -q chromedriver-linux64.zip -d /opt \
 && rm chromedriver-linux64.zip \
 && ln -s /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
 && chmod +x /usr/bin/chromedriver \
 && chromedriver --version # 설치 확인
# --- Chrome/ChromeDriver 설치 종료 ---

# 1단계: pip를 최신 버전으로 업그레이드
RUN python -m pip install --upgrade pip

# 2단계: 업그레이드된 pip를 사용하여 setuptools와 wheel을 최신 버전으로 설치/업그레이드
RUN python -m pip install --upgrade setuptools wheel

# 3단계: requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt --verbose

COPY . .

# 이미지 크기를 줄이기 위해 apt 캐시 정리
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]