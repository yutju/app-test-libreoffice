import os
import subprocess
import logging
import time
import shutil
from PIL import Image

logger = logging.getLogger("SixSense-Converter")


def run_libreoffice_convert(input_file, outdir, env):
    cmd = [
        "xvfb-run",
        "-a",
        "--server-args=-screen 0 1920x1080x24",
        "libreoffice",
        "--headless",
        "--invisible",
        "--nodefault",
        "--nofirststartwizard",
        "--nolockcheck",
        "--nologo",
        "--norestore",
        "--convert-to",
        "pdf:writer_pdf_Export:SelectPdfVersion=1;EmbedStandardFonts=true",
        "--outdir",
        outdir,
        input_file
    ]

    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        logger.error("=== PDF 변환 실패 ===")
        logger.error(result.stdout)
        logger.error(result.stderr)
        raise RuntimeError("LibreOffice PDF 변환 실패")


def run_hwp_to_docx(input_file, outdir, env):
    cmd = [
        "xvfb-run",
        "-a",
        "--server-args=-screen 0 1920x1080x24",
        "libreoffice",
        "--headless",
        "--invisible",
        "--nodefault",
        "--nofirststartwizard",
        "--nolockcheck",
        "--nologo",
        "--norestore",
        "--convert-to",
        "docx",
        "--outdir",
        outdir,
        input_file
    ]

    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        logger.error("=== HWP → DOCX 변환 실패 ===")
        logger.error(result.stdout)
        logger.error(result.stderr)
        raise RuntimeError("HWP → DOCX 변환 실패")


def process_conversion(input_path, output_path, ext, temp_dir):
    try:
        # ✅ 1. 이미지 변환
        if ext in ["png", "jpg", "jpeg", "bmp"]:
            with Image.open(input_path) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(output_path, "PDF")
            return

        # ✅ 2. 문서 변환
        elif ext in ["txt", "docx", "hwp"]:
            abs_temp_dir = os.path.abspath(temp_dir)
            ts = int(time.time() * 1000)

            safe_input = os.path.join(abs_temp_dir, f"input_{ts}.{ext}")
            shutil.copy2(input_path, safe_input)

            profile_dir = os.path.join(abs_temp_dir, f"profile_{ts}")
            os.makedirs(profile_dir, exist_ok=True)

            env = os.environ.copy()
            env["HOME"] = profile_dir
            env["LANG"] = "ko_KR.UTF-8"
            env["LC_ALL"] = "ko_KR.UTF-8"
            env["DISPLAY"] = ":99"

            # ✅ TXT 인코딩 보정
            if ext == "txt":
                with open(safe_input, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                with open(safe_input, "w", encoding="utf-8") as f:
                    f.write(content)

            # ✅ HWP 처리 (🔥 핵심 개선)
            if ext == "hwp":
                logger.info("HWP → PDF 직접 변환 시도")

                try:
                    # 1차: 바로 PDF 변환
                    run_libreoffice_convert(safe_input, abs_temp_dir, env)

                except Exception as e:
                    logger.warning(f"직접 PDF 변환 실패: {e}")
                    logger.info("HWP → DOCX → PDF fallback 시도")

                    # 2차: DOCX 변환
                    run_hwp_to_docx(safe_input, abs_temp_dir, env)

                    docx_path = safe_input.replace(".hwp", ".docx")

                    if not os.path.exists(docx_path):
                        raise RuntimeError("HWP 변환 완전 실패 (DOCX 생성 안됨)")

                    safe_input = docx_path

                    # DOCX → PDF
                    run_libreoffice_convert(safe_input, abs_temp_dir, env)

            else:
                # DOCX / TXT → PDF
                run_libreoffice_convert(safe_input, abs_temp_dir, env)

            # ✅ PDF 결과 처리
            pdf_name = os.path.basename(safe_input).rsplit(".", 1)[0] + ".pdf"
            generated_pdf = os.path.join(abs_temp_dir, pdf_name)

            for _ in range(20):
                if os.path.exists(generated_pdf) and os.path.getsize(generated_pdf) > 0:
                    time.sleep(1)
                    shutil.move(generated_pdf, output_path)
                    logger.info(f"변환 성공: {output_path}")
                    return
                time.sleep(1)

            raise FileNotFoundError("PDF 생성 실패")

        else:
            raise ValueError("지원하지 않는 형식")

    except Exception as e:
        logger.error(f"Conversion Error: {str(e)}")
        raise e

    finally:
        # ✅ 임시파일 정리
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except:
            pass
