FROM python:3.10-bookworm

# 🌏 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=ko_KR.UTF-8
ENV LC_ALL=ko_KR.UTF-8
ENV LANGUAGE=ko_KR:ko
ENV TZ=Asia/Seoul
ENV HOME=/tmp
ENV SAL_USE_VCLPLUGIN=gen
ENV DISPLAY=:99

# 🛠️ 시스템 패키지 설치 (🔥 최적 + 폰트 + xauth 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    xvfb \
    xauth \
    x11-xserver-utils \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-math \
    libreoffice-java-common \
    fonts-nanum \
    fonts-noto-cjk \
    fonts-dejavu \
    fonts-opensymbol \
    fonts-symbola \
    fonts-unifont \
    fonts-noto-color-emoji \
    default-jre \
    tzdata \
    && locale-gen ko_KR.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 👤 비루트 사용자 생성
RUN groupadd -r appgroup && useradd -r -g appgroup -m -u 1000 appuser

# 📁 작업 디렉토리
WORKDIR /app

# 📦 Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 📂 소스 코드 복사
COPY --chown=appuser:appgroup . .

# 🔐 디렉토리 및 로그 권한 설정
RUN mkdir -p /app/temp_storage && \
    touch /app/app.log && \
    chown -R appuser:appgroup /app && \
    chmod 777 /app/temp_storage && \
    chmod 666 /app/app.log

# 👤 실행 사용자
USER appuser

# 🚀 FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
