from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import hydra
from omegaconf import DictConfig, OmegaConf

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from embedding_pipeline import EmbeddingPipeline, EmbeddingResult  # noqa: E402
from vector_store_builder import build_faiss_index  # noqa: E402


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z_-]+", "_", name)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "output"


def read_latest_pointer(pointer_path: Path) -> Optional[Dict]:
    if not pointer_path.exists():
        return None
    try:
        return json.loads(pointer_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def find_week2_outputs(processed_dir: Path) -> List[Path]:
    outputs: List[Path] = []
    if not processed_dir.exists():
        return outputs
    for candidate in sorted(processed_dir.iterdir()):
        if not candidate.is_dir():
            continue
        if candidate.name.lower() == "index":
            continue
        if (candidate / "chunks").is_dir():
            outputs.append(candidate.resolve())
    return outputs


def load_chunks(chunks_path: Path) -> Dict:
    if not chunks_path.exists():
        raise FileNotFoundError(f"청크 JSON 파일을 찾을 수 없습니다: {chunks_path}")
    return json.loads(chunks_path.read_text(encoding="utf-8"))


def save_embeddings(path: Path, embeddings: List[EmbeddingResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {"doc_id": emb.doc_id, "text": emb.text, "vector": emb.vector}
        for emb in embeddings
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_chunk_metadata(path: Path, chunk_info: Dict, embeddings: List[EmbeddingResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    enriched = []
    for chunk, emb in zip(chunk_info["chunks"], embeddings):
        enriched.append({**chunk, "doc_id": emb.doc_id})
    payload = {
        "strategy": chunk_info.get("strategy"),
        "summary": chunk_info.get("summary"),
        "chunks": enriched,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_strategy_jobs(chunks_dir: Path, strategies: List[str]) -> List[Tuple[Path, str]]:
    jobs: List[Tuple[Path, str]] = []
    requested = [s.lower() for s in strategies] if strategies else ["all"]
    if "all" in requested:
        json_files = sorted(chunks_dir.glob("*.json"))
        if not json_files:
            print(f"⚠️  {chunks_dir} 에 JSON 청크 파일이 없습니다. 건너뜁니다.")
        for path in json_files:
            jobs.append((path, path.stem))
    else:
        for strategy in requested:
            path = chunks_dir / f"{strategy}.json"
            if not path.exists():
                print(f"⚠️  {chunks_dir}에서 {strategy}.json 파일을 찾을 수 없습니다. 건너뜁니다.")
                continue
            jobs.append((path, strategy))
    return jobs


def resolve_paths(cfg: DictConfig) -> Dict[str, Optional[Path]]:
    project_root = Path(cfg.project_root).resolve()
    processed_dir = Path(cfg.week2.processed_dir).resolve()
    pointer_path = Path(cfg.week2.pointer_path).resolve()
    vector_base = Path(cfg.vector_store.base_dir).resolve()

    chunk_json = Path(cfg.input.chunk_json).resolve() if cfg.input.chunk_json else None
    chunks_dir = Path(cfg.input.chunks_dir).resolve() if cfg.input.chunks_dir else None

    return {
        "project_root": project_root,
        "processed_dir": processed_dir,
        "pointer_path": pointer_path,
        "vector_base": vector_base,
        "chunk_json": chunk_json,
        "chunks_dir": chunks_dir,
    }


def resolve_week2_outputs(cfg: DictConfig, paths: Dict[str, Optional[Path]], pointer: Optional[Dict]) -> List[Path]:
    explicit_dir = paths["chunks_dir"]
    if explicit_dir:
        if explicit_dir.is_dir():
            if explicit_dir.name == "chunks":
                return [explicit_dir.parent.resolve()]
            if (explicit_dir / "chunks").is_dir():
                return [explicit_dir.resolve()]
        raise FileNotFoundError(f"{explicit_dir} 아래에 'chunks' 폴더가 없습니다.")

    processed_dir = paths["processed_dir"]
    if processed_dir is None:
        raise ValueError("week2.processed_dir 설정을 확인하세요.")

    outputs = find_week2_outputs(processed_dir)
    if not outputs:
        raise FileNotFoundError("처리할 Week2 결과가 없습니다. 먼저 week2 파이프라인을 실행해주세요.")

    if cfg.input.latest_only:
        if pointer and pointer.get("output_dir"):
            pointer_output = Path(pointer["output_dir"]).resolve()
            if pointer_output in outputs:
                print(f"ℹ️  최근 Week2 출력만 처리합니다: {pointer_output}")
                return [pointer_output]
            raise FileNotFoundError(f"최근 Week2 포인터 경로를 찾을 수 없습니다: {pointer_output}")
        latest = outputs[-1]
        print(f"ℹ️  최근 Week2 출력만 처리합니다: {latest}")
        return [latest]

    if pointer and pointer.get("output_dir"):
        pointer_output = Path(pointer["output_dir"]).resolve()
        if pointer_output in outputs:
            outputs.remove(pointer_output)
            outputs.insert(0, pointer_output)
            print(f"ℹ️  최근 Week2 출력이 우선 순위로 처리됩니다: {pointer_output}")

    print(f"ℹ️  총 {len(outputs)}개의 Week2 결과를 처리합니다.")
    return outputs


def resolve_output_root(base_dir: Path, week2_dir: Path, use_week2_slug: bool, total_outputs: int) -> Path:
    if use_week2_slug:
        return base_dir / slugify(week2_dir.name)
    if total_outputs == 1:
        return base_dir
    return base_dir / slugify(week2_dir.name)


def process_single_json(cfg: DictConfig, paths: Dict[str, Optional[Path]], pipeline: EmbeddingPipeline) -> None:
    chunk_json = paths["chunk_json"]
    if chunk_json is None:
        raise ValueError("input.chunk_json 설정이 필요합니다.")

    chunk_info = load_chunks(chunk_json)
    chunk_texts = [chunk["text"] for chunk in chunk_info.get("chunks", []) if chunk.get("text")]
    if not chunk_texts:
        raise ValueError(f"{chunk_json}에 청크 텍스트가 없습니다.")

    strategy = chunk_info.get("strategy") or chunk_json.stem
    prefix = cfg.embedding.doc_prefix or strategy
    embeddings = pipeline.encode_documents(chunk_texts, prefix=prefix)

    vector_base = paths["vector_base"]
    if vector_base is None:
        raise ValueError("vector_store.base_dir 설정을 확인하세요.")
    vector_base.mkdir(parents=True, exist_ok=True)

    file_slug = slugify(chunk_json.stem)
    base_dir = vector_base / file_slug
    base_dir.mkdir(parents=True, exist_ok=True)

    target_dir = base_dir / slugify(strategy)
    target_dir.mkdir(parents=True, exist_ok=True)

    if cfg.embedding.save_embeddings:
        save_embeddings(target_dir / "embeddings.json", embeddings)
    save_chunk_metadata(target_dir / "chunks_with_ids.json", chunk_info, embeddings)
    index_path = build_faiss_index(embeddings, target_dir)
    print(f"✅ 단일 청크 처리 완료: {index_path}")


def process_week2_outputs(cfg: DictConfig, paths: Dict[str, Optional[Path]]) -> None:
    pointer = read_latest_pointer(paths["pointer_path"])
    pipeline = EmbeddingPipeline(model_name=cfg.embedding.model_name)

    chunk_json = paths["chunk_json"]
    if chunk_json:
        process_single_json(cfg, paths, pipeline)
        return

    week2_outputs = resolve_week2_outputs(cfg, paths, pointer)
    if not week2_outputs:
        raise ValueError("처리할 Week2 산출물이 없습니다.")

    vector_base = paths["vector_base"]
    if vector_base is None:
        raise ValueError("vector_store.base_dir 설정을 확인하세요.")
    vector_base.mkdir(parents=True, exist_ok=True)

    strategies = cfg.input.strategies or ["all"]
    total_jobs = 0

    for output_dir in week2_outputs:
        chunks_dir = output_dir / "chunks"
        if not chunks_dir.is_dir():
            print(f"⚠️  {output_dir} 에 'chunks' 폴더가 없어 건너뜁니다.")
            continue

        strategy_jobs = collect_strategy_jobs(chunks_dir, strategies)
        if not strategy_jobs:
            continue

        base_output = resolve_output_root(vector_base, output_dir, cfg.vector_store.use_week2_slug, len(week2_outputs))
        base_output.mkdir(parents=True, exist_ok=True)

        print(f"\n=== Week2 결과 처리: {output_dir} → {base_output} ===")

        for chunks_path, strategy_hint in strategy_jobs:
            chunk_info = load_chunks(chunks_path)
            strategy = chunk_info.get("strategy") or strategy_hint
            chunk_texts = [chunk["text"] for chunk in chunk_info.get("chunks", []) if chunk.get("text")]
            if not chunk_texts:
                print(f"⚠️  {chunks_path}에 청크 텍스트가 없어 건너뜁니다.")
                continue

            prefix = cfg.embedding.doc_prefix or strategy
            embeddings = pipeline.encode_documents(chunk_texts, prefix=prefix)
            print(f"  - {strategy} 임베딩 생성 ({len(embeddings)}개, prefix={prefix})")

            strategy_slug = slugify(strategy)
            target_dir = base_output / strategy_slug
            target_dir.mkdir(parents=True, exist_ok=True)

            if cfg.embedding.save_embeddings:
                save_embeddings(target_dir / "embeddings.json", embeddings)
            save_chunk_metadata(target_dir / "chunks_with_ids.json", chunk_info, embeddings)

            index_path = build_faiss_index(embeddings, target_dir)
            print(f"      → 인덱스: {index_path}")
            print(f"      → 메타데이터: {target_dir / 'metadata.json'}")
            total_jobs += 1

    if total_jobs == 0:
        raise ValueError("처리된 청크가 없습니다. Week2 결과를 확인하세요.")
    print(f"\n✅ 완료: 총 {total_jobs}개 전략을 처리했습니다.")


@hydra.main(version_base=None, config_path="../../conf", config_name="week3")
def main(cfg: DictConfig) -> None:
    print("=== Week3 Hydra 설정 ===")
    print(OmegaConf.to_yaml(cfg, resolve=True))

    paths = resolve_paths(cfg)
    process_week2_outputs(cfg, paths)


if __name__ == "__main__":
    main()

