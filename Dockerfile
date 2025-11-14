FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# Python 경로 설정
ENV PYTHONPATH=/app/src

# 포트 노출 (Week6: FastAPI, Week7: Dash)
EXPOSE 8000 8050

# 기본 엔트리포인트
ENTRYPOINT ["python"]

# 기본 명령어 (Week6 API 서버)
CMD ["src/week6/run_week6.py"]
