from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import hydra
from omegaconf import DictConfig, OmegaConf

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from pdf_loader import PdfExtractionResult, extract_pdf  # noqa: E402
from chunking_pipeline import (  # noqa: E402
    Chunk,
    STRATEGY_REGISTRY,
    chunk_text,
    summarise_chunks,
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_chunks_as_txt(path: Path, chunks: Iterable[Chunk]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(f"# chunk {chunk.index} [{chunk.start}:{chunk.end}] size={chunk.size}\n")
            file.write(chunk.text.replace("\r", "") + "\n\n")


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", name).strip("_")
    return slug or "output"


def update_latest_pointer(
    pointer_path: Path,
    output_dir: Path,
    pdf_path: Path,
    stats: Dict[str, Dict],
    ocr_enabled: bool,
    ocr_lang: str,
) -> None:
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "output_dir": str(output_dir),
        "chunks_dir": str((output_dir / "chunks").resolve()),
        "pdf": str(pdf_path),
        "strategies": stats,
        "ocr_enabled": ocr_enabled,
        "ocr_lang": ocr_lang,
        "updated_at": datetime.now().isoformat(),
    }
    pointer_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def insert_image_placeholders(
    full_text: str,
    text_blocks: List,
    images: List,
    placeholder_format: str = "Image: [{name}] (Page {page}, {width}x{height})",
) -> str:
    """
    텍스트에 이미지 플레이스홀더를 삽입한다.
    
    이미지가 텍스트 블록 근처에 있으면 해당 위치에 플레이스홀더를 삽입합니다.
    """
    if not images:
        return full_text
    
    # 텍스트 블록과 이미지를 페이지별로 그룹화
    page_text_positions: Dict[int, List[tuple]] = {}  # page -> [(start, end, text_block)]
    page_images: Dict[int, List] = {}  # page -> [images]
    
    # 텍스트 블록 위치 계산 (full_text 기준)
    current_pos = 0
    for block in text_blocks:
        block_text = block.text
        pos = full_text.find(block_text, current_pos)
        if pos != -1:
            if block.page not in page_text_positions:
                page_text_positions[block.page] = []
            page_text_positions[block.page].append((pos, pos + len(block_text), block))
            current_pos = pos + len(block_text)
    
    # 이미지를 페이지별로 그룹화
    for img in images:
        if img.page not in page_images:
            page_images[img.page] = []
        page_images[img.page].append(img)
    
    # 각 페이지에서 이미지를 텍스트 블록 근처에 삽입
    result_text = full_text
    offset = 0  # 삽입으로 인한 오프셋
    
    for page in sorted(set(page_text_positions.keys()) | set(page_images.keys())):
        if page not in page_images:
            continue
        
        page_imgs = page_images[page]
        if page not in page_text_positions:
            # 텍스트 블록이 없는 페이지의 경우, 페이지 시작 부분에 이미지 정보 추가
            for img in page_imgs:
                placeholder = placeholder_format.format(
                    name=img.name,
                    page=img.page,
                    width=img.width,
                    height=img.height,
                )
                result_text = f"[Page {page} Images]\n{placeholder}\n\n{result_text}"
                offset += len(f"[Page {page} Images]\n{placeholder}\n\n")
            continue
        
        # 텍스트 블록이 있는 경우, 각 이미지를 가장 가까운 텍스트 블록 뒤에 삽입
        text_positions = sorted(page_text_positions[page], key=lambda x: x[0])
        
        for img in page_imgs:
            placeholder = placeholder_format.format(
                name=img.name,
                page=img.page,
                width=img.width,
                height=img.height,
            )
            
            # 이미지 bbox를 기반으로 가장 가까운 텍스트 블록 찾기
            # 간단히 페이지의 마지막 텍스트 블록 뒤에 삽입
            if text_positions:
                last_pos = text_positions[-1][1]
                insert_pos = last_pos + offset
                result_text = (
                    result_text[:insert_pos] + 
                    f"\n\n{placeholder}\n\n" + 
                    result_text[insert_pos:]
                )
                offset += len(f"\n\n{placeholder}\n\n")
    
    return result_text


def chunk_with_strategy(full_text: str, strategy: str, cfg: DictConfig) -> List[Chunk]:
    chunk_cfg = cfg.chunking

    if strategy == "fixed":
        return chunk_text(
            "fixed",
            full_text,
            chunk_size=chunk_cfg.fixed.chunk_size,
            overlap=chunk_cfg.fixed.overlap,
        )
    if strategy == "recursive":
        return chunk_text(
            "recursive",
            full_text,
            chunk_size=chunk_cfg.recursive.chunk_size,
            chunk_overlap=chunk_cfg.recursive.overlap,
        )
    if strategy == "sentence":
        return chunk_text(
            "sentence",
            full_text,
            sentences_per_chunk=chunk_cfg.sentence.sentences_per_chunk,
        )
    if strategy == "paragraph":
        return chunk_text(
            "paragraph",
            full_text,
            max_chars=chunk_cfg.paragraph.max_chars,
        )
    if strategy == "semantic":
        return chunk_text(
            "semantic",
            full_text,
            model_name=chunk_cfg.semantic.model,
            similarity_threshold=chunk_cfg.semantic.similarity_threshold,
            max_chunk_size=chunk_cfg.semantic.max_chunk_size,
        )
    raise ValueError(f"지원하지 않는 전략입니다: {strategy}")


def process_pdf(
    cfg: DictConfig,
    pdf_path: Path,
    output_dir: Path,
    image_dir: Path | None,
) -> None:
    strategies = [strategy.lower() for strategy in cfg.chunking.strategies]
    for invalid in set(strategies) - set(STRATEGY_REGISTRY):
        raise ValueError(f"알 수 없는 전략이 설정에 포함되어 있습니다: {invalid}")

    print(f"[1/4] PDF 추출 시작: {pdf_path}")
    result: PdfExtractionResult = extract_pdf(
        pdf_path=pdf_path,
        save_image_dir=image_dir,
        min_text_length=cfg.pdf.min_text_length,
        enable_ocr=bool(cfg.pdf.ocr.enable),
        ocr_lang=cfg.pdf.ocr.language,
    )

    full_text = result.full_text
    if not full_text.strip():
        print("⚠️  추출된 텍스트가 없습니다. OCR 설정을 확인하거나 다른 PDF를 사용해 주세요.")

    # 이미지 플레이스홀더 삽입 (설정에서 활성화된 경우)
    if cfg.pdf.get("insert_image_placeholders", False):
        placeholder_format = cfg.pdf.get("image_placeholder_format", "Image: [{name}] (Page {page}, {width}x{height})")
        full_text = insert_image_placeholders(
            full_text,
            result.text_blocks,
            result.images,
            placeholder_format=placeholder_format,
        )
        print(f"  - 이미지 플레이스홀더 삽입 완료: {len(result.images)}개 이미지")

    print(f"[2/4] 추출 결과 저장: {output_dir}")
    write_json(output_dir / "extraction.json", result.to_dict())
    write_text(output_dir / "full_text.txt", full_text)

    chunks_root = output_dir / "chunks"
    stats: Dict[str, Dict] = {}

    print("[3/4] 청킹 작업 실행")
    for strategy in strategies:
        try:
            chunks = chunk_with_strategy(full_text, strategy, cfg)
        except ImportError as exc:
            print(f"  - ⚠️  {strategy} 전략 실행 실패 (필요한 라이브러리 미설치): {exc}")
            continue

        stats[strategy] = summarise_chunks(chunks)
        write_chunks_as_txt(chunks_root / f"{strategy}.txt", chunks)
        write_json(
            chunks_root / f"{strategy}.json",
            {
                "strategy": strategy,
                "summary": stats[strategy],
                "chunks": [chunk.__dict__ for chunk in chunks],
            },
        )
        print(
            f"  - {strategy} 완료: "
            f"청크 {stats[strategy]['count']}개 | "
            f"평균 길이 {stats[strategy]['avg_size']:.1f}"
        )

    print("[4/4] 요약 저장")
    write_json(
        output_dir / "summary.json",
        {
            "pdf": str(pdf_path),
            "strategies": stats,
            "ocr_enabled": bool(cfg.pdf.ocr.enable),
            "ocr_lang": cfg.pdf.ocr.language,
        },
    )
    update_latest_pointer(
        pointer_path=Path(cfg.outputs.latest_pointer),
        output_dir=output_dir,
        pdf_path=pdf_path,
        stats=stats,
        ocr_enabled=bool(cfg.pdf.ocr.enable),
        ocr_lang=cfg.pdf.ocr.language,
    )
    print("✅ Week2 파이프라인이 완료되었습니다.")
    print(f"   - 전체 텍스트: {output_dir / 'full_text.txt'}")
    print(f"   - 청크 폴더:   {chunks_root}")
    print(f"   - 요약:        {output_dir / 'summary.json'}")


def resolve_pdf_paths(cfg: DictConfig, raw_dir: Path) -> List[Path]:
    candidates = []
    for item in cfg.pdf.inputs:
        candidate = Path(item)
        if not candidate.exists():
            alternative = raw_dir / item
            if alternative.exists():
                candidate = alternative
        if not candidate.exists():
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {item}")
        candidates.append(candidate.resolve())

    if candidates:
        return candidates

    if not raw_dir.exists():
        raise FileNotFoundError(f"PDF 원본 디렉터리를 찾을 수 없습니다: {raw_dir}")

    pdfs = sorted(raw_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"{raw_dir}에 PDF가 존재하지 않습니다. pdf.inputs 설정으로 파일을 지정해 주세요.")
    return pdfs


def resolve_environment_paths(cfg: DictConfig) -> Dict[str, Path | None]:
    project_root = Path(cfg.project_root).resolve()
    raw_dir = Path(cfg.data.raw_dir).resolve()
    base_output = Path(cfg.outputs.base_dir).resolve()
    image_dir = Path(cfg.outputs.image_dir).resolve() if cfg.outputs.image_dir else None
    return {
        "project_root": project_root,
        "raw_dir": raw_dir,
        "base_output": base_output,
        "image_base": image_dir,
    }


@hydra.main(version_base=None, config_path="../../conf", config_name="week2")
def main(cfg: DictConfig) -> None:
    print("=== Week2 Hydra 설정 ===")
    print(OmegaConf.to_yaml(cfg, resolve=True))

    paths = resolve_environment_paths(cfg)
    raw_dir = paths["raw_dir"]
    base_output = paths["base_output"]
    image_base = paths["image_base"]

    pdf_paths = resolve_pdf_paths(cfg, raw_dir)
    total = len(pdf_paths)

    for idx, pdf_path in enumerate(pdf_paths, start=1):
        slug = slugify(pdf_path.stem)
        if cfg.outputs.use_slug_subdir:
            output_dir = base_output / slug
            image_dir = image_base / slug if image_base else None
        else:
            output_dir = base_output if total == 1 else base_output / slug
            image_dir = image_base if image_base and total == 1 else (image_base / slug if image_base else None)

        print(f"\n=== [{idx}/{total}] {pdf_path.name} 처리 ===")
        process_pdf(
            cfg=cfg,
            pdf_path=pdf_path,
            output_dir=output_dir,
            image_dir=image_dir,
        )

    print(f"\n✅ 총 {total}개 PDF 처리를 완료했습니다.")


if __name__ == "__main__":
    main()
