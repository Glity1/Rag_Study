# Week3: 임베딩 생성 및 벡터 인덱스 구축

## 연구 날짜
2025년 11월 3주차

## 연구 목적
SentenceTransformer를 활용하여 텍스트를 임베딩으로 변환하고, FAISS를 통해 벡터 인덱스를 구축하여 고속 유사도 검색을 구현한다.

## 실험 방법

### 1. 임베딩 모델 선택
- **모델**: `sentence-transformers/all-MiniLM-L6-v2`
- **차원**: 384차원
- **선택 이유**: 빠른 처리 속도와 적절한 성능의 균형

### 2. 벡터 정규화
- L2 정규화를 통해 벡터 크기를 1로 정규화
- 코사인 유사도 계산 최적화

### 3. FAISS 인덱스 구축
- **IndexFlatL2**: 정확한 검색 (소규모 데이터)
- 벡터 저장 및 빠른 검색 지원

## 실험 결과

### 임베딩 생성 성능
- **처리 속도**: 평균 [결과] 초/문서
- **임베딩 차원**: 384차원
- **벡터 크기**: [결과] MB

### 인덱스 구축 결과
- **인덱스 파일**: `index.faiss`
- **메타데이터**: `metadata.json`
- **인덱스 크기**: [결과] MB
- **구축 시간**: [결과] 초

### 검색 성능
- **검색 속도**: 평균 [결과] ms/쿼리
- **정확도**: Recall@5 = [결과]

## 구현 내용

### 주요 파일
- `src/week3/embedding_pipeline.py`: 임베딩 생성 파이프라인
- `src/week3/vector_store_builder.py`: FAISS 인덱스 구축

### 출력 결과
```
data/processed/index/<slug>/<strategy>/
  ├─ index.faiss              # FAISS 인덱스
  ├─ metadata.json            # 문서 메타데이터
  └─ chunks_with_ids.json     # 청크 ID 매핑
```

## 문제 해결

### 메모리 부족 문제
- **문제**: 대용량 문서 처리 시 메모리 부족
- **해결**: 배치 처리 및 청크 단위 처리

### 벡터 정규화
- **문제**: 벡터 크기 불일치로 인한 검색 성능 저하
- **해결**: L2 정규화 적용

## 첨부 파일
- `src/week3/embedding_pipeline.py`
- `src/week3/vector_store_builder.py`
- `src/week3/run_week3.py`
- `docs/reports/week3/week3_report.md`
- 샘플 인덱스 메타데이터

## 다음 주차 계획
Week4에서는 구축한 벡터 인덱스를 활용하여 RAG 체인을 구성하고 평가합니다.

---

**작성일**: 2025년 11월 3주차  
**연구자**: [서혁준]

