"""4주차 검색 평가 스크립트.

검증용 질문-답변 세트를 기반으로 간단한 재현율(Recall) 지표를 계산한다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from rag_chain import DenseRetriever, load_documents_and_vectors
from langchain_community.embeddings import HuggingFaceEmbeddings


@dataclass
class QAExample:
    question: str
    answer: str


def load_validation_set(path: Path) -> List[QAExample]:
    """검증 JSON 파일을 읽어 QAExample 목록으로 변환한다."""

    data = json.loads(path.read_text(encoding="utf-8"))
    return [QAExample(**item) for item in data]


def evaluate(index_dir: Path, validation_path: Path, k: int = 5) -> float:
    """주어진 인덱스와 검증 세트로 Recall@k를 계산한다."""

    documents, vectors = load_documents_and_vectors(index_dir)
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    retriever = DenseRetriever(documents=documents, vectors=vectors, embedder=embedder, k=k)
    examples = load_validation_set(validation_path)

    hits = 0
    for example in examples:
        docs = retriever.get_relevant_documents(example.question)
        context = "\n".join(doc.page_content for doc in docs)
        if example.answer in context:
            hits += 1
    return hits / len(examples)


if __name__ == "__main__":
    score = evaluate(Path("../week3/data/index"), Path("data/validation.json"))
    print(f"Recall@5: {score:.2%}")
