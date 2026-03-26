#!/bin/bash

# 1. 기존 컨테이너 및 이미지 정리 (더 확실하게!) 🎖️
echo "♻️  Cleaning up old containers and images..."
sudo docker stop sixsense-final-test 2>/dev/null
sudo docker rm sixsense-final-test 2>/dev/null
# 기존 이미지를 삭제해서 빌드를 강제합니다. 🕵️
sudo docker rmi doc-converter:latest 2>/dev/null

# 2. 도커 이미지 빌드 (캐시 무시 옵션 필수!) 🚀
echo "📦 Building Docker image WITHOUT CACHE..."
sudo docker build --no-cache -t doc-converter:latest .

# 3. 환경 변수 파일(.env)을 로드하여 컨테이너 실행
echo "🚀 Starting container with S3 credentials..."
sudo docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name sixsense-final-test \
  doc-converter:latest

# 4. 로그 실시간 확인
echo "📋 Showing real-time logs..."
sudo docker logs -f sixsense-final-test
