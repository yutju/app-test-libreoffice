# 1단계: 베이스 이미지 (안정적인 Python 3.10-slim)
FROM python:3.10-slim

# 2단계: 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=ko_KR.UTF-8
# [추가] K3s 파드 내부 로그 시간대를 한국 시간으로 맞추기 위해 필수
ENV TZ=Asia/Seoul

# 3단계: 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-nanum \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4단계: 비루트(Non-root) 전용 그룹 및 유저 생성
RUN groupadd -r appgroup && useradd -r -g appgroup -m -u 1000 appuser

WORKDIR /app

# 5단계: 파이썬 패키지 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6단계: 소스 복사 및 권한 설정
# [핵심 수정] COPY 이후 RUN chown을 쓰면 이미지 레이어 용량이 2배가 됩니다.
# COPY 명령어 자체에 --chown 옵션을 주어 용량 뻥튀기를 원천 차단합니다.
COPY --chown=appuser:appgroup . .

# [추가] temp_storage 폴더 생성 및 권한 명시
RUN mkdir -p /app/temp_storage && chmod 755 /app/temp_storage

# 7단계: 컨테이너 실행 유저 전환 (Zero-Trust)
USER appuser

# 8단계: 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
