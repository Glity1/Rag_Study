from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List, Optional

import hydra
import uvicorn
from dotenv import load_dotenv
from omegaconf import DictConfig, OmegaConf

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
for path in {CURRENT_DIR, SRC_DIR}:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from api_server import create_app  # noqa: E402

load_dotenv()


def slugify(name: str) -> str:
    import re

    slug = re.sub(r"[^0-9A-Za-z_-]+", "_", name)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "index"


def read_latest_pointer(pointer_path: Path) -> Optional[dict]:
    if pointer_path.exists():
        try:
            return json.loads(pointer_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def find_index_dirs(root: Path, recursive: bool) -> List[Path]:
    dirs = set()
    if (root / "index.faiss").exists():
        dirs.add(root.resolve())
        if not recursive:
            return sorted(dirs)
    if recursive:
        for path in root.glob("**/index.faiss"):
            dirs.add(path.parent.resolve())
    return sorted(dirs)


def determine_index_dir(
    root: Path,
    pointer_path: Path,
    prefer_pointer: bool,
    recursive_search: bool,
) -> Path:
    if (root / "index.faiss").exists():
        return root.resolve()

    if prefer_pointer:
        pointer = read_latest_pointer(pointer_path)
        if pointer and pointer.get("output_dir"):
            slug = slugify(Path(pointer["output_dir"]).name)
            candidate_root = root / slug
            candidates = find_index_dirs(candidate_root, recursive=recursive_search)
            if candidates:
                return candidates[0]

    candidates = find_index_dirs(root, recursive=recursive_search)
    if not candidates:
        raise FileNotFoundError(
            f"{root} 아래에서 `index.faiss` 파일을 찾지 못했습니다. 먼저 Week3 파이프라인을 실행하세요."
        )
    return candidates[0]


def ensure_google_key(required: bool) -> str:
    key = os.getenv("GOOGLE_API_KEY")
    if required and not key:
        raise EnvironmentError("`GOOGLE_API_KEY`가 필요합니다. `.env` 또는 환경 변수를 확인하세요.")
    if key:
        os.environ["GOOGLE_API_KEY"] = key
    return key or ""


@hydra.main(version_base=None, config_path="../../conf", config_name="week6")
def main(cfg: DictConfig) -> None:
    print("=== Week6 Hydra 설정 ===")
    print(OmegaConf.to_yaml(cfg, resolve=True))

    index_root = Path(cfg.paths.index_root).resolve()
    if not index_root.exists():
        raise FileNotFoundError(f"인덱스 경로를 찾을 수 없습니다: {index_root}")

    index_dir = determine_index_dir(
        root=index_root,
        pointer_path=Path(cfg.paths.latest_pointer).resolve(),
        prefer_pointer=bool(cfg.index_selection.prefer_pointer),
        recursive_search=bool(cfg.index_selection.recursive_search),
    )
    print(f"ℹ️  사용할 인덱스 디렉터리: {index_dir}")

    ensure_google_key(bool(cfg.rag.ensure_google_key))
    
    # LLM 파라미터 추출
    temperature = float(cfg.rag.get("temperature", 0.0))
    top_p = cfg.rag.get("top_p")
    top_k = cfg.rag.get("top_k")
    use_mmr = bool(cfg.rag.get("use_mmr", False))
    mmr_diversity = float(cfg.rag.get("mmr_diversity", 0.5))
    
    app = create_app(
        index_dir, 
        google_api_key=os.getenv("GOOGLE_API_KEY"), 
        model_name=cfg.rag.model_name,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        use_mmr=use_mmr,
        mmr_diversity=mmr_diversity,
    )

    uvicorn.run(
        app,
        host=cfg.server.host,
        port=int(cfg.server.port),
        reload=bool(cfg.server.reload),
    )


if __name__ == "__main__":
    main()