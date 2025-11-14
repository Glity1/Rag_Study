# 📕 5주차: 프롬프트 튜닝 & 결과 분석

## 학습 목표
- 동일한 질문에 대해 다양한 프롬프트 변형을 적용해 결과 비교  
- LangChain + Gemini 조합의 `PromptTuner` 사용법 이해  
- 프롬프트 실험 결과를 저장하고 간단히 정량 분석

---

## 1. 구성 요소

| 파일 | 역할 | 비고 |
|------|------|------|
| `run_week5.py` | 설정 로딩 → 프롬프트 실행 → 결과 출력/저장 → LangGraph 데모 | Hydra `conf/week5.yaml` |
| `prompt_tuning.py` | `PromptVariant`, `PromptTuner` 정의 + `temperature/top_p/top_k` 지원 | few-shot 예시 지원 |
| `langgraph_rag.py` | LangGraph 기반 RAG 그래프 구성 (조건부 분기/재검색) | `build_rag_graph`, `run_rag` |

---

## 2. Hydra 실행 예시
```powershell
# 기본 프롬프트 세트 실행
python src/week5/run_week5.py

# 모델/온도 변경
python src/week5/run_week5.py llm.model_name=gemini-2.5-flash llm.temperature=0.0

# 결과 저장 경로 지정
python src/week5/run_week5.py output.save_path=data/processed/week5_report.txt

# Analytics 비활성화
python src/week5/run_week5.py output.show_analytics=false
```

`conf/week5.yaml`에서 `variants` 목록을 수정하면 프롬프트 조합을 손쉽게 추가/삭제할 수 있습니다.

---

## 3. LangGraph 조건부 분기 & 재검색

| 기능 | 설정 키 | 설명 |
|------|---------|------|
| 관련성 기반 재검색 | `langgraph.enable_conditional_branching=true` | `check_relevance_node`가 문서 점수가 `langgraph.reretrieve_threshold`보다 낮으면 재검색 |
| 재검색 최대 횟수 | `langgraph.max_reretrieves` | 재검색 반복 상한 (기본 1회) |
| 키워드 분기 | `langgraph.keyword_prompts` | 질문에 특정 키워드가 감지되면 해당 프롬프트를 적용 |
| 참고 문서 | `docs/guides/LANGGRAPH_CONDITIONAL_BRANCHING.md` | 구현 흐름도와 테스트 결과 |

```powershell
python src/week5/run_week5.py ^
  langgraph.enable_conditional_branching=true ^
  langgraph.reretrieve_threshold=0.35 ^
  langgraph.max_reretrieves=2 ^
  langgraph.keyword_prompts='[{"keyword":"전략","system":"전략가","user":"전략 요약"}]'
```

---

## 4. LLM 파라미터 / 출력 제어
- `llm.temperature`, `llm.top_p`, `llm.top_k`를 Hydra override로 조합 가능  
- `PromptTuner`와 LangGraph 노드 모두 동일한 파라미터를 사용하므로 실험 일관성 유지  
- 참고 문서: `docs/guides/LLM_PARAMETERS_GUIDE.md`

```powershell
python src/week5/run_week5.py ^
  llm.temperature=0.0 ^
  llm.top_p=0.8 ^
  llm.top_k=32
```

---

## 5. 결과 포맷
```
--- Variant: baseline ---
(LLM 응답)

--- Variant: cot ---
(체인 오브 텍스트 응답)
...

--- [간단 비교 지표] ---
Variant              Chars   Lines    JSON?   Steps?
baseline               135       6        N        N
cot                    220       9        N        Y
...
```

Analytics 열 설명:
- `Chars`: 응답 글자 수
- `Lines`: 줄 수
- `JSON?`: JSON 형식 여부
- `Steps?`: 단계(1., Step 등) 언급 여부

---

## 6. 프롬프트 작성 팁
- **System 프롬프트**: 역할, 말투, 출력 형식 명시  
- **User 프롬프트**: 구체적인 질문/요청, 길이 제한 등 포함  
- **Few-shot 예시**: 질문/답변 짝을 넣으면 출력 일관성 향상  
- **구조화된 출력**: JSON 등 기계 가독성 높여 후처리 용이

---

## 7. 체크리스트
- [ ] `GOOGLE_API_KEY` 환경 변수 설정  
- [ ] 모델 이름이 실제로 지원되는 Gemini 버전인지 확인 (`gemini-2.5-flash` 등)  
- [ ] 실행 후 각 프롬프트 응답과 비교 지표가 출력  
- [ ] `output.save_path` 지정 시 파일 생성 확인  
- [ ] 실험 결과를 문서화하거나 CSV로 추가 저장 여부 결정

---

## 8. 추가 실험 아이디어
- 응답 길이 제한: `system`에 “XX자로 요약” 명시  
- 역할 강조: 전문가/초보자/감정 분석 등 상황에 따라 변화  
- 모델 비교: `gemini-1.5-pro`, `gemini-1.0-pro` 등과 응답 품질 비교  
- 자동화: `experiment_logger`와 결합해 여러 프롬프트 조합을 CSV로 로깅

---

## 9. LangGraph 데모 (선택 기능)

Week5에는 LangGraph 기반 RAG 데모가 포함되어 있습니다.

### 7.1 설정
`conf/week5.yaml`의 `langgraph` 섹션에서 활성화:
```yaml
langgraph:
  enabled: true
  index_dir: ../../data/processed/index  # 인덱스 경로
  retrieval_k: 5
  max_context_docs: 4
  demo_questions:
    - "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"
```

### 7.2 실행
프롬프트 튜닝 실행 후 자동으로 LangGraph 데모가 실행됩니다.
- 인덱스 경로가 자동으로 탐색됩니다 (`metadata.json` 포함 디렉토리)
- 설정된 질문들에 대해 RAG 응답을 생성하고 참고 문서를 미리보기로 표시합니다.

### 7.3 비활성화
```powershell
python src/week5/run_week5.py langgraph.enabled=false
```

---

## 10. 실제 실행 결과 요약

- 테스트 스크립트: `python scripts/test_new_features.py`
- 결과 JSON: `outputs/feature_tests/test_results_1763105331.json`
- 요약 (2024-11-14)

| 실험 | 설정 | 메모 |
|------|------|------|
| MMR vs 유사도 | LangChain DenseRetriever | MMR이 0.6초 빠르고 답변이 38% 더 짧음 |
| LLM 파라미터 | 5가지 조합 | `temperature=0.0` 조합이 가장 빠름 (9.58초) |
| LangGraph 조건부 분기 | `reretrieve_threshold=0.3` | 재검색 1회, 응답 품질 안정 |

- 상세 리포트: `docs/results/ACTUAL_EXECUTION_RESULTS.md`

---

## 11. 다음 단계 예고
- Week6에서 FastAPI 서버로 RAG 체인을 노출하고,  
- Week7에서 Dash UI로 사용자와 상호작용하는 인터페이스를 구축합니다.

