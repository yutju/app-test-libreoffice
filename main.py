import os
import uuid
import shutil
import logging
import boto3
from typing import Optional, List # 🎖️ List 추가
from botocore.config import Config

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from processor import PDFProcessor
from templates import HTML_CONTENT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SixSense-Converter")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "sixsense-pdf-storage")
s3_client = boto3.client('s3', region_name="ap-northeast-2", config=Config(signature_version='s3v4'))

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_storage")
os.makedirs(TEMP_DIR, exist_ok=True)

def cleanup(path):
    if path and os.path.exists(path):
        if os.path.isfile(path): os.remove(path)
        else: shutil.rmtree(path)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return HTML_CONTENT

# 1. 단일 파일 변환 (기존 유지)
@app.post("/convert-single/")
@limiter.limit("10/minute")
async def convert_single(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    wm_type: str = Form("text"),
    wm_text: Optional[str] = Form("SIX SENSE"),
    wm_image: Optional[UploadFile] = File(None)
):
    ext = file.filename.split(".")[-1].lower()
    file_id = str(uuid.uuid4())
    input_path = os.path.join(TEMP_DIR, f"{file_id}.{ext}")
    output_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")
    wm_image_path = None

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if wm_type == "image" and wm_image and wm_image.filename:
            wm_ext = wm_image.filename.split(".")[-1].lower()
            wm_image_path = os.path.join(TEMP_DIR, f"wm_{file_id}.{wm_ext}")
            with open(wm_image_path, "wb") as wm_buffer:
                shutil.copyfileobj(wm_image.file, wm_buffer)

        # 단일 파일 변환 시에도 새로운 구조의 PDFProcessor 사용 🚀
        proc = PDFProcessor(TEMP_DIR)
        proc.process_merge([input_path], output_path, wm_type, wm_text, wm_image_path)

        s3_key = f"single/{file_id}.pdf"
        s3_client.upload_file(output_path, S3_BUCKET, s3_key)
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': s3_key}, ExpiresIn=300)

        background_tasks.add_task(cleanup, input_path)
        background_tasks.add_task(cleanup, output_path)
        if wm_image_path: background_tasks.add_task(cleanup, wm_image_path)

        return JSONResponse({"download_url": url})
    except Exception as e:
        logger.error(f"Error during single conversion: {e}")
        cleanup(input_path); cleanup(output_path)
        if wm_image_path: cleanup(wm_image_path)
        raise HTTPException(status_code=500, detail=str(e))

# 2. 🚀 다중 파일 병합 (10개 제한 로직 추가) 🎖️
@app.post("/convert-merge/")
@limiter.limit("5/minute")
async def convert_merge(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...), # 🕵️ 파일 리스트로 받기
    wm_type: str = Form("text"),
    wm_text: Optional[str] = Form("SIX SENSE"),
    wm_image: Optional[UploadFile] = File(None)
):
    # --- 🕵️ 보안 및 리소스 제약: 10개 제한 ---
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="최대 10개의 파일까지만 병합 가능합니다.")
    
    merge_id = str(uuid.uuid4())
    input_paths = []
    output_path = os.path.join(TEMP_DIR, f"{merge_id}_merged.pdf")
    wm_image_path = None

    try:
        # 1. 모든 파일 임시 저장
        for file in files:
            ext = file.filename.split(".")[-1].lower()
            path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.{ext}")
            with open(path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            input_paths.append(path)

        # 2. 이미지 워터마크 처리
        if wm_type == "image" and wm_image and wm_image.filename:
            wm_ext = wm_image.filename.split(".")[-1].lower()
            wm_image_path = os.path.join(TEMP_DIR, f"wm_m_{merge_id}.{wm_ext}")
            with open(wm_image_path, "wb") as wm_buffer:
                shutil.copyfileobj(wm_image.file, wm_buffer)

        # 3. 병합 프로세스 실행 🚀
        proc = PDFProcessor(TEMP_DIR)
        proc.process_merge(input_paths, output_path, wm_type, wm_text, wm_image_path)

        # 4. S3 업로드
        s3_key = f"merged/{merge_id}.pdf"
        s3_client.upload_file(output_path, S3_BUCKET, s3_key)
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': s3_key}, ExpiresIn=300)

        # 5. 백그라운드 정리 (입력 파일 리스트 전체 삭제) 🕵️
        for p in input_paths:
            background_tasks.add_task(cleanup, p)
        background_tasks.add_task(cleanup, output_path)
        if wm_image_path:
            background_tasks.add_task(cleanup, wm_image_path)

        return JSONResponse({"download_url": url})

    except Exception as e:
        logger.error(f"Merge Error: {e}")
        for p in input_paths: cleanup(p)
        cleanup(output_path)
        if wm_image_path: cleanup(wm_image_path)
        raise HTTPException(status_code=500, detail=str(e))
