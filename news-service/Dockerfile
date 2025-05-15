# Python 3.12.7-slim 이미지 사용
FROM python:3.12.7-slim

WORKDIR /app

# 시스템 의존성 설치 (기존 목록에 build-essential 추가)
# build-essential은 C/C++ 확장 모듈 컴파일에 필요한 도구 모음입니다.
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    wget \
    git \
    fontconfig \
    fonts-nanum \
    build-essential \
 && fc-cache -fv \
 && rm -rf /var/lib/apt/lists/*

# 1단계: pip를 최신 버전으로 업그레이드
# python -m pip를 사용하여 현재 Docker 이미지의 Python 환경에 맞는 pip를 명시적으로 실행합니다.
RUN python -m pip install --upgrade pip

# 2단계: 업그레이드된 pip를 사용하여 setuptools와 wheel을 최신 버전으로 설치/업그레이드
# Python 3.12에서는 최신 setuptools가 distutils를 포함하고 있으므로 매우 중요합니다.
RUN python -m pip install --upgrade setuptools wheel

# 3단계: requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
# --no-cache-dir 옵션은 Docker 이미지 크기를 줄이는 데 도움이 됩니다.
# --verbose 옵션을 추가하여 설치 과정에 대한 자세한 로그를 볼 수 있습니다 (문제 발생 시 디버깅에 유용).
RUN python -m pip install --no-cache-dir -r requirements.txt --verbose

COPY . .

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]