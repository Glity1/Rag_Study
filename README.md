# 🎓 RAG Study - 7주차 RAG 파이프라인 학습 프로젝트

> LangChain, LangGraph, FastAPI, Dash를 활용한 완전한 RAG 시스템 구현

Retrieval-Augmented Generation(RAG) 워크플로를 7주차 커리큘럼으로 단계화한 학습입니다.  
각 주차의 `run_weekX.py` 스크립트를 순서대로 실행하면 **PDF 추출 → 청킹 → 임베딩 → 인덱스 → RAG 서비스 → UI** 까지 파이프라인을 완성할 수 있습니다.

## 🚀 빠른 시작 (Quick Start)

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/rag-study.git
cd rag-study

# 2. 가상환경 생성 및 패키지 설치
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. 환경 변수 설정
# .env 파일 생성 후 GOOGLE_API_KEY=your_key 추가

# 4. 실행 (Week2부터 시작)
python src/week2/run_week2.py
```

## 📚 학습 커리큘럼

| 주차 | 내용 | 실행 명령 | 핵심 파일 |
|------|------|----------|----------|
| **Week1** | RAG 개념 학습 | `python src/week1/week1_hands_on.py` | `week1_hands_on.py` |
| **Week2** | PDF 전처리 & 청킹 | `python src/week2/run_week2.py` | `pdf_loader.py`, `chunking_pipeline.py` |
| **Week3** | 임베딩 & 벡터 인덱스 | `python src/week3/run_week3.py` | `embedding_pipeline.py`, `vector_store_builder.py` |
| **Week4** | RAG 체인 구성 ⭐ | `python src/week4/run_week4.py` | `rag_chain.py` (핵심 모듈) |
| **Week5** | 프롬프트 튜닝 + LangGraph | `python src/week5/run_week5.py` | `prompt_tuning.py`, `langgraph_rag.py` |
| **Week6** | FastAPI 서버 | `python src/week6/run_week6.py` | `api_server.py` |
| **Week7** | Dash UI | `python src/week7/run_week7.py` | `dash_app.py` |

> ⭐ Week4의 `rag_chain.py`가 다른 주차(Week5, Week6)에서 재사용되는 핵심 모듈입니다.

## ✨ 주요 기능

- 📄 **PDF 전처리**: 다양한 청킹 전략 + 이미지 플레이스홀더 자동 삽입 (필요 시 활성화)
- 🔍 **벡터 검색**: FAISS 기반 고속 유사도 검색, MMR(Maximal Marginal Relevance) 옵션 지원
- 🤖 **RAG 체인**: LangChain RetrievalQA + LangGraph StateGraph (조건부 분기/재검색/키워드 분기)
- 🎨 **프롬프트 튜닝**: PromptVariant 비교, LLM 파라미터(`temperature`, `top_p`, `top_k`) 튜닝
- 🌐 **API 서버**: FastAPI 기반 REST API (`POST /query`)
- 💻 **웹 UI**: Dash 기반 인터랙티브 질의응답 인터페이스
- 🐳 **Docker 지원**: Docker Compose로 전체 파이프라인 실행
- 🧪 **자동 테스트**: `scripts/test_new_features.py`로 핵심 기능 일괄 검증 (JSON 저장)

## 🧪 실제 실행 결과 (2024-11-14)

| 테스트 | 설정 | 응답 시간 | 비고 |
|--------|------|-----------|------|
| **MMR vs 유사도** | 질문: GKL 코로나 전략, k=5 | 유사도 11.70초 / MMR 11.11초 | MMR 답변 길이 824자 (−530자) |
| **LLM 파라미터** | temperature/top_p/top_k 조합 5종 | 9.58~11.34초 | temperature=0.0이 가장 빠름 |
| **LangGraph 조건부 분기** | 재검색 임계값 0.3 | 기본 10.97초 / 조건부 12.15초 | 재검색 1회, 키워드 없음 |

- 테스트 스크립트: `python scripts/test_new_features.py`
- 결과 JSON: `outputs/feature_tests/test_results_1763105331.json`
- 자세한 리포트: `docs/ACTUAL_EXECUTION_RESULTS.md`
- 가이드 문서 반영: `docs/guides/MMR_SEARCH_GUIDE.md`, `docs/guides/LLM_PARAMETERS_GUIDE.md`, `docs/guides/LANGGRAPH_CONDITIONAL_BRANCHING.md`

## 🏗️ 프로젝트 구조

```
rag-study/
├── src/                    # 주차별 소스 코드
│   ├── week1/             # RAG 개념 학습
│   ├── week2/             # PDF 전처리 & 청킹
│   ├── week3/             # 임베딩 & 벡터 인덱스
│   ├── week4/             # RAG 체인 구성 ⭐ 핵심
│   ├── week5/             # 프롬프트 튜닝 + LangGraph
│   ├── week6/             # FastAPI 서버
│   └── week7/             # Dash UI
│
├── conf/                   # Hydra 설정 파일
│   └── week*.yaml
│
├── docs/                   # 문서
│   ├── general/           # 아키텍처, 비교 분석
│   ├── reports/           # 주차별 보고서
│   └── workflows/         # 순서도
│
├── notebooks/             # 학습 노트
│   └── week*/
│
├── data/                   # 데이터 (샘플 포함)
│   ├── raw/               # 원본 PDF (샘플)
│   └── processed/         # 전처리 결과 (샘플 인덱스)
│
├── README.md              # 프로젝트 소개
├── README_DOCKER.md       # Docker 사용 가이드
├── requirements.txt       # Python 의존성
├── environment.yml        # Conda 환경
├── Dockerfile             # Docker 이미지
└── docker-compose.yml     # Docker Compose 설정
```

각 주차는 이전 주차의 결과물을 사용합니다: Week2 → Week3 → Week4 → Week5/Week6 → Week7

## 📖 상세 문서

- 🗂️ [문서 인덱스](docs/README.md) - guides/results/notes/reports 구조 안내
- 📐 [프로젝트 아키텍처](docs/guides/ARCHITECTURE.md) - 주차별 연관관계 및 의존성
- 🔄 [LangChain vs LangGraph](docs/guides/LANGCHAIN_VS_LANGGRAPH.md) - 비교 분석 및 사용 가이드
- 📊 [작업 흐름 순서도](docs/guides/LANGCHAIN_LANGGRAPH_WORKFLOWS.md) - 일반적인 워크플로우 패턴
- 🐳 [Docker 사용 가이드](README_DOCKER.md) - Docker Compose 실행 방법

---

## 1. 프로젝트 구조

- `src/week1` ~ `src/week7` : 주차별 핵심 코드
- `src/misc` : 실험/보조 스크립트
- `data/raw` : 원본 PDF
- `data/processed` : 전처리/임베딩/인덱스 결과
- `docs/guides` : 아키텍처/기능/가이드 문서
- `docs/results` : 커리큘럼 점검, 실제 실행 결과, 구현 요약
- `docs/notes` : 주차별 연구 노트(구노 업로드용 포함)
- `docs/reports/weekX` : 주간 보고서 템플릿
- `notebooks/weekX` : 학습 메모
- `requirements.txt`, `Dockerfile` 등 : 실행 환경 정의

---

## 2. 환경 준비

1. **가상환경 (권장)**  
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
2. **패키지 설치**  
   ```powershell
   pip install -r requirements.txt
   ```
3. **옵션: Tesseract OCR**  
   스캔본 PDF를 처리하려면 Tesseract 설치 후 경로 등록  
   ```powershell
   setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```
4. **Gemini API 키 설정**  
   ```powershell
   setx GOOGLE_API_KEY "your_google_api_key"
   ```
   또는 프로젝트 루트 `.env` 파일에 `GOOGLE_API_KEY=...` 저장  
   (모든 스크립트가 자동으로 `.env`를 로드합니다.)

---

## 3. Hydra 실행 개요

각 주차 실행 명령은 다음과 같습니다.

```powershell
python src/weekX/run_weekX.py
```

- 기본 설정은 `conf/weekX.yaml`에 정의되어 있습니다.
- 특정 파라미터를 바꾸고 싶으면 Hydra override를 사용합니다. 예:
  ```powershell
python src/week4/run_week4.py rag.model=gemini-2.5-flash rag.top_k=3
python src/week6/run_week6.py server.port=9000 server.host=127.0.0.1
  python src/week7/run_week7.py ui.api_endpoint=http://192.168.0.5:8000/query
  ```
- 모든 실행 시 실제 설정이 YAML 형태로 출력되므로, 적용된 값을 쉽게 확인할 수 있습니다.

### 자동 기능 테스트

- 주요 기능을 일괄 검증하려면 다음 스크립트를 실행하세요.
  ```powershell
  python scripts/test_new_features.py
  ```
- 테스트 내용: MMR vs 유사도, LLM 파라미터 조합, LangGraph 조건부 분기
- 결과는 `outputs/feature_tests/test_results_<timestamp>.json`에 저장되며, 문서(`docs/ACTUAL_EXECUTION_RESULTS.md`)에 반영됩니다.

---

## 4. 주차별 실행 가이드

### Week1 — RAG 기본 개념 체험
- 파일: `src/week1/week1_hands_on.py`
- 실행:
  ```powershell
  python src/week1/week1_hands_on.py
  ```
- 결과: 콘솔 로그 (산출물 없음)

### Week2 — PDF 전처리 & 청킹
- 실행:
  ```powershell
  python src/week2/run_week2.py
  ```
- 기본 설정: `data/raw`의 PDF 전체 처리, OCR ON, 모든 청킹 전략 실행  
- 출력:
  ```
  data/processed/<slug>/
    ├─ extraction.json
    ├─ full_text.txt
    ├─ summary.json
    └─ chunks/<strategy>.{json,txt}
  ```
- `data/processed/latest_week2.json` 포인터가 최신 산출물을 가리킵니다.
- Hydra 예시:
  ```powershell
  python src/week2/run_week2.py pdf.inputs="[data/raw/파일1.pdf,data/raw/파일2.pdf]" \
      chunking.strategies='["recursive","fixed"]' pdf.enable_ocr=false
  ```

### Week3 — 임베딩 & 벡터 인덱스
- 실행:
  ```powershell
  python src/week3/run_week3.py
  ```
- Week2 산출물(`chunks/*.json`)을 읽어 SentenceTransformer 임베딩 생성 후  
  `data/processed/index/<slug>/<strategy>/index.faiss` 등을 저장합니다.
- Hydra 예시:
  ```powershell
  python src/week3/run_week3.py input.strategies='["recursive","semantic"]' \
      vector_store.base_dir=data/processed/index/custom
  ```

### Week4 — RAG 체인 구성 & 평가
- 실행:
  ```powershell
  python src/week4/run_week4.py
  ```
- 모든 인덱스를 순회하며 Gemini 기반 QA 실행,  
  필요 시 `evaluation.validation_path`에 검증 세트를 지정해 Recall@K 계산.
- Hydra 예시:
  ```powershell
  python src/week4/run_week4.py rag.model=gemini-2.5-flash evaluation.validation_path=data/eval/validation.json
  ```
- FastAPI 로그와 동일하게 콘솔에 답변/평가 결과가 출력됩니다.

### Week5 — 프롬프트 튜닝
- 실행:
  ```powershell
  python src/week5/run_week5.py
  ```
- `prompt_tuning.py`에 정의된 여러 PromptVariant를 Gemini로 실행하여 비교합니다.
- 저장하려면:
  ```powershell
  python src/week5/run_week5.py output.save_path=data/processed/week5_report.txt
  ```

### Week6 — FastAPI RAG 서비스
- 실행:
  ```powershell
  python src/week6/run_week6.py
  ```
- Hydra가 인덱스 경로를 자동 탐색하여 FastAPI 서버(기본 `localhost:8000`)를 띄웁니다.
- 엔드포인트: `POST /query`
  ```bash
  curl -X POST http://localhost:8000/query \
       -H "Content-Type: application/json" \
       -d '{"question": "LangChain RAG 파이프라인을 요약해줘", "top_k": 5}'
  ```
- 설정 예:
  ```powershell
  python src/week6/run_week6.py server.port=9000 rag.model_name=gemini-2.5-flash
  ```

### Week7 — Dash UI
- 실행:
  ```powershell
  python src/week7/run_week7.py
  ```
- FastAPI 서버가 기동 중이어야 합니다. 기본 주소는 `http://localhost:8000/query`.
- 브라우저에서 `http://localhost:8050` 접속 → 질문 입력 → FastAPI를 통해 답변 표시
- Swagger UI(`http://localhost:8000/docs`)를 사용하면 API 응답을 직접 체크할 수 있습니다.
- 설정 예:
  ```powershell
  python src/week7/run_week7.py ui.port=9001 ui.api_endpoint=http://127.0.0.1:9000/query
  ```

---

## 5. 전체 워크플로 요약

1. **PDF 배치** : `data/raw`에 문서 복사  
2. **전처리 & 청킹 (Week2)** : `python src/week2/run_week2.py`  
3. **임베딩 & 인덱스 (Week3)** : `python src/week3/run_week3.py`  
4. **RAG 체인 & 평가 (Week4)** : `python src/week4/run_week4.py`  
5. **프롬프트 실험 (Week5)** : `python src/week5/run_week5.py`  
6. **API 서비스 (Week6)** : `python src/week6/run_week6.py`  
7. **Dash UI (Week7)** : `python src/week7/run_week7.py`

각 스크립트는 이전 주차의 산출물을 자동으로 탐색하도록 설계되어 있으며, 최신 실행 경로는 포인터(`latest_week2.json`)와 인덱스 디렉터리 구조로 이어집니다.

---

## 6. Docker & Compose 실행

### 6.1 이미지 빌드
```powershell
docker build -t rag-study .
```

### 6.2 FastAPI 서버 실행 (Week6)
```powershell
docker run --rm -it ^
  -p 8000:8000 ^
  -e GOOGLE_API_KEY="your_google_api_key" ^
  -v C:\경로\to\Rag_Study\data:/app/data ^
  rag-study
```
- 기본 CMD: `python src/week6/run_week6.py`
- `http://localhost:8000/docs`에서 `POST /query` 테스트 가능
- 다른 설정은 Hydra override로 변경
  ```powershell
  docker run --rm -it -p 8000:9000 rag-study \
    src/week6/run_week6.py server.port=9000 server.host=0.0.0.0
  ```

### 6.3 다른 주차 실행
`ENTRYPOINT ["python"]`이므로 명령만 바꿔 실행할 수 있습니다.
```powershell
docker run --rm -it rag-study src/week2/run_week2.py
docker run --rm -it rag-study src/week3/run_week3.py input.latest_only=true
docker run --rm -it rag-study src/week5/run_week5.py output.save_path=/app/data/week5_report.txt
```

- 산출물을 호스트에서 보려면 `/app/data`를 마운트하세요.
- Dash UI(Week7)를 컨테이너로 실행하려면 FastAPI가 먼저 기동되어 있어야 하며 포트를 추가로 개방합니다.
  ```powershell
  docker run --rm -it ^
    -p 8050:8050 ^
    -e GOOGLE_API_KEY="..." ^
    -v C:\경로\to\Rag_Study\data:/app/data ^
    rag-study src/week7/run_week7.py ui.api_endpoint=http://host.docker.internal:8000/query
  ```
  Windows/맥에서는 `host.docker.internal`이 호스트 주소를 가리킵니다. Linux라면 호스트 IP를 직접 적어 주세요.

- `ENTRYPOINT ["python"]` 덕분에 다른 주차도 명령만 바꿔 실행할 수 있습니다.
  ```powershell
  docker run --rm -it rag-study src/week3/run_week3.py input.latest_only=true
  docker run --rm -it rag-study src/week5/run_week5.py output.save_path=/app/data/week5_report.txt
  ```

### 6.4 docker compose로 전체 관리
- 루트의 `docker-compose.yml`에는 Week1~Week7 서비스가 선언돼 있습니다.
- 공통 이미지를 먼저 빌드합니다.
  ```powershell
  docker compose build
  ```
- 프로필 기반 실행(Compose v2 이상):
  ```powershell
  # 개별 주차 실행
  docker compose --profile week5 up
  
  # Week6와 Week7 동시 실행 (권장)
  docker compose --profile full up
  ```
- 백그라운드 실행:
  ```powershell
  docker compose --profile full up -d
  ```
- 상태 확인 및 종료:
  ```powershell
  docker compose ps
  docker compose --profile full down
  ```
- Week7 서비스는 자동으로 Week6 컨테이너(`http://week6:8000/query`)와 통신하므로, `docker compose --profile full up`만 실행하면 FastAPI API와 Dash UI가 동시에 기동됩니다.
- 자세한 내용은 `README_DOCKER.md`를 참조하세요.

---

## 7. 업로드/공유 시 주의사항

- `data/raw`는 용량이 크다면 샘플만 포함하고 사용법을 문서로 안내합니다.
- `__pycache__`, 로그, 임시 파일 삭제 후 공유합니다.
- `.env`와 `GOOGLE_API_KEY` 등 민감 정보는 절대 저장소에 포함하지 마세요.

---

이 README에 따라 순차적으로 실행하면 Week7까지의 RAG 학습 파이프라인을 무리 없이 재현할 수 있습니다.  
Hydra 설정을 적극 활용하면 각 주차별 파라미터를 쉽게 변형하거나 실험을 자동화할 수 있습니다.
