"""4주차 RAG 체인 구성 스크립트."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

import numpy as np
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

load_dotenv()


def load_documents_and_vectors(index_dir: Path) -> tuple[List[Document], np.ndarray]:
    metadata_path = index_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"metadata.json을 찾을 수 없습니다: {metadata_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not metadata:
        raise ValueError(f"{metadata_path}에 문서가 없습니다.")

    documents = [Document(page_content=item["text"], metadata={"doc_id": item["doc_id"]}) for item in metadata]
    vectors = np.array([item["vector"] for item in metadata], dtype="float32")
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
    return documents, vectors


class DenseRetriever(BaseRetriever):
    """간단한 내장 벡터 검색기."""

    documents: List[Document] = Field(default_factory=list)
    vectors: np.ndarray = Field(...)
    embedder: HuggingFaceEmbeddings
    k: int = 5
    use_mmr: bool = False
    mmr_diversity: float = 0.5  # lambda 파라미터: 0.0=유사도만, 1.0=다양성만

    def _get_relevant_documents(self, query: str) -> List[Document]:
        query_vec = np.array(self.embedder.embed_query(query), dtype="float32")
        query_vec /= np.linalg.norm(query_vec) + 1e-10
        sims = self.vectors @ query_vec
        
        if self.use_mmr:
            indices = self._mmr_search(query_vec, sims, self.k, self.mmr_diversity)
        else:
            # 기본 유사도 검색
            indices = np.argsort(sims)[::-1][: self.k]
        
        return [self.documents[i] for i in indices]

    def _mmr_search(
        self, 
        query_vec: np.ndarray, 
        similarities: np.ndarray, 
        k: int, 
        lambda_param: float
    ) -> np.ndarray:
        """
        MMR (Maximal Marginal Relevance) 검색 알고리즘.
        
        MMR은 유사도와 다양성을 모두 고려하여 검색 결과의 다양성을 높입니다.
        lambda_param: 0.0에 가까울수록 유사도 우선, 1.0에 가까울수록 다양성 우선
        """
        selected_indices = []
        candidate_indices = np.argsort(similarities)[::-1]  # 유사도 순으로 정렬
        
        # 첫 번째 문서는 가장 유사한 것으로 선택
        if len(candidate_indices) > 0:
            selected_indices.append(candidate_indices[0])
            candidate_indices = candidate_indices[1:]
        
        # 나머지 문서는 MMR 점수로 선택
        while len(selected_indices) < k and len(candidate_indices) > 0:
            best_score = -np.inf
            best_idx = None
            
            for candidate_idx in candidate_indices:
                # 유사도 점수
                relevance = similarities[candidate_idx]
                
                # 이미 선택된 문서들과의 최대 유사도 (다양성 측정)
                max_sim_to_selected = 0.0
                if selected_indices:
                    candidate_vec = self.vectors[candidate_idx]
                    selected_vecs = self.vectors[selected_indices]
                    sims_to_selected = selected_vecs @ candidate_vec
                    max_sim_to_selected = np.max(sims_to_selected)
                
                # MMR 점수 = lambda * relevance - (1 - lambda) * max_sim_to_selected
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = candidate_idx
            
            if best_idx is not None:
                selected_indices.append(best_idx)
                candidate_indices = candidate_indices[candidate_indices != best_idx]
            else:
                break
        
        return np.array(selected_indices)

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)


def build_rag_chain(
    index_dir: Path,
    google_api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    retrieval_k: int = 5,
    use_mmr: bool = False,
    mmr_diversity: float = 0.5,
    temperature: float = 0.0,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
) -> RetrievalQA:
    """
    RAG 체인을 구성한다.
    
    Args:
        index_dir: 인덱스 디렉토리 경로
        google_api_key: Google API 키 (None이면 환경 변수 사용)
        model_name: LLM 모델 이름
        retrieval_k: 검색할 문서 수
        use_mmr: MMR 검색 사용 여부
        mmr_diversity: MMR 다양성 파라미터 (0.0=유사도만, 1.0=다양성만)
        temperature: LLM temperature 파라미터
        top_p: LLM top_p 파라미터 (None이면 기본값 사용)
        top_k: LLM top_k 파라미터 (None이면 기본값 사용)
    """
    documents, vectors = load_documents_and_vectors(index_dir)
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    key = google_api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise EnvironmentError("GOOGLE_API_KEY 환경 변수가 필요합니다.")

    # LLM 파라미터 설정
    llm_kwargs = {
        "model": model_name,
        "temperature": temperature,
        "convert_system_message_to_human": False,
        "google_api_key": key,
    }
    
    # top_p와 top_k 파라미터 추가
    # Gemini API는 top_p, top_k를 지원하며, LangChain 래퍼도 이를 지원합니다
    if top_p is not None:
        llm_kwargs["top_p"] = float(top_p)
    if top_k is not None:
        llm_kwargs["top_k"] = int(top_k)
    
    llm = ChatGoogleGenerativeAI(**llm_kwargs)

    retriever = DenseRetriever(
        documents=documents, 
        vectors=vectors, 
        embedder=embedder, 
        k=retrieval_k,
        use_mmr=use_mmr,
        mmr_diversity=mmr_diversity,
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
    )
    return chain


if __name__ == "__main__":
    chain = build_rag_chain(Path("../../data/processed/index"))
    question = "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"
    answer = chain.run(question)
    print(answer)
