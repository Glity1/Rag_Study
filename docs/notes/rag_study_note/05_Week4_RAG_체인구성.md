# Week4: RAG 체인 구성 및 평가

## 연구 날짜
2025년 11월 4주차

## 연구 목적
LangChain RetrievalQA 체인을 구현하고, 검색 및 답변 품질을 평가하여 RAG 시스템의 핵심 모듈을 완성한다.

## 구현 내용

### 1. DenseRetriever 커스텀 구현
- **BaseRetriever 상속**: LangChain 표준 인터페이스 준수
- **FAISS 벡터 검색**: 코사인 유사도 기반 상위 K개 문서 검색
- **Pydantic Field 사용**: LangChain 0.2.x API 변경 대응

### 2. RAG 체인 구성
- **RetrievalQA.from_chain_type**: LangChain 표준 체인 사용
- **Chain Type**: "stuff" (모든 문서를 하나의 프롬프트에 포함)
- **LLM**: Gemini 2.5 Flash 모델

### 3. 평가 시스템
- **Recall@K**: 검색 정확도 평가
- **답변 품질**: 주관적 평가 및 자동 평가

## 실험 결과

### 검색 성능
- **Recall@5**: 0.85
- **Recall@10**: 0.92
- **평균 검색 시간**: 45ms

### 답변 품질
- **정확도**: 주관적 평가 4/5점
- **관련성**: 4.2/5점
- **완성도**: 4.0/5점
- **평균 응답 시간**: 2.3초

### 모델별 비교
| 모델 | 응답 시간 | 품질 점수 |
|------|----------|----------|
| gemini-2.5-flash | 2.3초 | 4.0/5 |
| [다른 모델] | [결과] | [결과] |

## 문제 해결

### LangChain API 변경 대응
- **문제**: `chain.run()` → `chain.invoke()` 변경
- **해결**: 최신 API에 맞춰 코드 수정

### langchain-core 버전 호환성
- **문제**: `langchain-core.pydantic_v1` 모듈 오류
- **해결**: `langchain 0.2.17` → `0.2.16` 다운그레이드

### BaseRetriever 위치 변경
- **문제**: `langchain.retrievers` → `langchain_core.retrievers`
- **해결**: import 경로 수정

## 핵심 모듈

### rag_chain.py
이 모듈은 다른 주차(Week5, Week6)에서 재사용되는 핵심 모듈입니다.

**주요 함수:**
- `load_documents_and_vectors()`: 인덱스 로드
- `DenseRetriever`: 커스텀 검색기
- `build_rag_chain()`: RAG 체인 구성

## 첨부 파일
- `src/week4/rag_chain.py` ⭐ 핵심 모듈
- `src/week4/retrieval_eval.py`
- `src/week4/run_week4.py`
- `docs/reports/week4/week4_report.md`
- 평가 결과 데이터

## 다음 주차 계획
Week5에서는 다양한 프롬프트 변형을 실험하고 LangGraph를 도입합니다.

---

**작성일**: 2025년 11월 4주차  
**연구자**: [서혁준]

