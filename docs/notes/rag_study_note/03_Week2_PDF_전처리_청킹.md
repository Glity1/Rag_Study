# Week2: PDF 전처리 및 청킹 전략 연구

## 연구 날짜
2025년 11월 2주차

## 연구 목적
PDF 문서에서 텍스트를 추출하고, 다양한 청킹 전략을 비교 분석하여 최적의 전처리 방법을 도출한다.

## 실험 방법

### 1. PDF 텍스트 추출
- `pdf_loader.py`: PyPDF2, pdfplumber를 활용한 텍스트 추출
- OCR 지원: Tesseract를 통한 스캔본 PDF 처리

### 2. 청킹 전략 비교
다음 5가지 청킹 전략을 실험:

1. **Fixed**: 고정 크기 청킹
   - 장점: 일관된 크기, 빠른 처리
   - 단점: 문장/단락 경계 무시

2. **Recursive**: 재귀적 분할
   - 장점: 문장 구조 고려
   - 단점: 복잡한 로직

3. **Sentence**: 문장 단위 분할
   - 장점: 의미 단위 보존
   - 단점: 짧은 문장으로 인한 정보 분산

4. **Paragraph**: 단락 단위 분할
   - 장점: 문맥 보존
   - 단점: 긴 단락 처리 어려움

5. **Semantic**: 의미 기반 분할
   - 장점: 의미 단위 최적화
   - 단점: 처리 시간 증가

## 실험 결과

### 청킹 결과 비교
| 전략 | 평균 청크 수 | 평균 길이 | 처리 시간 |
|------|------------|----------|----------|
| Fixed | [결과] | [결과] | [결과] |
| Recursive | [결과] | [결과] | [결과] |
| Sentence | [결과] | [결과] | [결과] |
| Paragraph | [결과] | [결과] | [결과] |
| Semantic | [결과] | [결과] | [결과] |

### 분석 및 인사이트
- **Recursive 전략**이 가장 균형잡힌 결과를 보임
- **Semantic 전략**은 의미 보존에 우수하나 처리 시간이 길음
- 문서 유형에 따라 최적 전략이 다름

## 구현 내용

### 주요 파일
- `src/week2/pdf_loader.py`: PDF 로더 구현
- `src/week2/chunking_pipeline.py`: 청킹 파이프라인
- `src/week2/run_week2.py`: 통합 실행 스크립트

### 출력 결과
```
data/processed/<slug>/
  ├─ extraction.json      # 추출된 텍스트
  ├─ full_text.txt         # 전체 텍스트
  ├─ summary.json         # 요약 정보
  └─ chunks/              # 청킹 결과
      ├─ fixed.json
      ├─ recursive.json
      ├─ sentence.json
      ├─ paragraph.json
      └─ semantic.json
```

## 문제 해결

### 한글 인코딩 문제
- **문제**: PowerShell 기본 CP949로 인한 한글 깨짐
- **해결**: UTF-8 저장 방식으로 재구성

### RecursiveCharacterTextSplitter 겹침 오류
- **문제**: 청크 간 겹침 발생
- **해결**: `strip_whitespace`, `chunk_size` 조정

## 첨부 파일
- `src/week2/pdf_loader.py`
- `src/week2/chunking_pipeline.py`
- `src/week2/run_week2.py`
- `docs/reports/week2/week2_report.md`
- 샘플 청킹 결과 파일

## 다음 주차 계획
Week3에서는 청킹된 텍스트를 임베딩으로 변환하고 벡터 인덱스를 구축합니다.

---

**작성일**: 2025년 11월 2주차  
**연구자**: [서혁준]

