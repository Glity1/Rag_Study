# LLM 파라미터 조율 가이드

## 개요

LLM의 출력 품질과 다양성을 조절하기 위한 주요 파라미터들:
- **temperature**: 출력의 창의성/무작위성 조절
- **top_p**: 누적 확률 기반 샘플링 (nucleus sampling)
- **top_k**: 상위 K개 토큰 중에서만 선택

## 파라미터 설명

### 1. Temperature (온도)

**범위**: 0.0 ~ 2.0 (일반적으로 0.0 ~ 1.0)

**동작 방식**:
- 낮은 값 (0.0 ~ 0.3): 결정적이고 일관된 답변, 사실 기반 응답에 적합
- 중간 값 (0.4 ~ 0.7): 균형잡힌 답변, 일반적인 대화에 적합
- 높은 값 (0.8 ~ 1.0): 창의적이고 다양한 답변, 창작에 적합

**사용 예시**:
```python
# 사실 기반 답변 (낮은 temperature)
chain = build_rag_chain(
    index_dir=Path("data/processed/index/..."),
    temperature=0.0,  # 일관된 답변
)

# 창의적인 답변 (높은 temperature)
chain = build_rag_chain(
    index_dir=Path("data/processed/index/..."),
    temperature=0.8,  # 다양한 답변
)
```

### 2. Top-p (Nucleus Sampling)

**범위**: 0.0 ~ 1.0

**동작 방식**:
- 확률이 높은 토큰부터 누적하여 p 값에 도달할 때까지의 토큰들만 고려
- 예: top_p=0.9이면 누적 확률 90%에 해당하는 토큰들만 고려

**특징**:
- 동적으로 고려할 토큰 수가 결정됨
- top_k와 함께 사용 가능 (둘 다 적용되면 더 엄격한 필터링)

**사용 예시**:
```python
chain = build_rag_chain(
    index_dir=Path("data/processed/index/..."),
    temperature=0.7,
    top_p=0.9,  # 상위 90% 확률 토큰만 고려
)
```

### 3. Top-k

**범위**: 1 ~ 모델의 어휘 크기

**동작 방식**:
- 확률이 높은 상위 K개 토큰만 고려
- 예: top_k=40이면 상위 40개 토큰만 고려

**특징**:
- 고정된 수의 토큰만 고려
- top_p와 함께 사용 가능

**사용 예시**:
```python
chain = build_rag_chain(
    index_dir=Path("data/processed/index/..."),
    temperature=0.7,
    top_k=40,  # 상위 40개 토큰만 고려
)
```

## 파라미터 조합 가이드

### 시나리오별 권장 설정

| 시나리오 | temperature | top_p | top_k | 설명 |
|---------|------------|-------|-------|------|
| **사실 기반 QA** | 0.0 ~ 0.2 | null | null | 정확하고 일관된 답변 |
| **균형잡힌 대화** | 0.4 ~ 0.6 | 0.9 | null | 자연스러운 대화 |
| **창의적 답변** | 0.7 ~ 0.9 | 0.95 | 50 | 다양한 관점의 답변 |
| **엄격한 필터링** | 0.5 | 0.9 | 40 | top_p + top_k 조합 |

## 사용 방법

### Week4에서 사용

#### Hydra 설정 (`conf/week4.yaml`)

```yaml
rag:
  temperature: 0.0
  top_p: 0.9
  top_k_llm: 40
```

#### 명령줄에서 실행

```bash
# temperature만 조정
python src/week4/run_week4.py rag.temperature=0.5

# top_p 추가
python src/week4/run_week4.py rag.temperature=0.5 rag.top_p=0.9

# top_k 추가
python src/week4/run_week4.py rag.temperature=0.5 rag.top_p=0.9 rag.top_k_llm=40
```

### Week5에서 사용

#### Hydra 설정 (`conf/week5.yaml`)

```yaml
llm:
  model_name: gemini-2.5-flash
  temperature: 0.2
  top_p: 0.9
  top_k: 40

langgraph:
  temperature: 0.1
  top_p: 0.95
  top_k: 50
```

#### 명령줄에서 실행

```bash
# 프롬프트 튜닝에 파라미터 적용
python src/week5/run_week5.py llm.temperature=0.5 llm.top_p=0.9 llm.top_k=40

# LangGraph에 파라미터 적용
python src/week5/run_week5.py langgraph.temperature=0.3 langgraph.top_p=0.9
```

### Week6 API 서버에서 사용

#### Hydra 설정 (`conf/week6.yaml`)

```yaml
rag:
  model_name: gemini-2.5-flash
  temperature: 0.0
  top_p: null
  top_k: null
```

#### 명령줄에서 실행

```bash
# API 서버에 파라미터 적용
python src/week6/run_week6.py rag.temperature=0.5 rag.top_p=0.9 rag.top_k=40
```

## 실험 예시

### 실험 1: Temperature 영향

```bash
# 낮은 temperature (일관된 답변)
python src/week4/run_week4.py rag.temperature=0.0 rag.question="코로나 대응 전략은?"

# 높은 temperature (다양한 답변)
python src/week4/run_week4.py rag.temperature=0.8 rag.question="코로나 대응 전략은?"
```

### 실험 2: Top-p 영향

```bash
# 엄격한 필터링 (top_p=0.7)
python src/week4/run_week4.py rag.temperature=0.5 rag.top_p=0.7

# 느슨한 필터링 (top_p=0.95)
python src/week4/run_week4.py rag.temperature=0.5 rag.top_p=0.95
```

### 실험 3: Top-k 영향

```bash
# 적은 토큰 고려 (top_k=20)
python src/week4/run_week4.py rag.temperature=0.5 rag.top_k_llm=20

# 많은 토큰 고려 (top_k=100)
python src/week4/run_week4.py rag.temperature=0.5 rag.top_k_llm=100
```

## 파라미터 간 상호작용

### Temperature vs Top-p/Top-k

- **Temperature가 낮을 때**: top_p, top_k의 영향이 작음 (이미 결정적)
- **Temperature가 높을 때**: top_p, top_k로 다양성을 제어 가능

### Top-p vs Top-k

- **둘 다 설정**: 더 엄격한 필터링 (둘 다 만족해야 함)
- **하나만 설정**: 해당 조건만 적용

## 주의사항

1. **Gemini API 지원**: Gemini API는 top_p, top_k를 지원하지만, 모든 모델이 동일하게 지원하지 않을 수 있음
2. **파라미터 이름**: 
   - Week4: `top_k_llm` (검색 top_k와 구분)
   - Week5/Week6: `top_k` (LLM 파라미터)
3. **기본값**: null로 설정하면 모델의 기본값 사용

## 실제 실행 결과

### 테스트 환경
- **테스트 날짜**: 2024-11-14
- **인덱스**: `data/processed/index/20201231-34-63/recursive`
- **질문**: "그랜드코리아레저의 코로나 대응 전략을 간단히 요약해줘."

### 파라미터별 성능 비교

| 파라미터 조합 | 응답 시간 | 답변 길이 | 답변 특징 |
|--------------|----------|----------|----------|
| **기본값** (temperature=0.0) | 9.58초 | 619자 | 일관적, 사실 기반 |
| **temperature=0.5** | 11.34초 | 565자 | 균형잡힌, 간결 |
| **temperature=0.5, top_p=0.9** | 10.21초 | 584자 | 엄격한 필터링, 균형 |
| **temperature=0.5, top_k=40** | 11.28초 | 664자 | 중간 필터링, 상세 |
| **temperature=0.5, top_p=0.9, top_k=40** | 10.12초 | 685자 | 엄격한 필터링, 상세 |

### 관찰 사항

1. **응답 시간**:
   - 기본값 (temperature=0.0)이 가장 빠름 (9.58초)
   - temperature=0.5일 때는 10~11초 범위
   - top_p와 top_k 조합이 응답 시간에 미치는 영향은 미미함

2. **답변 길이**:
   - temperature=0.0: 619자 (중간)
   - temperature=0.5: 565자 (가장 짧음)
   - top_k=40 추가 시: 664~685자 (더 상세)
   - top_p와 top_k 조합 시 가장 긴 답변 (685자)

3. **답변 품질**:
   - **기본값 (temperature=0.0)**: 일관적이고 사실 기반, 구조화된 답변
   - **temperature=0.5**: 더 자연스럽고 균형잡힌 답변
   - **top_p=0.9 추가**: 답변의 일관성 향상
   - **top_k=40 추가**: 더 상세하고 포괄적인 답변
   - **top_p + top_k 조합**: 가장 상세하고 구조화된 답변

### 권장 설정

| 사용 목적 | 권장 파라미터 | 이유 |
|----------|-------------|------|
| **빠른 사실 기반 답변** | temperature=0.0 | 가장 빠르고 일관적 |
| **균형잡힌 답변** | temperature=0.5 | 자연스럽고 적절한 길이 |
| **상세한 분석** | temperature=0.5, top_k=40 | 더 포괄적인 정보 제공 |
| **엄격한 품질 제어** | temperature=0.5, top_p=0.9, top_k=40 | 가장 상세하고 구조화된 답변 |

## 성능 고려사항

- **Temperature**: 낮을수록 빠르고 일관적 (테스트 결과: temperature=0.0이 9.58초로 가장 빠름)
- **Top-p/Top-k**: 엄격할수록 계산이 빠를 수 있으나, 실제 응답 시간 차이는 미미함
- **권장**: 사실 기반 QA에는 낮은 temperature, 창의적 작업에는 높은 temperature
- **답변 길이**: top_k를 추가하면 더 상세한 답변 생성 (664~685자)

---

**구현 위치**: 
- `src/week4/rag_chain.py` - `build_rag_chain()` 함수
- `src/week5/prompt_tuning.py` - `PromptTuner` 클래스
- `src/week5/langgraph_rag.py` - `build_rag_graph()` 함수
- `src/week6/api_server.py` - `create_app()` 함수

