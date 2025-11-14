"""3주차 FAISS 벡터 스토어 생성 스크립트."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import faiss
import numpy as np

from embedding_pipeline import EmbeddingResult


def build_faiss_index(embeddings: Iterable[EmbeddingResult], output_dir: Path) -> Path:
    """임베딩 결과를 받아 FAISS 인덱스를 생성하고 저장한다."""

    output_dir.mkdir(parents=True, exist_ok=True)

    vectors = np.array([result.vector for result in embeddings], dtype="float32")
    if vectors.size == 0:
        raise ValueError("저장할 임베딩이 없습니다.")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    index_path = output_dir / "index.faiss"
    faiss.write_index(index, str(index_path))

    metadata_path = output_dir / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(result) for result in embeddings], f, ensure_ascii=False, indent=2)

    return index_path


if __name__ == "__main__":
    sample = [
        EmbeddingResult(doc_id="doc_00001", text="안녕하세요", vector=[0.1, 0.2, 0.3]),
        EmbeddingResult(doc_id="doc_00002", text="세계", vector=[0.4, 0.5, 0.6]),
    ]
    output_dir = Path("../../data/processed/index")
    build_faiss_index(sample, output_dir)
    print(f"FAISS 인덱스를 {output_dir}에 저장했습니다")
