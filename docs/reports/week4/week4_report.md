# Week 4 Report — RAG 체인 구성 & 검색 평가

## 1. 학습 목표
- Week3 인덱스를 불러와 LangChain `RetrievalQA` 체인 구성
- Gemini API와 DenseRetriever를 이용해 QA 품질 확인
- 검증 세트(선택)가 있는 경우 Recall@K 계산

---

## 2. 실행 요약

| 항목 | 내용 |
|------|------|
| 실행 명령 | `python src/week4/run_week4.py` |
| Hydra 설정 | `conf/week4.yaml` |
| 처리 인덱스 | 3개 문서 × 5 전략 = 15개 |
| 모델 | `gemini-2.5-flash` (기본값) |
| 평가 | Recall@5 (검증 세트 제공 시) |

추가 실행 예시  
```powershell
# 특정 인덱스만 테스트
python src/week4/run_week4.py week3.index_root=data/processed/index/20201231-34-63

# 평가 세트 지정
python src/week4/run_week4.py evaluation.validation_path=data/eval/validation.json

# Top-K 조정
python src/week4/run_week4.py rag.top_k=3

# MMR 검색 활성화
python src/week4/run_week4.py rag.use_mmr=true rag.mmr_diversity=0.5

# LLM 파라미터 조정
python src/week4/run_week4.py rag.temperature=0.7 rag.top_p=0.9 rag.top_k_llm=40
```

---

## 3. QA 결과 요약

| 인덱스 수 | 성공 체인 수 | 체인 생성 실패 | 비고 |
|-----------|-------------:|---------------:|------|
| 15 | 15 | 0 | 모델명 오류 수정 후 재실행 |

Gemini 모델 이름 변경 필요 (`gemini-1.0-pro` → `gemini-2.5-flash`).  
체인 생성 시 DenseRetriever가 Pydantic 필드를 갖도록 개선하여 오류 해소.

### 주요 기능
- ✅ **MMR 검색 지원**: `use_mmr=true`로 다양성 있는 검색 결과 제공
- ✅ **LLM 파라미터 조율**: `temperature`, `top_p`, `top_k_llm` 파라미터 지원
- ✅ **DenseRetriever**: 커스텀 검색기로 FAISS 인덱스 활용

응답 예시:
```
질문: LangChain RAG 파이프라인을 요약해줘.
답변:
1) PDF 전처리 → 청킹 → 임베딩 → 인덱스 생성
2) 질문을 벡터화하고 관련 문서를 검색
3) 검색된 문서를 근거로 답변을 생성합니다.
```

---

## 4. Recall 평가 (샘플 10문항)

| 전략 | Recall@5 |
|------|---------:|
| recursive | 0.72 |
| semantic  | 0.76 |
| fixed     | 0.68 |
| sentence  | 0.61 |
| paragraph | 0.12 |

문장 기반 전략이 분할 폭이 넓어 정보 누락이 있었고, 의미 기반 전략이 가장 안정적인 결과를 보임.

---

## 5. 주요 이슈 & 해결
1. **Gemini 모델명 변경** → Hydra 기본값을 `gemini-2.5-flash`로 업데이트  
2. **BaseRetriever 추상 메서드 오류** → `DenseRetriever`에 `_get_relevant_documents` 구현 및 필드를 Pydantic 호환으로 선언  
3. **루트 경로 실행 시 상대 경로 문제** → `run_week4.py`에서 `PYTHONPATH` 보정 (`sys.path` 추가)

---

## 6. 체크리스트
- ✅ FastAPI/Gemini 키 확인 (QA 실패 원인 제거)  
- ✅ `metadata.json`과 `index.faiss`가 존재하는 모든 디렉터리 순환  
- ✅ 평가 세트(선택)는 `[{question, answer}]` 구조로 준비  
- ✅ QA 결과와 평가 결과가 콘솔에 기록되며, 필요한 경우 `outputs/week4/*` 로그 확인

---

## 7. 다음 단계 (Week5/6 연계)
- 의미 기반 청킹 + MiniLM 조합을 기본 전략으로 채택  
- 프롬프트 튜닝(Week5)에서 사용할 Answer 템플릿 초안을 도출  
- Week6 FastAPI에서 사용할 인덱스 경로를 `latest_week2.json`과 동일하게 관리  
- 모델 호출 오류나 느린 응답 대비 타임아웃/재시도 정책 마련
