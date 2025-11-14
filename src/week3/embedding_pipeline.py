"""3주차 임베딩 파이프라인."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:  # pragma: no cover
    raise ImportError("sentence-transformers 패키지가 필요합니다.") from exc


@dataclass
class EmbeddingResult:
    doc_id: str
    text: str
    vector: List[float]


class EmbeddingPipeline:
    """SentenceTransformer를 이용해 문서 임베딩을 생성하는 파이프라인."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)

    def encode_documents(self, documents: Iterable[str], prefix: str = "doc") -> List[EmbeddingResult]:
        texts = list(documents)
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [
            EmbeddingResult(doc_id=f"{prefix}_{idx:05d}", text=text, vector=vector.tolist())
            for idx, (text, vector) in enumerate(zip(texts, embeddings), start=1)
        ]


def load_documents(directory: Path) -> List[str]:
    """지정한 디렉터리의 .txt 파일을 읽어 리스트로 반환한다."""

    texts: List[str] = []
    for path in sorted(directory.glob("*.txt")):
        texts.append(path.read_text(encoding="utf-8"))
    return texts


if __name__ == "__main__":
    docs = load_documents(Path("../../data/processed"))
    pipeline = EmbeddingPipeline()
    results = pipeline.encode_documents(docs)
    print(f"{len(results)}개의 문서를 임베딩했습니다")
