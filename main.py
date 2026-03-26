# main.py
import os
import uuid
import shutil
import logging
import time
import boto3
from typing import List
from botocore.config import Config
from PyPDF2 import PdfMerger

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from templates import HTML_CONTENT
from converter import process_conversion

# --- [1. 로그 및 S3 설정] ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SixSense-Converter")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "sixsense-pdf-storage-xxxxxx")
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="ap-northeast-2",
    config=Config(signature_version='s3v4')
)

app = FastAPI(title="SixSense Doc-Converter")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

CONVERSION_REQUESTS = Counter('doc_conversion_requests_total', 'Total requests', ['status', 'file_type'])
CONVERSION_DURATION = Histogram('doc_conversion_duration_seconds', 'Processing time', ['file_type'])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_storage")
os.makedirs(TEMP_DIR, exist_ok=True)

# --- [2. 유틸리티 함수] ---
def cleanup_local_path(path: str):
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        logger.info(f"Cleanup success: {path}")
    except Exception as e:
        logger.error(f"Cleanup error {path}: {e}")

def get_s3_presigned_url(object_name: str, expiration=300):
    try:
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': object_name},
            ExpiresIn=expiration
        )
    except Exception as e:
        logger.error(f"S3 URL Generation Error: {e}")
        return None

# --- [3. 엔드포인트] ---

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# --- [기능 1: 단일 파일 변환] ---
@app.post("/convert-single/")
@limiter.limit("10/minute")
async def convert_single(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()

    # 지원 형식 사전 검증
    if ext not in ["hwp", "docx", "txt", "png", "jpg", "jpeg", "bmp"]:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 형식입니다: {ext}")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{file_id}.{ext}")
    output_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")

    start_time = time.time()
    logger.info(f"Single Conversion Started: {file.filename} (id={file_id})")

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        process_conversion(input_path, output_path, ext, TEMP_DIR)

        if not os.path.exists(output_path):
            raise Exception("PDF 변환 엔진 결과물이 없습니다.")

        s3_key = f"single/{file_id}_{file.filename.rsplit('.', 1)[0]}.pdf"
        s3_client.upload_file(output_path, S3_BUCKET, s3_key)

        download_url = get_s3_presigned_url(s3_key)
        if not download_url:
            raise Exception("S3 Presigned URL 생성 실패")

        duration = time.time() - start_time
        CONVERSION_DURATION.labels(file_type=ext).observe(duration)
        CONVERSION_REQUESTS.labels(status='success', file_type=ext).inc()
        logger.info(f"Single Conversion Done: {file.filename} ({duration:.2f}s)")

        background_tasks.add_task(cleanup_local_path, input_path)
        background_tasks.add_task(cleanup_local_path, output_path)

        return JSONResponse({"download_url": download_url})

    except Exception as e:
        CONVERSION_REQUESTS.labels(status='failed', file_type=ext).inc()
        logger.error(f"Single Conversion Failed [{file.filename}]: {e}")
        cleanup_local_path(input_path)
        cleanup_local_path(output_path)
        raise HTTPException(status_code=500, detail=f"변환 실패: {str(e)}")

# --- [기능 2: 다중 파일 병합 변환] ---
@app.post("/convert-merge/")
@limiter.limit("5/minute")
async def convert_merge(request: Request, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="파일을 1개 이상 업로드해주세요.")
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="최대 10개 파일까지만 가능합니다.")

    unique_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, unique_id)
    os.makedirs(job_dir, exist_ok=True)

    merger = PdfMerger()
    start_time = time.time()
    converted_count = 0

    try:
        for file in files:
            ext = file.filename.split(".")[-1].lower()

            if ext not in ["hwp", "docx", "txt", "png", "jpg", "jpeg", "bmp"]:
                logger.warning(f"Unsupported extension skipped: {file.filename}")
                continue

            file_uuid = str(uuid.uuid4())
            # 핵심 수정: 한글/특수문자 파일명 제거, UUID + 확장자만 사용
            input_path = os.path.join(job_dir, f"{file_uuid}.{ext}")
            output_path = os.path.join(job_dir, f"{file_uuid}.pdf")

            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"Processing merge file: {file.filename} -> {file_uuid}.{ext}")

            process_conversion(input_path, output_path, ext, job_dir)

            if os.path.exists(output_path):
                merger.append(output_path)
                converted_count += 1
                logger.info(f"Appended to merger: {file.filename}")
            else:
                logger.error(f"Conversion failed, skipping: {file.filename}")

        if converted_count == 0:
            raise Exception("변환 가능한 파일이 없거나 모든 변환에 실패했습니다.")

        final_filename = f"Merged_{unique_id}.pdf"
        final_path = os.path.join(TEMP_DIR, final_filename)
        merger.write(final_path)
        merger.close()

        s3_key = f"merged/{final_filename}"
        s3_client.upload_file(final_path, S3_BUCKET, s3_key)

        download_url = get_s3_presigned_url(s3_key)
        if not download_url:
            raise Exception("S3 Presigned URL 생성 실패")

        duration = time.time() - start_time
        CONVERSION_DURATION.labels(file_type="merged").observe(duration)
        CONVERSION_REQUESTS.labels(status='success', file_type="merged").inc()
        logger.info(f"Merge Done: {converted_count}개 파일 ({duration:.2f}s)")

        background_tasks.add_task(cleanup_local_path, job_dir)
        background_tasks.add_task(cleanup_local_path, final_path)

        return JSONResponse({
            "download_url": download_url,
            "merged_count": converted_count
        })

    except Exception as e:
        CONVERSION_REQUESTS.labels(status='failed', file_type="merged").inc()
        logger.error(f"Merge Job Failed: {e}")
        merger.close()
        background_tasks.add_task(cleanup_local_path, job_dir)
        raise HTTPException(status_code=500, detail=f"병합 실패: {str(e)}")
