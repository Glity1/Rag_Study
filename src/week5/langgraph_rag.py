"""LangGraph 기반 RAG 플로우 구성 유틸리티."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, TypedDict

from langchain.schema import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph


class RAGState(TypedDict, total=False):
    """그래프 실행 중 공유되는 상태."""

    question: str
    documents: List[Document]
    context: str
    answer: str
    retrieval_count: int  # 재검색 횟수
    needs_reretrieve: bool  # 재검색 필요 여부
    keywords_detected: List[str]  # 감지된 키워드


def _format_documents(docs: Iterable[Document]) -> str:
    """LLM 프롬프트용 컨텍스트 문자열을 생성한다."""

    formatted = []
    for idx, doc in enumerate(docs, start=1):
        meta = doc.metadata or {}
        doc_id = meta.get("doc_id", f"doc_{idx:02d}")
        formatted.append(f"[{idx}] ({doc_id}) {doc.page_content}")
    return "\n\n".join(formatted)


def build_rag_graph(
    llm: BaseChatModel,
    retriever: BaseRetriever,
    *,
    max_context_docs: int = 4,
    enable_conditional_branching: bool = False,
    reretrieve_threshold: float = 0.3,  # 문서 관련성 임계값
    max_reretrieves: int = 1,  # 최대 재검색 횟수
    keyword_prompts: dict[str, str] = None,  # 키워드별 프롬프트 템플릿
) -> Runnable:
    """
    LLM과 리트리버를 연결한 LangGraph RAG 플로우를 생성한다.
    
    Args:
        llm: LLM 모델
        retriever: 검색기
        max_context_docs: 최대 컨텍스트 문서 수
        enable_conditional_branching: 조건부 분기 활성화 여부
        reretrieve_threshold: 재검색 임계값 (문서 관련성 점수)
        max_reretrieves: 최대 재검색 횟수
        keyword_prompts: 키워드별 프롬프트 템플릿 (예: {"긴급": "긴급 상황에 대한 답변입니다..."})
    """
    if keyword_prompts is None:
        keyword_prompts = {}

    workflow: StateGraph = StateGraph(RAGState)

    def retrieve_node(state: RAGState) -> RAGState:
        """문서 검색 노드"""
        question = state.get("question", "")
        retrieval_count = state.get("retrieval_count") or 0
        
        # 재검색 시 쿼리 확장 (간단한 예시)
        if retrieval_count > 0:
            # 재검색 시 더 구체적인 키워드 추가
            question = f"{question} (상세 검색)"
        
        documents = retriever.get_relevant_documents(question)[:max_context_docs]
        return RAGState(
            documents=documents,
            retrieval_count=retrieval_count + 1,
        )

    def check_relevance_node(state: RAGState) -> str:
        """문서 관련성 판단 노드 (조건부 분기용)"""
        if not enable_conditional_branching:
            return "generate"
        
        documents = state.get("documents", [])
        if not documents:
            return "generate"  # 문서가 없으면 그냥 생성
        
        # 간단한 관련성 판단: 문서 수와 길이 기반
        # 실제로는 더 정교한 방법 사용 가능 (예: LLM으로 관련성 평가)
        total_length = sum(len(doc.page_content) for doc in documents)
        avg_length = total_length / len(documents) if documents else 0
        
        # 관련성 점수 계산 (간단한 휴리스틱)
        relevance_score = min(avg_length / 100.0, 1.0)  # 평균 길이 기반
        
        retrieval_count = state.get("retrieval_count") or 0
        max_reretrieves_int = int(max_reretrieves) if max_reretrieves is not None else 1
        needs_reretrieve = (
            relevance_score < reretrieve_threshold 
            and retrieval_count < max_reretrieves_int
        )
        
        if needs_reretrieve:
            return "retrieve"  # 재검색
        else:
            return "generate"  # 답변 생성

    def detect_keywords_node(state: RAGState) -> RAGState:
        """키워드 감지 노드"""
        question = state.get("question", "")
        detected_keywords = []
        
        for keyword in keyword_prompts.keys():
            if keyword in question:
                detected_keywords.append(keyword)
        
        return RAGState(keywords_detected=detected_keywords)

    def generate_node(state: RAGState) -> RAGState:
        """답변 생성 노드"""
        question = state.get("question", "")
        documents = state.get("documents", [])
        keywords = state.get("keywords_detected", [])
        context_text = _format_documents(documents) if documents else "관련 문서를 찾지 못했습니다."

        # 키워드 기반 프롬프트 선택
        base_prompt = (
            "당신은 주어진 참고 문서를 활용해 질문에 답하는 전문가입니다.\n"
            "가능하면 문서의 핵심을 인용하여 응답하고, 근거가 없으면 모른다고 말하세요.\n\n"
        )
        
        # 키워드가 감지되면 해당 프롬프트 사용
        if keywords and keyword_prompts:
            keyword = keywords[0]  # 첫 번째 키워드 사용
            custom_prompt = keyword_prompts.get(keyword, "")
            if custom_prompt:
                base_prompt = custom_prompt + "\n\n"

        prompt = (
            f"{base_prompt}"
            f"질문:\n{question}\n\n"
            f"참고 문서:\n{context_text}\n\n"
            "답변:"
        )

        response = llm.invoke(prompt)
        answer_text = getattr(response, "content", str(response))
        return RAGState(answer=answer_text, context=context_text)

    # 노드 추가
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("detect_keywords", detect_keywords_node)
    workflow.add_node("generate", generate_node)
    
    # 엔트리 포인트 설정
    workflow.set_entry_point("detect_keywords")
    
    if enable_conditional_branching:
        # 조건부 분기 활성화 시
        workflow.add_edge("detect_keywords", "retrieve")
        workflow.add_conditional_edges(
            "retrieve",
            check_relevance_node,
            {
                "retrieve": "retrieve",  # 재검색
                "generate": "generate",  # 답변 생성
            }
        )
        workflow.add_edge("generate", END)
    else:
        # 기본 선형 플로우
        workflow.add_edge("detect_keywords", "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

    return workflow.compile()


def run_rag(app: Runnable, question: str) -> RAGState:
    """컴파일된 LangGraph RAG 앱을 실행하고 상태를 반환한다."""

    state = app.invoke({"question": question})
    return RAGState(state)


def preview_documents(docs: Iterable[Document], limit: int = 3) -> List[str]:
    """콘솔 출력용 문서 미리보기 텍스트를 생성한다."""

    previews: List[str] = []
    for idx, doc in enumerate(docs):
        if idx >= limit:
            break
        snippet = doc.page_content[:160].replace("\n", " ")
        suffix = "…" if len(doc.page_content) > 160 else ""
        meta = doc.metadata or {}
        previews.append(f"- doc_id={meta.get('doc_id', f'doc_{idx+1:02d}')}: {snippet}{suffix}")
    return previews

