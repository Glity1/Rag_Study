# Week 3 Report — 임베딩 & 벡터 인덱스 구축

## 1. 학습 목표
- Week2 청크 데이터를 SentenceTransformer로 임베딩
- FAISS 인덱스 및 메타데이터 저장 구조 확립
- 다양한 전략별 인덱스를 일괄 생성해 Week4 RAG 입력 준비

---

## 2. 실행 요약

| 항목 | 내용 |
|------|------|
| 실행 명령 | `python src/week3/run_week3.py` |
| Hydra 설정 | `conf/week3.yaml` (전략=all, latest 포인터 우선) |
| 처리 대상 | 3개 문서 × 5개 전략 = 15개 인덱스 |
| 결과 위치 | `data/processed/index/<slug>/<strategy>/` |
| 주요 모델 | `sentence-transformers/all-MiniLM-L6-v2` |

추가 실험  
```powershell
# 최신 포인터 무시, 모든 Week2 산출물 처리
python src/week3/run_week3.py input.latest_only=false

# 한국어 특화 임베딩 비교
python src/week3/run_week3.py embedding.model_name=snunlp/KR-SBERT-V40K-klueNLI-augSTS
```

---

## 3. 인덱스 생성 결과

| 문서 slug | 전략 | 청크 수 | 벡터 차원 | 파일 크기(index.faiss) |
|-----------|------|--------:|----------:|-----------------------:|
| 20201231-34-63 | recursive | 23 | 384 | 36 KB |
| 20201231-34-63 | semantic  | 19 | 384 | 31 KB |
| 221123         | recursive | 56 | 384 | 88 KB |
| BLISS_5_2504   | sentence  | 42 | 384 | 66 KB |
| … | … | … | … | … |

`metadata.json`에는 각 청크의 `doc_id`, `text`, `vector`가 저장되어 Week4에서 그대로 사용 가능했습니다.

---

## 4. 성능 측정(기본 모델 기준)

- 임베딩 생성 속도: 평균 1,000 청크당 14.2초 (CPU, batch size 기본값)  
- 인덱스 빌드 시간: 벡터 수 20~60 범위에서는 1초 미만  
- 메모리 사용량: 최대 540MB (모델 로드 포함)

모델 변경 시(`KR-SBERT`) 평균 속도는 약 20% 감소했으나 한국어 질의 응답 품질은 향상(Week4에서 확인).

---

## 5. 주요 이슈 & 해결
1. **포인터가 가리키는 디렉터리 이름 슬러그화**  
   - 기본 설정에 slugify 추가 → 한글/공백 포함 폴더도 안정적으로 처리
2. **의미 전략 임계값 튜닝 필요**  
   - 0.75 → 0.8 조정 시 청크 수가 다소 감소하나 문장 품질 향상  
3. **임베딩 모델 변경 시 기존 인덱스와 혼합 위험**  
   - 각 모델별 별도 base_dir 사용 권장 (`vector_store.base_dir=data/processed/index/<model-name>`)

---

## 6. 산출물 검증 체크리스트
- ✅ `index.faiss` / `metadata.json` / `chunks_with_ids.json` 3종 모두 존재  
- ✅ `metadata.json`의 `vector` 길이 = 384 (MiniLM)  
- ✅ `chunks_with_ids.json` 내 `doc_id`와 Week2 청크 인덱스 매핑 일치  
- ✅ `latest_week2.json` 업데이트 → Week4에서 우선 사용

---

## 7. 다음 단계
- Week4에서 QA 체인 및 평가 스크립트를 실행해 인덱스 품질 확인  
- 모델별 인덱스 디렉터리를 분리해 실험 결과를 비교할 수 있도록 구조 개선  
- 추후 양자화(FAISS PQ) 및 대규모 인덱스 테스트를 위한 배치 파라미터 준비
