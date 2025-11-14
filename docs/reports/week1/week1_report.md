# 📊 1주차 학습 결과 리포트

**작성일**: 2025년 11월 7일  
**주제**: RAG 기반 Q&A 시스템 개발 - 1주차  
**학습 주제**: 프로젝트 기획 및 RAG의 이해

---

## 🎯 학습 목표 달성도

✅ RAG 아키텍처의 전체 그림 이해  
✅ 벡터 DB, 임베딩, LLM의 핵심 개념 학습  
✅ RAG 시스템의 작동 원리 파악  
✅ 개발 환경 구축 계획 수립  

---

## 📚 RAG 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                  RAG 시스템 전체 구조                      │
└─────────────────────────────────────────────────────────┘

[사전 작업: Indexing (색인)]
PDF 문서 → 청킹(분할) → 임베딩(벡터화) → 벡터 DB 저장

[실시간 처리: Retrieval (검색)]
사용자 질문 → 질문 벡터화 → 유사도 검색 → 관련 문서 추출

[실시간 처리: Generation (생성)]
검색된 문서 + 질문 → LLM 처리 → 근거 기반 답변
```

---

## 🔑 핵심 개념 정리

### 1. RAG (Retrieval-Augmented Generation)

**정의**: 외부 문서 검색을 통해 LLM의 답변을 강화하는 기술

**필요성**:
- ❌ 순수 LLM의 한계: 최신 정보 부족, 도메인 특화 지식 결여, 환각 문제
- ✅ RAG의 장점: 근거 기반 답변, 최신 정보 활용, 검증 가능성

**작동 원리**:
1. **Indexing**: 문서를 벡터로 변환하여 DB에 저장
2. **Retrieval**: 질문과 유사한 문서 조각을 검색
3. **Generation**: 검색된 문서를 근거로 답변 생성

---

### 2. 벡터 DB (Vector Database)

**정의**: 유사도 검색에 최적화된 특수 데이터베이스

**작동 원리**:
- 텍스트를 고차원 벡터로 저장
- 코사인 유사도, 유클리드 거리 등으로 유사도 계산
- ANN(Approximate Nearest Neighbor) 알고리즘으로 빠른 검색

**주요 선택지**:
|    DB     |     타입    |       장점      |    추천 용도   |
|-----------|-------------|----------------|---------------|
| FAISS     | In-memory  | 빠름, 무료       | 개발/테스트     |
| ChromaDB  | 로컬        | 쉬운 설치, 영속성 | 소규모 프로젝트 |
| Pinecone  | 클라우드    | 관리 불필요       | 프로덕션       |

**프로젝트 선택**: FAISS (초기 개발용)

---

### 3. 임베딩 (Embedding)

**정의**: 텍스트를 숫자 벡터로 변환하는 과정

**핵심 원리**:
- 의미가 비슷한 텍스트 → 벡터 공간에서 가까운 위치
- 수백~수천 차원의 벡터로 표현
- 사전 학습된 모델 사용

**실습 결과**:
```
"강아지" ↔ "고양이" 유사도: 0.9962 (매우 유사)
"강아지" ↔ "자동차" 유사도: 0.9656 (매우 다름)
```

**한국어 모델 후보**:
- ko-sroberta-multitask
- ko-simcse-roberta
- BGE M3 (다국어)

---

### 4. LLM (Large Language Model)

**정의**: 대규모 텍스트로 학습된 언어 생성 모델

**핵심 기술**:
- Transformer 아키텍처
- Attention 메커니즘
- 문맥 이해 및 자연어 생성

**RAG에서의 역할**:
1. 검색된 문서 내용 이해
2. 사용자 질문 의도 파악
3. 근거 기반 답변 생성
4. 불확실성 표현 (모르면 "모른다" 답변)

**한국어 모델 후보**:
- EEVE (한국어 성능 우수)
- SOLAR (효율성)
- API 기반: GPT-4, Claude, Gemini

---

## 💡 실습을 통한 검증

### 실습 1: 임베딩 유사도 계산
- 단어를 2차원 벡터로 표현
- 코사인 유사도로 관련성 측정
- **결과**: 같은 카테고리 단어들이 높은 유사도 확인

### 실습 2: 벡터 검색 시뮬레이션
- 5개 문서로 간단한 DB 구성
- 질문에 대한 유사 문서 검색
- **결과**: 관련 문서가 상위에 정확히 검색됨

### 실습 3: RAG 전체 흐름 시뮬레이션
```
질문: "반려동물은 어떤 특징이 있나요?"
→ 검색: "강아지는 충성스러운...", "고양이는 독립적인..."
→ 답변: 검색된 문서를 기반으로 답변 생성
```

---

## 🛠️ 기술 스택 결정

### 개발 환경
- **언어**: Python 3.9+
- **가상환경**: venv/conda
- **버전 관리**: Git

### 핵심 라이브러리
```
langchain          # RAG 파이프라인 구축
sentence-transformers  # 임베딩 모델
faiss-cpu          # 벡터 검색
pypdf2             # PDF 처리
fastapi            # API 서버 (6주차)
dash               # 웹 UI (7주차)
```

---

## 🧾 RAG 학습 용어 · 명령어 사전

### 핵심 용어 (사전순)
- **ANN (Approximate Nearest Neighbor)**: 고차원 벡터 공간에서 근사 최근접 이웃을 빠르게 찾기 위한 알고리즘 계열. FAISS, HNSW 등.
- **BM25**: 전통적인 키워드 기반 검색 모델. RAG에서 초기 후보군 확보에 활용 가능.
- **Chunk**: 긴 문서를 일정 규칙으로 나눈 텍스트 조각. RAG에서는 검색 정밀도를 높이는 기본 단위.
- **Context Window**: LLM이 한 번에 처리할 수 있는 토큰 범위. 컨텍스트가 길어질수록 비용·시간이 증가.
- **Embedding**: 텍스트/이미지 등을 벡터 공간으로 투영한 수치 표현. 의미 유사성이 거리로 나타남.
- **FAISS**: Facebook AI에서 만든 벡터 검색 라이브러리. CPU/GPU 지원, 대규모 검색에 최적화.
- **Hallucination**: LLM이 근거 없는 답변을 생성하는 현상. RAG는 검색 근거를 주어 억제.
- **Indexer**: 문서를 청킹·임베딩·벡터 DB에 저장하는 파이프라인 전체를 지칭.
- **K-Value (top_k)**: 검색 시 반환할 문서/청크 개수. 높을수록 recall↑, precision↓.
- **LangChain**: LLM 애플리케이션 구성용 프레임워크. 체인, 에이전트, 도구 호출 등을 추상화.
- **LLM (Large Language Model)**: 대규모 텍스트로 학습된 언어 모델. GPT-4, Claude, Gemini 등.
- **Metadata**: 청크와 관련된 부가 정보(문서 제목, 페이지 번호 등). 검색 후 필터링에 활용.
- **OpenAI Embedding**: OpenAI에서 제공하는 임베딩 API. `text-embedding-3-large` 등.
- **Prompt Engineering**: LLM 입력 프롬프트를 설계·튜닝하는 과정. RAG에서는 추출된 근거를 포함하도록 작성.
- **QA Pair**: 질문과 정답 세트. retrieval 평가나 few-shot 학습에 활용.
- **Recall / Precision**: 검색 품질 지표. Recall은 놓치지 않는 정도, Precision은 정확한 비율.
- **Retriever**: 질문 벡터를 받아 벡터 DB에서 유사한 청크를 찾아주는 컴포넌트.
- **Similarity Search**: 임베딩 벡터 간 거리/유사도를 기반으로 관련 문서를 찾는 과정.
- **Tesseract OCR**: 스캔본 PDF를 텍스트로 변환하기 위한 오픈소스 OCR 엔진.

### 필수 명령어 & 실행 예시
#### 가상환경 및 패키지
- `python -m venv venv` : 새 가상환경 생성
- `venv\Scripts\activate` : Windows PowerShell에서 가상환경 활성화
- `pip install -r requirements.txt` : 프로젝트 의존성 설치
- `setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"` : Windows에 Tesseract 경로 등록

#### Week2 (PDF 전처리 · 청킹)
- `python src/week2/run_week2.py --pdf data/raw/sample.pdf --enable-ocr --output-dir data/processed/sample`
- `python src/week2/pdf_loader.py --path data/raw/sample.pdf --enable-ocr --output data/processed/sample.json`
- `python src/week2/chunking_pipeline.py --path data/processed/sample.txt --strategy recursive --chunk-size 600 --overlap 100`

#### Week3 (임베딩 · 벡터 인덱스)
- `python src/week3/run_week3.py --chunks-json data/processed/sample/chunks/recursive.json --output-dir data/processed/index/sample`
- `python src/week3/embedding_pipeline.py` : `data/processed` 폴더의 `.txt` 파일을 임베딩
- `python src/week3/vector_store_builder.py` : 임베딩 결과를 FAISS 인덱스로 저장

#### Week4 (RAG 체인 · 평가)
- `python src/week4/run_week4.py --index-dir data/processed/index/sample --validation data/eval/validation.json --google-key your_api_key`
- `python src/week4/rag_chain.py` : 기본 질의응답 체인 실행
- `python src/week4/retrieval_eval.py --validation data/eval/validation.json` : Recall@k 계산

#### Week5 (프롬프트 튜닝)
- `python src/week5/run_week5.py --save data/processed/week5_report.txt`
- `.env` 예시: `GOOGLE_API_KEY=your_key`

#### Week6 (FastAPI 서비스)
- `python src/week6/run_week6.py --index-dir data/processed/index/sample --google-key your_api_key`
- `uvicorn week6.api_server:app --host 0.0.0.0 --port 8000 --app-dir src` : 직접 서버 실행
- `python src/week6/smoke_test.py` : API 기본 동작 확인

#### Week7 (Dash UI)
- `python src/week7/run_week7.py --api-endpoint http://localhost:8000/query`
- 웹 브라우저에서 `http://localhost:8050` 접속 후 UI 확인

#### Docker 관련
- `docker build -t rag-study .`
- `docker run --rm -it -p 8000:8000 rag-study`
- `docker logs <container_id>` : 컨테이너 로그 확인

---

## 📊 RAG vs 순수 LLM 비교표

| 평가 항목 | 순수 LLM | RAG 시스템 |
|----------|----------|-----------|
| **지식 범위** | 학습 데이터 한정 ⚠️ | 외부 문서 활용 ✅ |
| **최신성** | 학습 시점까지 ⚠️ | 문서 업데이트 반영 ✅ |
| **정확도** | 환각 위험 ⚠️ | 근거 기반 높음 ✅ |
| **검증 가능성** | 출처 불명 ⚠️ | 출처 추적 가능 ✅ |
| **비용** | 낮음 (1회 호출) ✅ | 중간 (검색+LLM) ⚠️ |
| **응답 속도** | 빠름 ✅ | 중간 (검색 추가) ⚠️ |

---

## 🎯 프로젝트 최종 목표 재확인

**시스템 구성**:
- 백엔드: FastAPI
- 프론트엔드: Dash
- 오케스트레이션: Langchain & Langgraph

**핵심 기능**:
- 이미지+텍스트 혼합 PDF 처리
- 자연어 질문 입력
- 문서 기반 답변 생성
- 근거(출처) 제시

---

## 📈 학습 성과

### 이론 학습
✅ RAG의 개념과 필요성 완전 이해  
✅ 3단계 작동 원리 (Indexing → Retrieval → Generation) 파악  
✅ 벡터 DB, 임베딩, LLM의 역할 명확화  

### 실습 경험
✅ 임베딩 유사도 계산 직접 구현  
✅ 벡터 검색 메커니즘 시뮬레이션  
✅ RAG 전체 파이프라인 프로토타입 실행  

### 환경 구축
✅ Python 개발 환경 구성  
✅ 필수 라이브러리 목록 정리  
✅ 가상환경 설정 방법 습득  

---

## 🔜 2주차 학습 계획

**주제**: 데이터 수집 및 전처리 (Indexing Part 1)

**목표**:
- PDF 문서에서 텍스트와 이미지 정보 추출
- 효과적인 청킹(Chunking) 전략 연구
- 이미지와 텍스트 혼합 처리 방법 구현

**예상 결과물**:
- `preprocess.py`: PDF → 청크 변환 스크립트
- 청킹 전략 비교 문서

---

## 💭 학습 소감 및 질문사항

**명확히 이해한 부분**:
- RAG가 왜 필요한지, 어떤 문제를 해결하는지
- 벡터 검색이 어떻게 "의미"를 찾아내는지
- 전체 시스템의 데이터 흐름

**더 깊이 학습하고 싶은 부분**:
- 임베딩 모델의 내부 구조 (Transformer)
- 벡터 DB의 인덱싱 알고리즘 (ANN)
- LLM의 프롬프트 엔지니어링 기법

**다음 주 기대사항**:
- 실제 PDF 파일 처리 경험
- 다양한 청킹 전략 실험
- 이미지가 포함된 문서 처리 방법

---

## 📌 핵심 개념 한줄 요약

> **RAG는 외부 문서를 검색하여 LLM의 답변에 근거를 제공하는 시스템으로,  
> 벡터 임베딩과 유사도 검색을 통해 관련 문서를 찾고,  
> LLM이 이를 바탕으로 정확하고 검증 가능한 답변을 생성한다.**

---

**1주차 학습 완료** ✅  
**다음 단계**: 2주차 - PDF 전처리 및 청킹

