from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig, OmegaConf

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent
for path in {CURRENT_DIR, ROOT_DIR / "week3"}:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rag_chain import build_rag_chain  # noqa: E402
from retrieval_eval import evaluate  # noqa: E402

load_dotenv()


def resolve_google_key(config_key: Optional[str]) -> Optional[str]:
    """환경 변수와 설정 값을 종합해 Google API 키를 반환한다."""

    if config_key:
        return config_key
    return os.getenv("GOOGLE_API_KEY")


def find_index_dirs(root: Path, recursive: bool) -> List[Path]:
    """index.faiss 파일을 포함하는 디렉터리를 탐색한다."""

    candidates = set()
    if (root / "index.faiss").exists():
        candidates.add(root.resolve())
        if not recursive:
            return sorted(candidates)

    if recursive:
        for path in root.glob("**/index.faiss"):
            candidates.add(path.parent.resolve())

    return sorted(candidates)


def resolve_index_dirs(index_root: Path, recursive: bool) -> List[Path]:
    """설정에 따라 사용할 인덱스 디렉터리 목록을 결정한다."""

    if not index_root.exists():
        raise FileNotFoundError(f"인덱스 경로를 찾을 수 없습니다: {index_root}")

    index_dirs = find_index_dirs(index_root, recursive=recursive)
    if not index_dirs:
        raise FileNotFoundError(
            f"{index_root} 아래에서 `index.faiss` 파일을 찾지 못했습니다. 먼저 Week3 파이프라인을 실행하세요."
        )
    return index_dirs


def resolve_validation_path(path_str: Optional[str]) -> Optional[Path]:
    """평가용 검증 세트 경로를 확인한다."""

    if not path_str:
        return None
    candidate = Path(path_str).resolve()
    if not candidate.exists():
        print(f"⚠️  검증 세트를 찾을 수 없어 평가를 건너뜁니다: {candidate}")
        return None
    return candidate


def run_workflow(cfg: DictConfig) -> None:
    index_root = Path(cfg.week3.index_root).resolve()
    recursive = bool(cfg.discovery.use_recursive_search)
    index_dirs = resolve_index_dirs(index_root, recursive=recursive)

    validation_path = resolve_validation_path(cfg.evaluation.validation_path)
    google_key = resolve_google_key(cfg.rag.google_key)
    skip_qa = bool(cfg.rag.skip_qa)

    if google_key is None and not skip_qa:
        print("⚠️  GOOGLE_API_KEY가 없어 QA 단계를 건너뜁니다. `.env` 또는 환경 변수를 확인하세요.")
        skip_qa = True

    question = cfg.rag.question
    top_k = int(cfg.rag.top_k)
    model_name = cfg.rag.model
    use_mmr = bool(cfg.rag.get("use_mmr", False))
    mmr_diversity = float(cfg.rag.get("mmr_diversity", 0.5))
    temperature = float(cfg.rag.get("temperature", 0.0))
    top_p = cfg.rag.get("top_p")
    top_k_llm = cfg.rag.get("top_k_llm")

    for idx, index_dir in enumerate(index_dirs, start=1):
        print(f"\n=== [{idx}/{len(index_dirs)}] 인덱스: {index_dir} ===")

        if not skip_qa and google_key is not None:
            search_method = "MMR" if use_mmr else "Similarity"
            print(f"[1/3] RAG 체인 구성 (index={index_dir}, 검색={search_method})")
            try:
                chain = build_rag_chain(
                    index_dir,
                    google_api_key=google_key,
                    model_name=model_name,
                    retrieval_k=top_k,
                    use_mmr=use_mmr,
                    mmr_diversity=mmr_diversity,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k_llm,
                )
            except Exception as exc:  # pragma: no cover - 외부 API 호출 오류
                print(f"    ❌ RAG 체인 생성 실패: {exc}")
            else:
                print("[2/3] 샘플 질문 실행")
                try:
                    result = chain.invoke({"query": question})
                    answer = result.get("result", result)
                    print("질문:", question)
                    print("답변:")
                    print(answer)
                except Exception as exc:
                    print(f"    ❌ QA 실행 실패: {exc}")
        else:
            print("⚠️  QA 실행이 비활성화되어 있습니다.")

        if validation_path:
            print("[3/3] Recall 평가 실행")
            try:
                score = evaluate(index_dir, validation_path, k=top_k)
                print(f"Recall@{top_k}: {score:.2%}")
            except Exception as exc:
                print(f"    ❌ 평가 실패: {exc}")

    print(f"\n✅ 총 {len(index_dirs)}개 인덱스에 대해 Week4 테스트를 완료했습니다.")


@hydra.main(version_base=None, config_path="../../conf", config_name="week4")
def main(cfg: DictConfig) -> None:
    print("=== Week4 Hydra 설정 ===")
    print(OmegaConf.to_yaml(cfg, resolve=True))
    run_workflow(cfg)


if __name__ == "__main__":
    main()

