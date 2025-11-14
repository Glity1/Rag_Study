"""6주차 FastAPI 스모크 테스트 클라이언트."""

from __future__ import annotations

import httpx


def ask(question: str, endpoint: str = "http://localhost:8000/query") -> str:
    """간단한 POST 요청으로 RAG API를 호출한다."""

    response = httpx.post(endpoint, json={"question": question})
    response.raise_for_status()
    return response.json()["answer"]


if __name__ == "__main__":
    print(ask("그랜드코리아레저의 코로나 대응 전략을 요약해줘."))
