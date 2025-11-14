"""2주차 청킹 파이프라인 유틸리티.

여러 가지 텍스트 분할 전략을 적용해 RAG에 필요한 청크를 생성한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:  # pragma: no cover
    RecursiveCharacterTextSplitter = None  # type: ignore

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore
    np = None  # type: ignore


@dataclass
class Chunk:
    """생성된 청크 정보를 담는 데이터 클래스."""

    index: int
    text: str
    start: int
    end: int
    strategy: str

    @property
    def size(self) -> int:
        return len(self.text)


def fixed_size_chunking(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
    """고정 길이와 오버랩을 사용한 단순 청킹."""

    chunks: List[Chunk] = []
    cursor = 0
    index = 1
    while cursor < len(text):
        end = min(cursor + chunk_size, len(text))
        chunk_text = text[cursor:end]
        chunks.append(Chunk(index=index, text=chunk_text, start=cursor, end=end, strategy="fixed"))
        index += 1
        if end == len(text):
            break
        cursor = max(end - overlap, 0)
    return chunks


def recursive_chunking(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Chunk]:
    """LangChain 재귀 분할기를 활용한 청킹."""

    if RecursiveCharacterTextSplitter is None:
        raise ImportError("LangChain이 설치되어 있어야 재귀 청킹을 사용할 수 있습니다.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    pieces = splitter.split_text(text)
    chunks: List[Chunk] = []
    cursor = 0
    for idx, piece in enumerate(pieces, 1):
        cleaned = piece.strip()
        if not cleaned:
            continue
        position = text.find(cleaned, cursor)
        if position == -1:
            position = text.find(cleaned)
        chunks.append(Chunk(index=idx, text=cleaned, start=position, end=position + len(cleaned), strategy="recursive"))
        cursor = position + len(cleaned)
    return chunks


def sentence_chunking(text: str, sentences_per_chunk: int = 3) -> List[Chunk]:
    """문장 단위로 묶는 청킹 전략."""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    chunks: List[Chunk] = []
    cursor = 0
    for idx in range(0, len(sentences), sentences_per_chunk):
        group = " ".join(sentences[idx : idx + sentences_per_chunk])
        position = text.find(group, cursor)
        if position == -1:
            position = text.find(group)
        chunks.append(Chunk(index=len(chunks) + 1, text=group, start=position, end=position + len(group), strategy="sentence"))
        cursor = position + len(group)
    return chunks


def paragraph_chunking(text: str, max_chars: int = 800) -> List[Chunk]:
    """단락 기반 청킹 전략."""

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[Chunk] = []
    buffer: List[str] = []
    buffer_start = 0
    cursor = 0

    for para in paragraphs:
        position = text.find(para, cursor)
        if position == -1:
            position = text.find(para)
        if not buffer:
            buffer_start = position
        buffer.append(para)
        buffer_text = "\n\n".join(buffer)
        if len(buffer_text) >= max_chars:
            chunks.append(Chunk(index=len(chunks) + 1, text=buffer_text, start=buffer_start, end=buffer_start + len(buffer_text), strategy="paragraph"))
            buffer = []
        cursor = position + len(para)

    if buffer:
        buffer_text = "\n\n".join(buffer)
        chunks.append(Chunk(index=len(chunks) + 1, text=buffer_text, start=buffer_start, end=buffer_start + len(buffer_text), strategy="paragraph"))

    return chunks


def semantic_chunking(
    text: str,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    similarity_threshold: float = 0.75,
    max_chunk_size: int = 800,
) -> List[Chunk]:
    """임베딩 유사도 기반으로 의미 단위 청킹을 수행한다."""

    if SentenceTransformer is None or np is None:
        raise ImportError("의미 기반 청킹을 사용하려면 sentence-transformers가 필요합니다.")

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return []

    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, convert_to_numpy=True)

    chunks: List[Chunk] = []
    current_group: List[str] = [sentences[0]]
    current_start = text.find(sentences[0])
    cursor = current_start + len(sentences[0])

    def append_chunk(group: List[str], start_pos: int) -> None:
        chunk_text = " ".join(group)
        chunks.append(
            Chunk(
                index=len(chunks) + 1,
                text=chunk_text,
                start=start_pos,
                end=start_pos + len(chunk_text),
                strategy="semantic",
            )
        )

    for idx in range(1, len(sentences)):
        prev_embedding = embeddings[idx - 1]
        current_embedding = embeddings[idx]
        denominator = float(np.linalg.norm(prev_embedding) * np.linalg.norm(current_embedding))
        similarity = float(np.dot(prev_embedding, current_embedding) / denominator) if denominator else 0.0
        sentence = sentences[idx]
        position = text.find(sentence, cursor)
        if position == -1:
            position = text.find(sentence)

        prospective = " ".join(current_group + [sentence])
        if similarity < similarity_threshold or len(prospective) > max_chunk_size:
            append_chunk(current_group, current_start)
            current_group = [sentence]
            current_start = position
        else:
            current_group.append(sentence)
        cursor = position + len(sentence)

    if current_group:
        append_chunk(current_group, current_start)

    return chunks


Strategy = Callable[..., List[Chunk]]

STRATEGY_REGISTRY: Dict[str, Strategy] = {
    "fixed": fixed_size_chunking,
    "recursive": recursive_chunking,
    "sentence": sentence_chunking,
    "paragraph": paragraph_chunking,
    "semantic": semantic_chunking,
}


def chunk_text(strategy: str, text: str, **kwargs) -> List[Chunk]:
    """전략 이름에 따라 청킹 함수를 실행한다."""

    if strategy not in STRATEGY_REGISTRY:
        raise ValueError(f"지원하지 않는 전략입니다: {strategy}")
    return STRATEGY_REGISTRY[strategy](text, **kwargs)


def summarise_chunks(chunks: Iterable[Chunk]) -> Dict[str, float]:
    """청크 목록에 대한 간단한 통계를 반환한다."""

    chunks_list = list(chunks)
    if not chunks_list:
        return {"count": 0, "avg_size": 0.0, "min_size": 0, "max_size": 0}
    sizes = [chunk.size for chunk in chunks_list]
    return {
        "count": len(chunks_list),
        "avg_size": sum(sizes) / len(sizes),
        "min_size": min(sizes),
        "max_size": max(sizes),
    }