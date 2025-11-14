# Docker 사용 가이드

이 문서는 Rag_Study 프로젝트를 Docker와 Docker Compose로 실행하는 방법을 설명합니다.

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [Dockerfile 개요](#dockerfile-개요)
3. [Docker Compose 사용법](#docker-compose-사용법)
4. [주차별 실행](#주차별-실행)
5. [환경 변수 설정](#환경-변수-설정)
6. [볼륨 마운트](#볼륨-마운트)
7. [문제 해결](#문제-해결)

---

## 사전 준비

### 1. Docker 설치 확인

```bash
docker --version
docker-compose --version
```

### 2. 환경 변수 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 API 키를 설정합니다:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

---

## Dockerfile 개요

### 기본 구조

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python"]
CMD ["src/week6/run_week6.py"]
```

### 주요 특징

- **Python 3.11-slim** 기반 이미지
- **Tesseract OCR** 지원 (스캔본 PDF 처리용)
- **PYTHONPATH** 설정으로 모듈 import 자동 해결
- **ENTRYPOINT**로 모든 주차 스크립트 실행 가능

---

## Docker Compose 사용법

### 전체 서비스 구조

```yaml
services:
  week1-week5:  # 데이터 처리 주차
  week6:        # FastAPI 서버 (포트 8000)
  week7:         # Dash UI (포트 8050)
```

### Week6와 Week7 동시 실행 (권장)

#### 방법 1: Full Profile 사용

```bash
# Week6와 Week7을 동시에 실행
docker-compose --profile full up

# 백그라운드 실행
docker-compose --profile full up -d

# 로그 확인
docker-compose logs -f week6 week7

# 중지
docker-compose --profile full down
```

#### 방법 2: 개별 Profile 지정

```bash
# Week6와 Week7을 동시에 실행
docker-compose --profile week6 --profile week7 up

# 백그라운드 실행
docker-compose --profile week6 --profile week7 up -d
```

### 개별 서비스 실행

```bash
# Week6만 실행 (FastAPI 서버)
docker-compose --profile week6 up week6

# Week7만 실행 (Dash UI, Week6가 먼저 실행되어야 함)
docker-compose --profile week7 up week7

# Week2 실행 (PDF 전처리)
docker-compose --profile week2 up week2

# Week3 실행 (임베딩 & 인덱스)
docker-compose --profile week3 up week3
```

---

## 주차별 실행

### Week1: RAG 개념 학습

```bash
docker-compose --profile week1 up week1
```

### Week2: PDF 전처리 & 청킹

```bash
docker-compose --profile week2 up week2
```

**볼륨 마운트**: `./data:/app/data` (입력 PDF와 출력 결과 저장)

### Week3: 임베딩 & 벡터 인덱스

```bash
docker-compose --profile week3 up week3
```

**의존성**: Week2 완료 후 실행

### Week4: RAG 체인 구성

```bash
docker-compose --profile week4 up week4
```

**의존성**: Week3 완료 후 실행

### Week5: 프롬프트 튜닝 & LangGraph

```bash
docker-compose --profile week5 up week5
```

**주요 기능**:
- 프롬프트 튜닝 실험
- LangGraph 조건부 분기 데모
- LLM 파라미터 조율 (`temperature`, `top_p`, `top_k`)

**설정 예시**:
```bash
docker-compose --profile week5 up week5 \
  --env-file .env \
  -e "langgraph.enable_conditional_branching=true"
```

### Week6: FastAPI 서버

```bash
# 기본 실행
docker-compose --profile week6 up week6

# 포트 변경
docker-compose --profile week6 up week6 \
  -e "server.port=9000"
```

**접속 주소**:
- API 서버: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

**주요 기능**:
- MMR 검색 지원 (`use_mmr=true`)
- LLM 파라미터 조율 (`temperature`, `top_p`, `top_k`)
- 인덱스 자동 탐색

### Week7: Dash UI

```bash
# Week6와 함께 실행 (권장)
docker-compose --profile full up

# 단독 실행 (Week6가 별도로 실행 중이어야 함)
docker-compose --profile week7 up week7
```

**접속 주소**: http://localhost:8050

**주의**: Week6 API 서버가 먼저 실행되어 있어야 합니다!

---

## 환경 변수 설정

### .env 파일 사용

```bash
# .env 파일 생성
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
EOF

# Docker Compose에서 자동 로드
docker-compose --profile full up
```

### 환경 변수 직접 전달

```bash
docker run --rm -it \
  -e GOOGLE_API_KEY="your_key" \
  -p 8000:8000 \
  rag-study
```

---

## 볼륨 마운트

### 기본 볼륨 설정

`docker-compose.yml`에서 다음 볼륨이 자동으로 마운트됩니다:

```yaml
volumes:
  - ./data:/app/data          # 데이터 (입력/출력)
  - ./conf:/app/conf          # Hydra 설정 파일
  - ./outputs:/app/outputs    # 실행 로그
```

### 데이터 구조

```
data/
├── raw/              # 입력 PDF 파일
└── processed/        # 처리 결과
    ├── index/        # 벡터 인덱스
    └── chunks/       # 청킹 결과
```

---

## 문제 해결

### 1. 포트 충돌

```bash
# 포트가 이미 사용 중인 경우
# docker-compose.yml에서 포트 변경 또는
# 기존 컨테이너 중지

docker-compose down
docker ps  # 실행 중인 컨테이너 확인
docker stop <container_id>
```

### 2. API 키 오류

```bash
# .env 파일 확인
cat .env

# 환경 변수 확인
docker-compose config | grep GOOGLE_API_KEY
```

### 3. 인덱스 파일을 찾을 수 없음

```bash
# Week3를 먼저 실행하여 인덱스 생성
docker-compose --profile week3 up week3

# 인덱스 확인
ls -la data/processed/index/*/recursive/metadata.json
```

### 4. 연결 거부 오류 (Week7)

```bash
# Week6가 실행 중인지 확인
docker-compose ps

# Week6 로그 확인
docker-compose logs week6

# Week6와 Week7을 함께 실행 (권장)
docker-compose --profile full up
```

### 5. 이미지 재빌드

```bash
# 이미지 강제 재빌드
docker-compose build --no-cache

# 특정 서비스만 재빌드
docker-compose build week6
```

---

## 유용한 명령어

### 이미지 관리

```bash
# 이미지 빌드
docker-compose build

# 이미지 확인
docker images | grep rag-study

# 이미지 삭제
docker rmi rag-study
```

### 컨테이너 관리

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 컨테이너 로그 확인
docker-compose logs -f week6
docker-compose logs -f week7

# 컨테이너 재시작
docker-compose restart week6

# 컨테이너 중지 및 제거
docker-compose down

# 볼륨까지 함께 제거
docker-compose down -v
```

### 디버깅

```bash
# 컨테이너 내부 접속
docker-compose exec week6 bash

# Python 경로 확인
docker-compose exec week6 python -c "import sys; print(sys.path)"

# 환경 변수 확인
docker-compose exec week6 env | grep GOOGLE
```

---

## 고급 사용법

### Hydra Override와 함께 사용

```bash
# Docker Compose에서 Hydra 설정 오버라이드
docker-compose run --rm week5 \
  src/week5/run_week5.py \
  langgraph.enable_conditional_branching=true \
  llm.temperature=0.7
```

### 커스텀 네트워크

```bash
# 네트워크 생성
docker network create rag-network

# 네트워크 사용
docker-compose --profile full up --network rag-network
```

### 리소스 제한

`docker-compose.yml`에 리소스 제한 추가:

```yaml
services:
  week6:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 접속 주소 요약

| 서비스 | 주소 | 설명 |
|--------|------|------|
| Week6 API | http://localhost:8000 | FastAPI 서버 |
| Week6 Swagger | http://localhost:8000/docs | API 문서 |
| Week7 Dash UI | http://localhost:8050 | 웹 인터페이스 |

---

## 참고 문서

- [프로젝트 아키텍처](docs/guides/ARCHITECTURE.md)
- [LangChain vs LangGraph](docs/guides/LANGCHAIN_VS_LANGGRAPH.md)
- [MMR 검색 가이드](docs/guides/MMR_SEARCH_GUIDE.md)
- [LangGraph 조건부 분기](docs/guides/LANGGRAPH_CONDITIONAL_BRANCHING.md)
- [LLM 파라미터 가이드](docs/guides/LLM_PARAMETERS_GUIDE.md)

---

## 요약

### 빠른 시작

```bash
# 1. 이미지 빌드
docker-compose build

# 2. Week6와 Week7 동시 실행
docker-compose --profile full up

# 3. 접속
# - API: http://localhost:8000/docs
# - UI: http://localhost:8050
```

### 주요 명령어

```bash
# 실행
docker-compose --profile full up

# 백그라운드 실행
docker-compose --profile full up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose --profile full down
```

이 가이드를 따라 Docker 환경에서 Rag_Study 프로젝트를 실행할 수 있습니다! 🐳
