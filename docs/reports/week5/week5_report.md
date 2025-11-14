# Week 5 Report — 프롬프트 튜닝 결과

## 1. 학습 목표
- Gemini LLM을 대상으로 다양한 프롬프트 변형 실험
- 응답 품질(관련성, 구조화 정도, 길이)을 간단히 정량 비교
- 최적 프롬프트 세트를 Week6 API 기본값으로 선별

---

## 2. 실행 요약

| 항목 | 내용 |
|------|------|
| 실행 명령 | `python src/week5/run_week5.py` |
| Hydra 설정 | `conf/week5.yaml` (`variants` 4종, `langgraph` 데모 포함) |
| 사용 모델 | `gemini-2.5-flash` |
| 출력 | 콘솔 로그 + (옵션) `output.save_path` + LangGraph 데모 |

실험 명령 예  
```powershell
# 기본 4가지 프롬프트 변형 실행
python src/week5/run_week5.py

# 결과 저장
python src/week5/run_week5.py output.save_path=data/processed/week5_report.txt

# 모델 온도 조정
python src/week5/run_week5.py llm.temperature=0.0

# LangGraph 데모 비활성화
python src/week5/run_week5.py langgraph.enabled=false

# LangGraph 조건부 분기 활성화
python src/week5/run_week5.py langgraph.enable_conditional_branching=true

# LLM 파라미터 조정
python src/week5/run_week5.py llm.temperature=0.7 llm.top_p=0.9 llm.top_k=40
```

**LangGraph 데모**: 프롬프트 튜닝 실행 후 자동으로 LangGraph 기반 RAG 데모가 실행됩니다. `conf/week5.yaml`의 `langgraph` 섹션에서 설정할 수 있습니다.

**주요 기능**:
- ✅ **조건부 분기**: 문서 관련성 기반 자동 재검색 (`enable_conditional_branching=true`)
- ✅ **키워드 기반 프롬프트 분기**: 질문 유형에 따른 프롬프트 자동 선택
- ✅ **LLM 파라미터 조율**: `temperature`, `top_p`, `top_k` 지원

---

## 3. 프롬프트 변형 비교

| Variant | 특징 | 응답 길이(평균) | JSON 형식 | 단계 표기 |
|---------|------|----------------:|-----------|-----------|
| baseline | 일반 설명형 | 135 chars | N | N |
| cot | 체인-오브-씽킹 | 220 chars | N | Y |
| structured | JSON 출력 | 290 chars | Y | N |
| few_shot | 전문가 톤 + 예시 | 205 chars | N | Y |

관찰 사항  
- `structured`는 JSON 형태라 후처리 용이, 다만 길이가 가장 김  
- `cot`/`few_shot`은 단계적 서술을 자연스럽게 포함  
- Temperature 0.0으로 낮추면 응답 일관성 증가 (특히 `structured`)

---

## 4. 품질 메모 (주관 평가)

| Variant | 관련성 | 근거 언급 | 톤/스타일 | 비고 |
|---------|--------|-----------|-----------|------|
| baseline | 보통 | 낮음 | 친근 | 간단 요약에 적합 |
| cot | 높음 | 중간 | 단계적 | QA 설명형에 적합 |
| structured | 높음 | 매우 높음 | 형식적 | API 응답 가공용 |
| few_shot | 높음 | 중간 | 전문가 | 엔터프라이즈 톤 |

환각 사례는 관찰되지 않았으며, 질문이 불명확할 때 `cot` 변형이 “문서를 확인할 수 없다”는 답변을 주어 안정성이 더 높았다.

---

## 5. 산출물 및 로그
- `outputs/week5/20251112_145931/run_week5.log` (Hydra 로그)  
- `data/processed/week5_report.txt` (옵션 저장)  
- 코드 수정: `PromptVariant.examples` 지원 및 Analytics 표 자동 생성

---

## 6. 다음 단계 & 적용 계획
1. Week6 FastAPI 기본 프롬프트를 `structured` 변형으로 교체  
2. `cot` 프롬프트는 UI(Dash)에서 “자세히 설명” 옵션으로 제공 예정  
3. 향후 자동화:
   ```powershell
   python src/week5/run_week5.py \
     variants='[{"name":"guardrail","system":"...","user":"..."}]' \
     output.save_path=/app/data/week5_guardrail.txt
   ```
4. 응답 품질 검증을 위해 평가 지표(관련성, 톤)를 CSV로 로깅하는 스크립트 추가 예정
