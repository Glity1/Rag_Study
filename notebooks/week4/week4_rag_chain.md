# 📙 4주차: RAG 체인 구성 & 검색 평가

## 학습 목표
- Week3 인덱스를 활용해 RetrievalQA 체인을 구성  
- Gemini 기반 QA를 수행하고 결과를 확인  
- 검증 세트가 있을 경우 Recall@K 평가 진행

---

## 1. 데이터 의존성
```
data/processed/index/<slug>/<strategy>/
 ├─ index.faiss
 ├─ metadata.json
 └─ chunks_with_ids.json
```

이 디렉터리가 존재해야 Week4가 정상 작동합니다.  
`run_week3.py` 실행 후 생성된 인덱스를 그대로 사용하세요.

---

## 2. 핵심 스크립트 요약

| 파일 | 역할 | 비고 |
|------|------|------|
| `run_week4.py` | 인덱스 탐색 → RAG 체인 → QA/평가 실행 | Hydra `conf/week4.yaml` |
| `rag_chain.py` | `build_rag_chain()` 구현, DenseRetriever 포함 | Gemini 호출 |
| `retrieval_eval.py` | JSON 검증 세트 기반으로 Recall@K 계산 | `validation_path` 필요 |

---

## 3. Hydra 실행 예시
```powershell
# 기본 설정으로 모든 인덱스 테스트
python src/week4/run_week4.py

# 특정 인덱스 디렉터리만 평가
python src/week4/run_week4.py week3.index_root=data/processed/index/20201231-34-63

# 모델 및 Top-K 변경
python src/week4/run_week4.py rag.model_name=gemini-2.5-flash rag.top_k=3

# 평가 데이터 추가
python src/week4/run_week4.py evaluation.validation_path=data/eval/validation.json
```

---

## 4. 출력 로그 예시
```
=== [1/15] 인덱스: .../index/recursive ===
[1/3] RAG 체인 구성 (index=...)
[2/3] 샘플 질문 실행
질문: LangChain RAG 파이프라인을 요약해줘.
답변: ...
[3/3] Recall 평가 실행
Recall@5: 72.00%
```

---

## 5. DenseRetriever 내부 구조
```python
class DenseRetriever(BaseRetriever):
    documents: List[Document]
    vectors: np.ndarray
    embedder: HuggingFaceEmbeddings
    k: int
```
- 질의 임베딩과 벡터 DB를 직접 곱해 상위 K개 문서를 반환  
- 비동기 처리에도 대응 (`_aget_relevant_documents`)

---

## 6. 체크리스트
- [ ] `GOOGLE_API_KEY` 환경변수 설정  
- [ ] Week3 인덱스 디렉터리에 `metadata.json`이 존재  
- [ ] 실행 후 체인 생성/QA 로그가 정상적으로 출력  
- [ ] 평가용 JSON 구조 확인 (`[{"question": "...", "answer": "..."}]`)  
- [ ] 필요 시 Hydra override로 모델/Top-K/인덱스 경로 조정

---

## 7. 문제 해결
- `metadata.json을 찾을 수 없습니다` → 인덱스 경로 또는 Week3 산출물 확인  
- `BaseRetriever` 관련 오류 → `rag_chain.py` 최신 버전(`DenseRetriever`) 확인  
- `404 models/... not found` → `rag.model` 값을 사용 가능한 Gemini 모델로 변경

---

## 8. 다음 단계 예고
- Week5에서는 다양한 프롬프트 변형을 실험합니다.  
- Week6에선 FastAPI 서버로 RAG 체인을 서비스화합니다.

