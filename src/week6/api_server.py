"""6주차 FastAPI RAG 서버."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from dotenv import load_dotenv

from week4.rag_chain import build_rag_chain

load_dotenv()

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    answer: str


def create_app(
    index_dir: Path,
    google_api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.0,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    use_mmr: bool = False,
    mmr_diversity: float = 0.5,
) -> FastAPI:
    """
    FAISS 인덱스를 기반으로 하는 RAG FastAPI 애플리케이션을 생성한다.
    
    Args:
        index_dir: 인덱스 디렉토리 경로
        google_api_key: Google API 키
        model_name: LLM 모델 이름
        temperature: LLM temperature 파라미터
        top_p: LLM top_p 파라미터
        top_k: LLM top_k 파라미터
        use_mmr: MMR 검색 사용 여부
        mmr_diversity: MMR 다양성 파라미터
    """

    key = google_api_key or os.getenv("GOOGLE_API_KEY")
    chain = build_rag_chain(
        index_dir, 
        google_api_key=key, 
        model_name=model_name,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        use_mmr=use_mmr,
        mmr_diversity=mmr_diversity,
    )

    app = FastAPI(title="Week6 RAG API", version="0.1.0")

    @app.post("/query", response_model=QueryResponse)
    def query(req: QueryRequest) -> QueryResponse:  # type: ignore[override]
        if not req.question.strip():
            raise HTTPException(status_code=400, detail="질문을 입력해주세요")
        answer = chain.run(req.question)
        return QueryResponse(answer=answer)

    return app
