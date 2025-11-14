# LangGraph 조건부 분기 가이드

## 개요

LangGraph의 조건부 분기 기능을 활용하여 더 지능적인 RAG 파이프라인을 구현할 수 있습니다. 현재 구현된 기능:

1. **재검색 로직**: 검색된 문서의 관련성이 낮으면 자동으로 재검색
2. **키워드 기반 프롬프트 분기**: 질문에 특정 키워드가 포함되면 다른 프롬프트 사용

## 워크플로우

### 기본 플로우 (조건부 분기 비활성화)
```
START → detect_keywords → retrieve → generate → END
```

### 조건부 분기 활성화 시
```
START → detect_keywords → retrieve → [관련성 판단]
                                    ↓
                          [관련성 낮음] → retrieve (재검색)
                                    ↓
                          [관련성 충분] → generate → END
```

## 사용 방법

### Week5에서 조건부 분기 활성화

#### Hydra 설정 파일 (`conf/week5.yaml`)

```yaml
langgraph:
  enable_conditional_branching: true  # 조건부 분기 활성화
  reretrieve_threshold: 0.3  # 재검색 임계값 (0.0~1.0)
  max_reretrieves: 1  # 최대 재검색 횟수
  keyword_prompts:
    긴급: "긴급 상황에 대한 답변입니다. 빠르고 정확한 정보를 제공하세요."
    상세: "상세한 설명이 필요한 질문입니다. 구체적이고 자세하게 답변하세요."
    요약: "간결하고 핵심적인 요약을 제공하세요."
```

#### 명령줄에서 실행

```bash
# 조건부 분기 활성화
python src/week5/run_week5.py langgraph.enable_conditional_branching=true

# 재검색 임계값 조정
python src/week5/run_week5.py langgraph.enable_conditional_branching=true langgraph.reretrieve_threshold=0.5

# 최대 재검색 횟수 증가
python src/week5/run_week5.py langgraph.enable_conditional_branching=true langgraph.max_reretrieves=2
```

### 코드에서 직접 사용

```python
from src.week5.langgraph_rag import build_rag_graph
from src.week4.rag_chain import DenseRetriever, load_documents_and_vectors
from langchain_google_genai import ChatGoogleGenerativeAI
from pathlib import Path

# 인덱스 로드
index_dir = Path("data/processed/index/20201231-34-63/recursive")
documents, vectors = load_documents_and_vectors(index_dir)
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
retriever = DenseRetriever(documents=documents, vectors=vectors, embedder=embedder, k=5)

# LLM 설정
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# 조건부 분기 활성화된 그래프 생성
graph = build_rag_graph(
    llm=llm,
    retriever=retriever,
    max_context_docs=4,
    enable_conditional_branching=True,
    reretrieve_threshold=0.3,
    max_reretrieves=1,
    keyword_prompts={
        "긴급": "긴급 상황입니다. 빠르고 정확하게 답변하세요.",
        "상세": "상세한 설명을 제공하세요.",
    }
)

# 실행
state = graph.invoke({"question": "긴급 상황에서의 대응 방법은?"})
print(state["answer"])
```

## 재검색 로직

### 관련성 판단 기준

현재 구현은 간단한 휴리스틱을 사용합니다:
- 문서의 평균 길이 기반 점수 계산
- 점수가 `reretrieve_threshold`보다 낮으면 재검색

### 향후 개선 방향

더 정교한 관련성 판단 방법:
1. **LLM 기반 관련성 평가**: 검색된 문서를 LLM으로 평가
2. **유사도 점수 기반**: 검색 유사도 점수의 평균/최소값 사용
3. **키워드 매칭**: 질문의 핵심 키워드가 문서에 포함되는지 확인

## 키워드 기반 프롬프트 분기

### 설정 예시

```yaml
keyword_prompts:
  긴급: |
    긴급 상황에 대한 답변입니다.
    빠르고 정확한 정보를 제공하세요.
    핵심만 간결하게 설명하세요.
  
  상세: |
    상세한 설명이 필요한 질문입니다.
    구체적이고 자세하게 답변하세요.
    예시와 함께 설명하세요.
  
  요약: |
    간결하고 핵심적인 요약을 제공하세요.
    3-5개의 핵심 포인트로 정리하세요.
```

### 동작 방식

1. 질문에서 키워드 감지 (`detect_keywords_node`)
2. 감지된 키워드가 있으면 해당 프롬프트 사용
3. 여러 키워드가 감지되면 첫 번째 키워드 사용

## 상태 관리

`RAGState`에 추가된 필드:

- `retrieval_count`: 재검색 횟수 추적
- `needs_reretrieve`: 재검색 필요 여부 (내부 사용)
- `keywords_detected`: 감지된 키워드 리스트

## 성능 고려사항

- **재검색**: 추가 검색으로 인해 응답 시간이 증가할 수 있음
- **키워드 감지**: 단순 문자열 매칭이므로 매우 빠름
- **권장 사용**: 복잡한 질문이나 다양한 답변 스타일이 필요한 경우

## 실제 실행 결과

### 테스트 환경
- **테스트 날짜**: 2024-11-14
- **인덱스**: `data/processed/index/20201231-34-63/recursive`
- **질문**: "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"

### 기본 플로우 vs 조건부 분기 비교

| 항목 | 기본 플로우 | 조건부 분기 활성화 |
|------|------------|------------------|
| **응답 시간** | 10.97초 | 12.15초 |
| **답변 길이** | 1,223자 | 1,127자 |
| **재검색 횟수** | 1회 | 1회 |
| **키워드 감지** | 없음 | 없음 (키워드 없음) |

### 관찰 사항

1. **응답 시간**: 조건부 분기가 약간 느림 (1.18초 차이)
   - 관련성 판단 로직 추가로 인한 오버헤드
   - 재검색이 발생하지 않아도 관련성 판단 과정에서 시간 소요

2. **답변 품질**: 두 방식 모두 유사한 품질의 답변 생성
   - 기본 플로우: 1,223자 (상세)
   - 조건부 분기: 1,127자 (약간 간결)

3. **재검색**: 이번 테스트에서는 재검색이 발생하지 않음
   - 관련성 점수가 임계값(0.3) 이상이었을 것으로 추정
   - 재검색이 필요한 경우 응답 시간이 더 증가할 수 있음

### 결론

조건부 분기는 **약간의 오버헤드가 있지만 (1.18초), 복잡한 질문이나 낮은 관련성 문서를 다룰 때 유용**합니다. 재검색이 실제로 발생하는 경우 더 정확한 답변을 얻을 수 있지만, 응답 시간은 추가로 증가할 수 있습니다.

## 예시 시나리오

### 시나리오 1: 재검색

```
질문: "코로나 대응 전략"
1차 검색: 관련성 점수 0.25 (임계값 0.3 미만)
→ 재검색 수행
2차 검색: 관련성 점수 0.45 (임계값 초과)
→ 답변 생성
```

### 시나리오 2: 키워드 기반 프롬프트

```
질문: "긴급 상황에서의 대응 방법은?"
키워드 감지: ["긴급"]
→ "긴급 상황에 대한 답변입니다..." 프롬프트 사용
→ 답변 생성
```

### 실제 테스트 결과

```
질문: "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"

[기본 플로우]
- 응답 시간: 10.97초
- 답변 길이: 1,223자
- 재검색 횟수: 1회

[조건부 분기]
- 응답 시간: 12.15초
- 답변 길이: 1,127자
- 재검색 횟수: 1회
- 키워드 감지: [] (키워드 없음)
```

## 향후 확장 가능성

1. **다중 재검색 전략**: 쿼리 확장, 다른 검색 파라미터 사용
2. **LLM 기반 관련성 평가**: 더 정교한 관련성 판단
3. **동적 프롬프트 생성**: 키워드 조합에 따른 프롬프트 생성
4. **병렬 검색**: 여러 검색 전략을 병렬로 실행 후 통합

---

**구현 위치**: `src/week5/langgraph_rag.py` - `build_rag_graph()` 함수

