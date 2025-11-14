# Week1: RAG 기본 개념 학습

## 연구 날짜
2025년 11월 1주차

## 연구 목적
Retrieval-Augmented Generation(RAG)의 기본 개념을 이해하고, 간단한 실습을 통해 동작 원리를 파악한다.

## 학습 내용

### RAG의 정의
RAG는 외부 지식 베이스에서 관련 정보를 검색(Retrieval)하여 생성(Generation) 과정에 활용하는 기법입니다.

### RAG의 핵심 구성 요소
1. **Retriever**: 질문과 관련된 문서를 검색
2. **Generator (LLM)**: 검색된 문서를 바탕으로 답변 생성
3. **Vector Store**: 문서를 벡터로 변환하여 저장

### RAG의 장점
- 최신 정보 활용 가능
- 도메인 특화 지식 활용
- 환각(Hallucination) 감소
- 답변의 근거 제공 가능

## 실습 내용

### 실행 파일
- `src/week1/week1_hands_on.py`

### 실습 결과
- RAG의 기본 동작 원리 이해
- 검색과 생성의 결합 과정 파악
- 간단한 RAG 파이프라인 체험

## 학습 자료
- RAG 관련 논문 및 문서
- LangChain 공식 문서

## 첨부 파일
- `src/week1/week1_hands_on.py`
- `notebooks/week1/week1_rag_learning.md`

## 다음 주차 계획
Week2에서는 실제 PDF 문서를 전처리하고 청킹하는 방법을 학습합니다.

---

**작성일**: 2025년 11월 1주차  
**연구자**: [서혁준]

