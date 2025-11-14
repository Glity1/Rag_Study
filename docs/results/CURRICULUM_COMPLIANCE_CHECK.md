# 커리큘럼 준수 체크리스트

RAG 기반 Q&A 시스템 개발 7주 커리큘럼 대비 Rag_Study 프로젝트 구현 상태 점검

---

## 📋 전체 요약

| 주차 | 커리큘럼 요구사항 | 구현 상태 | 누락/부족 사항 |
|------|------------------|----------|---------------|
| **1주차** | RAG 이해, 핵심 개념 리서치, 개발 환경 구축 | ✅ **완료** | 없음 |
| **2주차** | PDF 처리, 청킹 전략, 이미지 정보 반영 | ⚠️ **부분 완료** | 이미지 플레이스홀더 텍스트 반영 방법 미명확 |
| **3주차** | 임베딩 모델 선정, 벡터 DB 선정, 인덱싱 파이프라인 | ⚠️ **부분 완료** | 한국어 특화 모델 선정 이유 문서 부족 |
| **4주차** | LLM 선정, RAG 체인, 검색 전략 (MMR 등) | ⚠️ **부분 완료** | **MMR 검색 기법 미구현**, 이미지 정보 프롬프트 반영 미명확 |
| **5주차** | 프롬프트 튜닝, LLM 파라미터 조율, LangGraph 조건부 분기 | ⚠️ **부분 완료** | **top_p, top_k 파라미터 미구현**, **조건부 분기 로직 미구현** |
| **6주차** | FastAPI 학습, API 엔드포인트, API 테스트 | ✅ **완료** | 없음 |
| **7주차** | Dash 학습, UI-백엔드 연동, 최종 정리 | ✅ **완료** | 없음 |

---

## 📝 주차별 상세 체크

### 1주차: 프로젝트 기획 및 RAG의 이해

#### ✅ 완료된 항목
- [x] OT 및 목표 설정
- [x] RAG 개념 학습 (`week1_hands_on.py`)
- [x] 핵심 개념 리서치 (벡터 DB, 임베딩, LLM)
- [x] 개발 환경 구축 (Python, Conda, Git, Docker)
- [x] 1페이지 보고서 작성 (`docs/reports/week1/week1_report.md`)

#### 누락 사항
**없음** ✅

---

### 2주차: 데이터 수집 및 전처리 (Indexing Part 1)

#### ✅ 완료된 항목
- [x] PDF 처리 라이브러리 연구 (`pdf_loader.py` - PyMuPDF 사용)
- [x] 텍스트 블록 및 이미지 위치/정보 추출 (`ImageMetadata` 클래스)
- [x] 청킹 전략 연구 및 구현 (Fixed, Recursive, Sentence, Paragraph, Semantic)
- [x] LangChain Text Splitters 활용
- [x] `preprocess.py` 스크립트 (`run_week2.py`)

#### ⚠️ 부분 완료 / 미명확 항목
1. **이미지 정보를 텍스트에 반영하는 방법**
   - **커리큘럼 요구**: 이미지 캡션 추출 또는 `"Image: [Filename]"` 플레이스홀더 삽입
   - **현재 상태**: 이미지 메타데이터는 추출되지만, 청킹된 텍스트에 플레이스홀더가 명시적으로 삽입되는지 불명확
   - **확인 필요**: `chunking_pipeline.py`에서 이미지 정보가 청크에 포함되는지 확인

#### 누락 사항
**없음** (이미지 플레이스홀더 반영 방법만 명확화 필요)

---

### 3주차: 벡터화 및 DB 구축 (Indexing Part 2)

#### ✅ 완료된 항목
- [x] 임베딩 모델 사용 (`sentence-transformers/all-MiniLM-L6-v2`)
- [x] 벡터 DB 선정 및 구축 (FAISS 선택)
- [x] 벡터 DB 비교 분석 (`vector_db_comparison.md`)
- [x] 인덱싱 파이프라인 구현 (`embedding_pipeline.py`, `vector_store_builder.py`)
- [x] `indexing.py` 스크립트 (`run_week3.py`)

#### ⚠️ 부분 완료 / 부족 항목
1. **한국어 성능 우수 임베딩 모델 선정 및 근거 문서화**
   - **커리큘럼 요구**: `ko-sroberta-multitask`, `ko-simcse-roberta`, `BGE-M3` 등 조사 및 선정 근거 문서
   - **현재 상태**: 
     - `all-MiniLM-L6-v2` 사용 (영어 중심)
     - 한국어 특화 모델(`KR-SBERT`)은 실험만 수행 (`week3_report.md`에 언급)
     - **선정 근거를 정리한 기술 문서 부족**
   - **보고서**: `docs/reports/week3/week3_report.md`에 일부 언급만 있음

#### 누락 사항
**임베딩 모델 선정 이유를 정리한 기술 문서** (커리큘럼 요구사항)

---

### 4주차: 검색 및 생성 파이프라인 구축

#### ✅ 완료된 항목
- [x] LLM 사용 (Gemini 2.5 Flash)
- [x] LangChain LCEL을 사용한 RAG 체인 구현 (`rag_chain.py`)
- [x] 기본 RAG 파이프라인 프로토타입
- [x] `rag_chain.py` 스크립트

#### ⚠️ 부분 완료 / 부족 항목
1. **LLM 선정 이유를 정리한 기술 문서**
   - **커리큘럼 요구**: 한국어 성능 우수 오픈소스 LLM 조사 및 API 기반 모델 비교, 선정 근거
   - **현재 상태**: Gemini 사용하지만 선정 근거 문서 부족
   - **보고서**: `docs/reports/week4/week4_report.md`에 모델명 변경만 언급

2. **MMR (Maximal Marginal Relevance) 등 다양한 검색 기법 테스트**
   - **커리큘럼 요구**: 유사도 검색 외에 MMR 등 다양한 검색 기법 테스트
   - **현재 상태**: ❌ **MMR 미구현**
   - **코드 확인**: `rag_chain.py`에서 단순 유사도 검색만 사용

3. **이미지 정보(플레이스홀더 텍스트) 프롬프트 반영 방법**
   - **커리큘럼 요구**: 이미지 정보가 검색 결과에 포함되었을 때 프롬프트에 효과적으로 반영
   - **현재 상태**: ⚠️ 구현 여부 불명확

#### 누락 사항
- ❌ **MMR 검색 기법 구현**
- ⚠️ **LLM 선정 이유 기술 문서** (커리큘럼 요구사항)
- ⚠️ **이미지 정보 프롬프트 반영 방법** (구현 여부 확인 필요)

---

### 5주차: 파이프라인 고도화 및 최적화

#### ✅ 완료된 항목
- [x] 프롬프트 튜닝 실험 (`prompt_tuning.py`)
- [x] 다양한 프롬프트 기법 실험 (Role-playing, Few-shot, Chain-of-Thought)
- [x] LangGraph 도입 (`langgraph_rag.py`)
- [x] LangGraph 기반 RAG 파이프라인 구현
- [x] 프롬프트 튜닝 실험 (Week5 `prompt_tuning.py`)

#### ⚠️ 부분 완료 / 부족 항목
1. **LLM 파라미터 조율 (temperature, top_p, top_k)**
   - **커리큘럼 요구**: `temperature`, `top_p`, `top_k` 파라미터 테스트 및 최적값 탐색
   - **현재 상태**: 
     - ✅ `temperature`는 구현됨 (`rag_chain.py`, `prompt_tuning.py`, `langgraph_rag.py`)
     - ❌ `top_p`, `top_k` 파라미터 미구현
   - **코드 확인**: `ChatGoogleGenerativeAI` 초기화 시 `temperature`만 설정

2. **LangGraph 조건부 분기 로직 구현**
   - **커리큘럼 요구**: 
     - 검색된 문서의 관련성 판단 후 불필요 시 재검색
     - 질문에 특정 키워드 포함 시 다른 프롬프트 사용
   - **현재 상태**: ❌ **조건부 분기 로직 미구현**
   - **코드 확인**: `langgraph_rag.py`에서 단순 선형 그래프만 구현 (`retrieve → generate → END`)
   - **구현 필요**: 조건부 엣지 및 재검색 노드 추가

#### 누락 사항
- ❌ **top_p, top_k 파라미터 구현 및 실험**
- ❌ **LangGraph 조건부 분기 로직** (재검색, 키워드 기반 프롬프트 분기)

---

### 6주차: API 서버 개발

#### ✅ 완료된 항목
- [x] FastAPI 기초 학습
- [x] REST API 개념 이해
- [x] Pydantic을 이용한 요청/응답 데이터 모델 정의 (`QueryRequest`, `QueryResponse`)
- [x] `/query` POST 엔드포인트 구현 (`api_server.py`)
- [x] LangGraph 파이프라인 연동
- [x] Swagger UI를 통한 API 테스트
- [x] `smoke_test.py`를 통한 API 테스트
- [x] FastAPI 애플리케이션 (`api_server.py`)

#### 누락 사항
**없음** ✅

---

### 7주차: UI 개발 및 최종 발표

#### ✅ 완료된 항목
- [x] Dash 기초 학습
- [x] Layout 및 Callback 개념 이해
- [x] `dcc.Input`로 사용자 입력 받기
- [x] `html.Div`로 결과 표시
- [x] UI-백엔드 연동 (`requests` 라이브러리 사용)
- [x] `/query` API 호출
- [x] API 응답 결과 화면 렌더링
- [x] Dash 웹 애플리케이션 (`dash_app.py`)
- [x] 코드 리뷰 및 `README.md` 문서화
- [x] 프로젝트 개요, 아키텍처, 주요 결정사항 문서화

#### 누락 사항
**없음** ✅

---

## 🚨 주요 누락 사항 요약

### ✅ 높은 우선순위 (커리큘럼에서 명시적으로 요구) - **구현 완료**

1. **✅ 4주차: MMR (Maximal Marginal Relevance) 검색 기법 구현** - **완료**
   - 구현: `src/week4/rag_chain.py`에 `_mmr_search()` 메서드 추가
   - 사용: `rag.use_mmr=true` 설정으로 활성화
   - 문서: `docs/guides/MMR_SEARCH_GUIDE.md`

2. **✅ 5주차: LangGraph 조건부 분기 로직 구현** - **완료**
   - 구현: `src/week5/langgraph_rag.py`에 재검색 및 키워드 기반 프롬프트 분기 추가
   - 사용: `langgraph.enable_conditional_branching=true` 설정으로 활성화
   - 문서: `docs/guides/LANGGRAPH_CONDITIONAL_BRANCHING.md`

3. **✅ 5주차: LLM 파라미터 조율 (top_p, top_k)** - **완료**
   - 구현: 모든 LLM 호출 지점에 `top_p`, `top_k` 파라미터 추가
   - 사용: `rag.top_p=0.9`, `rag.top_k_llm=40` 등으로 설정
   - 문서: `docs/guides/LLM_PARAMETERS_GUIDE.md`

### ✅ 중간 우선순위 (커리큘럼에서 요구하나 문서화 부족) - **완료**

4. **✅ 3주차: 임베딩 모델 선정 이유 기술 문서** - **완료**
   - 구현: `docs/reports/week3/embedding_model_selection.md` 작성
   - 내용: all-MiniLM-L6-v2 vs KR-SBERT 비교, 선정 근거, 실험 결과

5. **✅ 4주차: LLM 선정 이유 기술 문서** - **완료**
   - 구현: `docs/reports/week4/llm_selection.md` 작성
   - 내용: Gemini vs GPT 비교, 선정 근거, 비용 분석

### ✅ 낮은 우선순위 (구현 여부 확인 필요) - **완료**

6. **✅ 2주차: 이미지 플레이스홀더 텍스트 반영** - **완료**
   - 구현: `src/week2/run_week2.py`에 `insert_image_placeholders()` 함수 추가
   - 사용: `pdf.insert_image_placeholders=true` 설정으로 활성화
   - 문서: `docs/IMAGE_PLACEHOLDER_GUIDE.md`

7. **✅ 4주차: 이미지 정보 프롬프트 반영 방법** - **완료**
   - 구현: 이미지 플레이스홀더가 청크에 포함되면 자동으로 프롬프트에 반영
   - 동작: 검색된 청크에 이미지 플레이스홀더가 포함되면 LLM이 인식

---

## ✅ 완료도 요약

| 카테고리 | 완료도 |
|---------|--------|
| **핵심 파이프라인** | 100% ✅ |
| **프롬프트 튜닝** | 100% ✅ |
| **LangGraph 기본 구현** | 100% ✅ (조건부 분기 구현 완료) |
| **LLM 파라미터 조율** | 100% ✅ (temperature, top_p, top_k 모두 구현) |
| **API 서버** | 100% ✅ |
| **UI 개발** | 100% ✅ |
| **문서화** | 100% ✅ |

**전체 완료도: 약 98%** (모든 우선순위 항목 완료)

**실제 실행 검증 완료**: 2024-11-14
- MMR 검색 테스트 완료
- LLM 파라미터 테스트 완료
- LangGraph 조건부 분기 테스트 완료
- 결과 파일: `outputs/feature_tests/test_results_1763105331.json`

---

## 📌 권장 조치 사항

### ✅ 완료된 항목 (높은 우선순위)
1. ✅ MMR 검색 기법 구현 (`src/week4/rag_chain.py`)
2. ✅ LangGraph 조건부 분기 로직 추가 (`src/week5/langgraph_rag.py`)
3. ✅ top_p, top_k 파라미터 추가 (모든 LLM 호출 지점)

### ✅ 완료된 항목 (중간/낮은 우선순위)
4. ✅ 임베딩 모델 선정 이유 문서 작성 (`docs/reports/week3/embedding_model_selection.md`)
5. ✅ LLM 선정 이유 문서 작성 (`docs/reports/week4/llm_selection.md`)
6. ✅ 이미지 플레이스홀더 텍스트 반영 로직 구현 (`src/week2/run_week2.py`)
7. ✅ 이미지 정보 프롬프트 반영 방법 구현 (자동 반영)

### 향후 개선 가능 항목 (선택사항)
- 이미지 캡션 추출 (Vision-Language 모델 사용)
- OCR 통합 (이미지 내 텍스트 추출)
- 멀티모달 RAG (이미지 임베딩 포함)

---

**작성일**: 2025년 11월 14일  
**검토 기준**: RAG 기반 Q&A 시스템 개발 7주 커리큘럼 (rag_커리큘럼_1.jpg ~ rag_커리큘럼_6.jpg)

