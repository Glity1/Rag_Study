# LangChain vs LangGraph 비교 분석

## 📊 현재 프로젝트에서의 사용

### Week4: LangChain (RetrievalQA)
```python
# week4/rag_chain.py
chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
)
answer = chain.run(question)
```

### Week5: LangGraph (StateGraph)
```python
# week5/langgraph_rag.py
workflow = StateGraph(RAGState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
graph_app = workflow.compile()
state = graph_app.invoke({"question": question})
```

---

## 🔍 주요 차이점

### 1. **구조적 차이**

#### LangChain (Week4)
- **선형 체인 (Linear Chain)**: 단순한 순차 실행
- **블랙박스**: 내부 동작이 추상화되어 있음
- **간단한 사용**: `chain.run(question)` 한 줄로 실행

```python
# 내부적으로는 이렇게 동작 (추상화됨)
question → retriever → documents → LLM → answer
```

#### LangGraph (Week5)
- **그래프 구조 (Graph Structure)**: 노드와 엣지로 명시적 정의
- **명시적 제어**: 각 단계를 노드로 분리하여 제어 가능
- **상태 관리**: `RAGState`로 중간 상태를 추적

```python
# 명시적으로 노드와 엣지 정의
retrieve_node → generate_node → END
     ↓              ↓
  documents      answer
```

---

### 2. **현재 프로젝트에서의 장점 비교**

#### LangGraph의 장점 (현재 구현 기준)

##### ✅ 1. **명시적 상태 관리**
```python
class RAGState(TypedDict, total=False):
    question: str
    documents: List[Document]  # 검색된 문서
    context: str                # 포맷된 컨텍스트
    answer: str                 # 최종 답변
```

**장점**: 
- 각 단계의 중간 결과를 명확히 추적 가능
- 디버깅 시 어느 단계에서 문제가 발생했는지 파악 용이
- Week5에서 `preview_documents()`로 검색된 문서를 미리보기 가능

**LangChain**: 중간 상태에 접근하기 어려움 (내부 처리)

##### ✅ 2. **확장성과 유연성**
```python
# 현재는 단순하지만, 쉽게 확장 가능
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

# 나중에 추가 가능한 예시:
# workflow.add_node("rerank", rerank_node)      # 재순위화
# workflow.add_node("validate", validate_node)  # 검증
# workflow.add_node("format", format_node)      # 포맷팅
```

**장점**:
- 복잡한 워크플로우로 확장하기 쉬움
- 조건부 분기, 루프, 병렬 처리 등 추가 가능

**LangChain**: `RetrievalQA`는 고정된 구조로 확장이 제한적

##### ✅ 3. **시각화 가능**
```python
# LangGraph는 그래프 구조이므로 시각화 가능
# (현재 코드에는 없지만 가능)
from langgraph.graph import StateGraph
# 그래프를 이미지로 저장하거나 UI로 표시 가능
```

**장점**: 워크플로우를 시각적으로 이해하고 공유 가능

##### ✅ 4. **중간 결과 접근**
```python
# Week5에서 사용 예시
state = run_rag(graph_app, question)
answer = state.get("answer", "(응답 없음)")
docs = state.get("documents", [])  # 검색된 문서 접근 가능!
previews = preview_documents(docs, limit=preview_limit)
```

**장점**: 
- 검색된 문서를 사용자에게 보여줄 수 있음
- 각 단계의 결과를 로깅하거나 분석 가능

**LangChain**: `chain.run()`은 최종 답변만 반환

---

### 3. **현재 프로젝트의 복잡도 분석**

#### 현재 LangGraph 구현: **조건부 분기 포함 그래프**

```python
# 기본 모드
retrieve → generate → END

# 조건부 분기 모드 (enable_conditional_branching=true)
retrieve → check_relevance → (조건부) → retrieve (재검색) 또는 generate
generate → detect_keywords → (조건부) → keyword_prompt 또는 default_prompt
```

**복잡도**: ⭐⭐⭐☆☆ (3/5) - 중간 수준

**이유**:
1. 기본 2노드 구조 (retrieve → generate)
2. ✅ **조건부 분기 구현됨**: 문서 관련성 기반 재검색
3. ✅ **키워드 기반 프롬프트 분기**: 질문 유형별 다른 프롬프트 사용
4. 루프 없음 (재검색은 조건부 분기로 처리)
5. 병렬 처리 없음

#### LangChain 구현: **더 단순**

```python
RetrievalQA.from_chain_type()  # 내부적으로 처리
```

**복잡도**: ⭐☆☆☆☆ (1/5) - 가장 단순

---

## 🚀 LangGraph가 더 유용한 경우

### 현재 프로젝트에서는 **아직 단순하지만**, 다음 기능 추가 시 큰 장점:

#### 1. **재검색 (Re-ranking) 추가**
```python
def rerank_node(state: RAGState) -> RAGState:
    # 검색된 문서를 재순위화
    documents = rerank(state["question"], state["documents"])
    return RAGState(documents=documents)

workflow.add_node("rerank", rerank_node)
workflow.add_edge("retrieve", "rerank")
workflow.add_edge("rerank", "generate")
```

#### 2. **조건부 분기 (답변 품질 검증)**
```python
def should_reretrieve(state: RAGState) -> str:
    # 답변 품질이 낮으면 재검색
    if state.get("answer_confidence", 0) < 0.7:
        return "retrieve"
    return "end"

workflow.add_conditional_edges(
    "generate",
    should_reretrieve,
    {"retrieve": "retrieve", "end": END}
)
```

#### 3. **다중 검색 전략**
```python
def dense_retrieve_node(state: RAGState) -> RAGState:
    # Dense 검색
    docs1 = dense_retriever.get_relevant_documents(state["question"])
    return RAGState(dense_docs=docs1)

def keyword_retrieve_node(state: RAGState) -> RAGState:
    # 키워드 검색
    docs2 = keyword_retriever.get_relevant_documents(state["question"])
    return RAGState(keyword_docs=docs2)

def merge_node(state: RAGState) -> RAGState:
    # 두 검색 결과 병합
    all_docs = state["dense_docs"] + state["keyword_docs"]
    return RAGState(documents=all_docs)

# 병렬 실행 후 병합
workflow.add_edge("dense_retrieve", "merge")
workflow.add_edge("keyword_retrieve", "merge")
```

#### 4. **에러 처리 및 재시도**
```python
def generate_with_retry(state: RAGState) -> RAGState:
    try:
        return generate_node(state)
    except Exception as e:
        if state.get("retry_count", 0) < 3:
            return RAGState(retry_count=state.get("retry_count", 0) + 1)
        raise
```

---

## 📈 현재 프로젝트의 평가

### 현재 상태: **단순하지만 확장 가능한 구조 → 실제로 확장됨**

#### LangChain (Week4) 사용 이유:
- ✅ **간단한 RAG 체인**에 적합
- ✅ **빠른 프로토타이핑**
- ✅ **Week6 FastAPI 서버**에서 안정적으로 사용
- ✅ **학습 목적**: 기본 RAG 이해
- ✅ **MMR 검색 지원**: 다양성 있는 검색 결과 제공 (`use_mmr`, `mmr_diversity` 파라미터)
- ✅ **LLM 파라미터 조율**: `temperature`, `top_p`, `top_k` 지원

#### LangGraph (Week5) 사용 이유:
- ✅ **확장 가능한 구조** 제공
- ✅ **중간 상태 접근**으로 디버깅/분석 용이
- ✅ **실제 확장 완료**: 조건부 분기, 재검색 기능 구현
  - **조건부 재검색**: 문서 관련성 점수 기반 자동 재검색
  - **키워드 기반 프롬프트 분기**: 질문 유형에 따른 프롬프트 자동 선택
- ✅ **학습 목적**: 그래프 기반 워크플로우 이해

---

## 🎯 결론

### 현재 프로젝트에서:

1. **복잡도**: ⭐⭐☆☆☆ (단순)
   - 현재는 단순한 선형 그래프
   - LangChain과 거의 동일한 기능

2. **LangGraph의 장점**:
   - ✅ **명시적 상태 관리**: 중간 결과 접근 가능
   - ✅ **확장성**: 복잡한 워크플로우로 쉽게 확장
   - ✅ **디버깅**: 각 단계 추적 용이
   - ✅ **문서 미리보기**: 검색된 문서를 사용자에게 표시 가능

3. **언제 LangGraph가 더 좋은가?**
   - 복잡한 워크플로우가 필요할 때
   - 중간 결과를 추적해야 할 때
   - 조건부 분기, 루프, 병렬 처리가 필요할 때
   - 워크플로우를 시각화하고 싶을 때

4. **언제 LangChain이 더 좋은가?**
   - 단순한 RAG 체인이면 충분할 때
   - 빠른 프로토타이핑이 필요할 때
   - 내부 동작을 신경 쓰지 않아도 될 때

---

## 💡 실전 예시: 복잡한 RAG 워크플로우

### LangGraph로 구현 가능한 고급 RAG:

```python
# 1. 다중 검색 (병렬)
dense_retrieve → merge ← keyword_retrieve
                    ↓
                 rerank
                    ↓
                 generate
                    ↓
              validate_answer
                    ↓
         (품질 낮으면) → reretrieve
         (품질 좋으면) → format → END
```

이런 복잡한 흐름은 **LangGraph 없이는 구현하기 어렵습니다**.

---

## 📝 요약

| 항목          | LangChain (Week4) | LangGraph (Week5) |
|--------------|-------------------|-------------------|
| **복잡도**    | ⭐☆☆☆☆ (1/5)    | ⭐⭐⭐☆☆ (3/5)  |
| **확장성**    | ⭐⭐⭐☆☆ (MMR 지원) | ⭐⭐⭐⭐⭐     |
| **상태 접근** | ❌ 어려움          | ✅ 쉬움           |
| **디버깅**    | ⭐⭐☆☆☆         | ⭐⭐⭐⭐☆      |
| **학습 곡선** | ⭐⭐☆☆☆         | ⭐⭐⭐☆☆       |
| **현재 사용** | Week4, Week6 (MMR, LLM 파라미터 지원) | Week5 (조건부 분기, 재검색) |
| **고급 기능** | MMR 검색, LLM 파라미터 조율 | 조건부 분기, 키워드 프롬프트, 재검색 |

