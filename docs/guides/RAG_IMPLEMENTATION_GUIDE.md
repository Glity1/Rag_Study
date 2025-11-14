# RAG 프로젝트 구현 가이드

랜덤한 프로젝트에 RAG(Retrieval-Augmented Generation)를 적용할 때의 단계별 체크리스트입니다.

---

## 📋 단계별 작업 체크리스트

### 1단계: 프로젝트 요구사항 파악 및 환경 설정
**목표**: RAG 적용 범위와 환경을 명확히 정의

- [ ] **비즈니스 요구사항 정의**
  - 질의응답 대상 문서/데이터의 형태 파악 (PDF, 웹페이지, 데이터베이스, API 등)
  - 예상 질문 유형과 답변 형식 정의
  - 성능 요구사항 (응답 시간, 정확도, 동시 사용자 수)

- [ ] **환경 설정**
  - Python 가상환경 또는 Conda 환경 구성
  - 필수 라이브러리 설치 (`requirements.txt` 또는 `environment.yml` 작성)
    - LangChain (체인 구성)
    - 임베딩 모델 (SentenceTransformers, OpenAI Embeddings 등)
    - 벡터 DB (FAISS, Chroma, Pinecone, Weaviate 등)
    - LLM (OpenAI, Google Gemini, Anthropic Claude 등)
  - API 키 및 환경 변수 설정 (`.env` 파일)

- [ ] **프로젝트 구조 설계**
  ```
  project/
  ├── data/
  │   ├── raw/          # 원본 문서
  │   ├── processed/    # 전처리된 문서
  │   └── vectors/      # 벡터 인덱스
  ├── src/
  │   ├── loaders/      # 문서 로더
  │   ├── chunking/     # 청킹 전략
  │   ├── embedding/    # 임베딩 파이프라인
  │   ├── retrieval/    # 검색 로직
  │   └── rag/          # RAG 체인
  ├── config/           # 설정 파일 (Hydra 등)
  └── tests/            # 테스트 코드
  ```

---

### 2단계: 문서 로딩 및 전처리 (Week2)
**목표**: 원본 문서를 시스템이 처리 가능한 형태로 변환

- [ ] **문서 로더 구현**
  - 문서 형식별 로더 선택/구현
    - PDF: `PyMuPDF`, `pypdf`, `pdfplumber`
    - 웹: `BeautifulSoup`, `Selenium`
    - 이미지: OCR (`pytesseract`, `EasyOCR`)
    - 데이터베이스: 커스텀 쿼리
    - API: HTTP 클라이언트

- [ ] **메타데이터 추출**
  - 문서 ID, 소스, 날짜, 저자 등 메타데이터 수집
  - 청킹 단계에서 참조 가능하도록 구조화

- [ ] **텍스트 정제**
  - 불필요한 공백, 특수문자 제거
  - 인코딩 문제 해결 (UTF-8 통일)
  - 테이블, 이미지, 표 처리 전략 수립

---

### 3단계: 텍스트 청킹 전략 설계 (Week2)
**목표**: 긴 문서를 검색 가능한 단위로 분할

- [ ] **청킹 전략 선택/실험**
  - **Fixed Size**: 고정 길이 청크 (단순, 빠름)
  - **Recursive Character**: 계층적 분할 (LangChain 기본)
  - **Sentence**: 문장 단위 분할
  - **Semantic**: 의미적 유사도 기반 분할 (고품질, 느림)
  - **Document-specific**: 도메인 특화 전략 (예: 섹션 단위)

- [ ] **청킹 파라미터 튜닝**
  - `chunk_size`: 청크 크기 (보통 200-1000 토큰)
  - `chunk_overlap`: 겹치는 부분 (10-20% 권장)
  - 도메인별 최적값 실험 및 비교

- [ ] **청킹 결과 검증**
  - 샘플 청크 품질 확인
  - 문맥 손실 최소화
  - 청크별 메타데이터 보존 확인

---

### 4단계: 임베딩 생성 및 벡터 인덱스 구축 (Week3)
**목표**: 텍스트를 벡터로 변환하고 검색 가능한 인덱스 생성

- [ ] **임베딩 모델 선택**
  - **로컬 모델**: `sentence-transformers` (무료, 프라이빗)
    - 다국어: `paraphrase-multilingual-MiniLM-L6-v2`
    - 한국어 특화: `jhgan/ko-sbert-multitask`
  - **클라우드 모델**: OpenAI `text-embedding-ada-002`, `text-embedding-3-small`

- [ ] **임베딩 생성 파이프라인**
  - 청크별 임베딩 벡터 생성
  - 벡터 차원 및 정규화 확인
  - 벡터 저장 형식 결정 (JSON, pickle, numpy)

- [ ] **벡터 인덱스 구축**
  - **FAISS** (Facebook AI Similarity Search): 로컬, 빠름
  - **Chroma**: 경량, 메타데이터 필터링 강점
  - **Pinecone**: 클라우드, 확장성 좋음
  - **Weaviate**: 그래프 기반, 고급 기능

- [ ] **인덱스 메타데이터 관리**
  - 청크 ID, 원본 문서 참조, 위치 정보 저장
  - 검색 시 메타데이터 필터링 지원

---

### 5단계: 검색(Retrieval) 로직 구현 (Week4)
**목표**: 사용자 질문에 가장 관련 있는 문서 검색

- [ ] **Retriever 구현**
  - **Dense Retrieval**: 임베딩 유사도 기반 (기본)
  - **Hybrid Retrieval**: Dense + Sparse (BM25 등)
  - **Reranking**: 검색 결과 재정렬 (Cross-encoder 모델)

- [ ] **검색 파라미터 설정**
  - `top_k`: 검색할 문서 개수 (보통 3-10개)
  - 유사도 임계값 설정 (필요시)
  - 메타데이터 필터링 로직

- [ ] **검색 품질 평가**
  - 샘플 질문으로 검색 결과 확인
  - Recall@K 지표 계산
  - 잘못된 검색 패턴 파악 및 개선

---

### 6단계: RAG 체인 구성 및 LLM 통합 (Week4-5)
**목표**: 검색된 문서와 질문을 LLM에 전달하여 답변 생성

- [ ] **LLM 선택 및 설정**
  - **OpenAI**: `gpt-4`, `gpt-3.5-turbo`
  - **Google**: `gemini-pro`, `gemini-1.5-flash`
  - **Anthropic**: `claude-3-opus`, `claude-3-sonnet`
  - **로컬**: `llama2`, `mistral` (Ollama 등)

- [ ] **프롬프트 엔지니어링**
  - 컨텍스트와 질문을 포함한 프롬프트 템플릿 작성
  - 역할 설정, 답변 형식, 근거 요구사항 명시
  - 프롬프트 버전별 A/B 테스트

- [ ] **RAG 체인 구현**
  - LangChain `RetrievalQA` 또는 커스텀 체인
  - LangGraph를 활용한 복잡한 플로우 구성 (필요시)
  - 에러 처리 및 폴백 로직

- [ ] **답변 품질 검증**
  - 다양한 질문 유형으로 테스트
  - 할루시네이션 감지 및 감소
  - 근거 문서 인용 정확도 확인

---

### 7단계: API 서버 및 UI 구성 (Week6-7)
**목표**: RAG 시스템을 실제 사용 가능한 서비스로 배포

- [ ] **API 서버 구축**
  - **FastAPI**: RESTful API 엔드포인트
    - `/query`: 질문 요청 처리
    - `/health`: 헬스체크
    - `/retrieve`: 검색만 수행 (디버깅용)
  - 인증/인가 추가 (필요시)
  - 요청/응답 로깅 및 모니터링

- [ ] **UI 구축 (선택사항)**
  - **Dash/Streamlit**: 빠른 프로토타입
  - **React/Vue**: 커스텀 프론트엔드
  - 대화 히스토리, 근거 문서 표시 기능

- [ ] **성능 최적화**
  - 캐싱 전략 (질문-답변 캐시)
  - 비동기 처리 (FastAPI async)
  - 벡터 검색 병렬화

---

### 8단계: 평가 및 개선 (Week5)
**목표**: 시스템 성능 측정 및 지속적 개선

- [ ] **평가 지표 정의**
  - **정확도**: 답변 정확성 (수동 평가 또는 자동화)
  - **Recall@K**: 검색 품질
  - **응답 시간**: 지연시간 측정
  - **사용자 만족도**: 피드백 수집

- [ ] **평가 데이터셋 구축**
  - 질문-답변 쌍 (Q&A pairs)
  - 검증 세트 (validation set)
  - 엣지 케이스 수집

- [ ] **반복 개선**
  - 청킹 전략 재조정
  - 임베딩 모델 업그레이드
  - 프롬프트 최적화
  - 하이퍼파라미터 튜닝

---

### 9단계: 배포 및 운영
**목표**: 프로덕션 환경에서 안정적으로 서비스 제공

- [ ] **컨테이너화**
  - Docker 이미지 빌드
  - Docker Compose로 멀티 서비스 관리
  - 환경별 설정 분리

- [ ] **인프라 구성**
  - 서버 배포 (AWS, GCP, Azure 등)
  - 벡터 DB 인프라 구축
  - 로드 밸런싱 (필요시)

- [ ] **모니터링 및 로깅**
  - 에러 추적 (Sentry 등)
  - 성능 메트릭 수집
  - 사용 패턴 분석

- [ ] **문서화**
  - API 문서 (Swagger/OpenAPI)
  - 사용자 가이드
  - 운영 매뉴얼

---

## 🚀 빠른 시작 템플릿

### 최소 구현 (MVP)
```
1. PDF 로더 → 2. Recursive 청킹 → 3. Sentence Transformer 임베딩 → 
4. FAISS 인덱스 → 5. LangChain RetrievalQA → 6. 간단한 API/CLI
```

### 고급 구현 (Production)
```
1. 멀티 소스 로더 → 2. Semantic 청킹 + 하이브리드 검색 → 
3. OpenAI Embeddings → 4. Pinecone/Weaviate → 5. LangGraph 체인 + 
Reranking → 6. FastAPI + React UI → 7. 평가 파이프라인
```

---

## ⚠️ 주의사항

1. **문서 품질이 핵심**: 입력 문서의 품질이 RAG 성능에 가장 큰 영향
2. **청킹이 중요**: 잘못된 청킹은 컨텍스트 손실로 이어짐
3. **임베딩 모델 선택**: 도메인 특화 모델이 일반 모델보다 우수할 수 있음
4. **비용 관리**: LLM API 호출 비용을 모니터링하고 최적화
5. **보안**: API 키 및 민감 정보 관리 주의

---

## 📚 참고 리소스

- LangChain 공식 문서: https://python.langchain.com/
- 이 프로젝트의 주차별 실습 코드 참고
- 벡터 DB 비교: `notebooks/week3/vector_db_comparison.md`
- 프로젝트 구현 가이드: `docs/guides/MMR_SEARCH_GUIDE.md`, `docs/guides/LANGGRAPH_CONDITIONAL_BRANCHING.md`, `docs/guides/LLM_PARAMETERS_GUIDE.md`

