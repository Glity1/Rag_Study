from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF

try:
    # Pillow는 선택 설치 항목입니다. 이미지 파일로 저장할 때에만 필요합니다.
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[misc]

try:
    import pytesseract
except ImportError:  # pragma: no cover
    pytesseract = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# 데이터 클래스 정의
# ---------------------------------------------------------------------------

@dataclass
class ImageMetadata:
    """PDF에서 추출된 이미지 정보를 담는 컨테이너."""

    page: int
    name: str
    bbox: List[float]
    width: int
    height: int
    ext: str
    saved_path: Optional[str] = None


@dataclass
class TextBlock:
    """PyMuPDF가 반환하는 텍스트 블록을 표현한다."""

    page: int
    block_no: int
    bbox: List[float]
    text: str


@dataclass
class PdfExtractionResult:
    """PDF에서 추출한 텍스트/이미지 정보를 묶어서 제공한다."""

    path: str
    page_count: int
    text_blocks: List[TextBlock]
    images: List[ImageMetadata]

    @property
    def full_text(self) -> str:
        """모든 텍스트 블록을 하나의 문자열로 이어 붙인다."""

        return "\n".join(block.text for block in self.text_blocks if block.text)

    def to_dict(self) -> Dict[str, Any]:
        """JSON 저장을 위한 사전(dict) 형태로 직렬화한다."""

        return {
            "path": self.path,
            "page_count": self.page_count,
            "text_blocks": [asdict(block) for block in self.text_blocks],
            "images": [asdict(image) for image in self.images],
        }


# ---------------------------------------------------------------------------
# PDF 추출 핵심 로직
# ---------------------------------------------------------------------------

def extract_pdf(
    pdf_path: str | Path,
    save_image_dir: str | Path | None = None,
    min_text_length: int = 10,
    enable_ocr: bool = False,
    ocr_lang: str = "kor+eng",
) -> PdfExtractionResult:
    """PDF 파일에서 텍스트와 이미지를 추출한다."""

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    image_dir: Optional[Path] = None
    if save_image_dir is not None:
        image_dir = Path(save_image_dir)
        image_dir.mkdir(parents=True, exist_ok=True)

    if enable_ocr and pytesseract is None:
        raise ImportError("pytesseract가 설치되어 있어야 OCR 기능을 사용할 수 있습니다.")
    if enable_ocr and Image is None:
        raise ImportError("Pillow가 설치되어 있어야 OCR 기능을 사용할 수 있습니다.")
    if enable_ocr:
        tess_cmd = os.getenv("TESSERACT_CMD")
        if tess_cmd:
            pytesseract.pytesseract.tesseract_cmd = tess_cmd  # type: ignore[attr-defined]

    doc = fitz.open(pdf_path)

    text_blocks: List[TextBlock] = []
    images: List[ImageMetadata] = []
    block_counter = 0

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)

        page_blocks: List[TextBlock] = []

        # 텍스트 추출
        for block_no, block in enumerate(page.get_text("blocks")):
            x0, y0, x1, y1, text, *_ = block
            cleaned = text.strip()
            if len(cleaned) < min_text_length:
                continue
            page_blocks.append(
                TextBlock(
                    page=page_index + 1,
                    block_no=block_counter,
                    bbox=[x0, y0, x1, y1],
                    text=cleaned,
                )
            )
            block_counter += 1

        # 이미지 추출
        for img_index, image in enumerate(page.get_images(full=True)):
            xref = image[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            width = base_image["width"]
            height = base_image["height"]
            name = f"page{page_index + 1}_img{img_index + 1}.{ext}"
            bbox = list(page.get_image_bbox(image)) if hasattr(page, "get_image_bbox") else []

            saved_path: Optional[str] = None
            if image_dir is not None and Image is not None:
                img_path = image_dir / name
                with open(img_path, "wb") as img_file:
                    img_file.write(image_bytes)
                saved_path = str(img_path)

            images.append(
                ImageMetadata(
                    page=page_index + 1,
                    name=name,
                    bbox=bbox,
                    width=width,
                    height=height,
                    ext=ext,
                    saved_path=saved_path,
                )
            )

        if enable_ocr and not page_blocks:
            pix = page.get_pixmap(alpha=False)
            mode = "RGB"
            if Image is not None:
                ocr_image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(ocr_image, lang=ocr_lang)  # type: ignore[misc]
                cleaned = ocr_text.strip()
                if len(cleaned) >= min_text_length:
                    page_blocks.append(
                        TextBlock(
                            page=page_index + 1,
                            block_no=block_counter,
                            bbox=[0, 0, float(pix.width), float(pix.height)],
                            text=cleaned,
                        )
                    )
                    block_counter += 1

        text_blocks.extend(page_blocks)

    page_count = doc.page_count
    doc.close()

    return PdfExtractionResult(
        path=str(pdf_path.resolve()),
        page_count=page_count,
        text_blocks=text_blocks,
        images=images,
    )


# ---------------------------------------------------------------------------
# 명령행 인터페이스
# ---------------------------------------------------------------------------

def main() -> None:
    """명령행 인자를 받아 PDF 전처리 파이프라인을 실행한다."""

    parser = argparse.ArgumentParser(description="PDF 전처리 유틸리티")
    parser.add_argument("--path", required=True, help="분석할 PDF 파일 경로")
    parser.add_argument(
        "--image-dir",
        default=None,
        help="추출한 이미지를 저장할 디렉터리(생략 시 저장하지 않음)",
    )
    parser.add_argument(
        "--min-text-length",
        type=int,
        default=10,
        help="텍스트 블록으로 인정할 최소 글자 수",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="결과를 JSON으로 저장할 파일 경로(생략 시 표준 출력)",
    )
    parser.add_argument(
        "--enable-ocr",
        action="store_true",
        help="텍스트가 없는 스캔본 PDF를 위해 OCR을 활성화",
    )
    parser.add_argument(
        "--ocr-lang",
        default="kor+eng",
        help="pytesseract OCR 언어 코드 (예: kor, eng, kor+eng)",
    )

    args = parser.parse_args()

    result = extract_pdf(
        pdf_path=args.path,
        save_image_dir=args.image_dir,
        min_text_length=args.min_text_length,
        enable_ocr=args.enable_ocr,
        ocr_lang=args.ocr_lang,
    )

    result_dict = result.to_dict()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        print(f"결과를 저장했습니다: {output_path}")
    else:
        # ensure_ascii=False는 한글이 깨지지 않고 JSON으로 출력되도록 보장합니다.
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()