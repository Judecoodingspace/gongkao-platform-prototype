"""Build local DocumentBlock JSON from parser POC outputs.

The generated files may contain private exam text. Keep the output directory
ignored by git and use it only for local prototype testing.

Two input sources are supported:

- Docling JSON (default): reads ``texts`` and ``pictures`` arrays produced by
  ``scripts/docling_poc/convert_with_docling.py``.
- LibreOffice PDF (``--from-pdf``): reads text blocks and embedded images
  directly from a PDF produced by
  ``scripts/libreoffice_poc/convert_with_libreoffice.py``. This path avoids
  Docling's dependency on torch and its DrawingML rasterization, which fails
  when LibreOffice is not configured for Docling.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
from pathlib import Path
from typing import Any


def safe_name(path: Path) -> str:
    return path.name.replace(".docling.json", "").replace(".json", "")


def first_prov(item: dict[str, Any]) -> dict[str, Any]:
    prov = item.get("prov")
    if isinstance(prov, list) and prov:
        return prov[0] if isinstance(prov[0], dict) else {}
    if isinstance(prov, dict):
        return prov
    return {}


def page_label(prov: dict[str, Any]) -> str:
    page_no = prov.get("page_no")
    return f"第 {page_no} 页" if page_no is not None else "Docling 顺序"


def bbox_to_span(prov: dict[str, Any]) -> dict[str, Any]:
    bbox = prov.get("bbox")
    if not isinstance(bbox, dict):
        return {}
    return {
        "bbox": {
            "l": bbox.get("l"),
            "t": bbox.get("t"),
            "r": bbox.get("r"),
            "b": bbox.get("b"),
            "coord_origin": bbox.get("coord_origin"),
        }
    }


def text_block(item: dict[str, Any], index: int, source_name: str) -> dict[str, Any] | None:
    text = str(item.get("text") or "").strip()
    if not text:
        return None
    prov = first_prov(item)
    page_no = prov.get("page_no")
    block_id = f"docling-text-{index:05d}"
    source_span_id = f"span-{block_id}"
    return {
        "block_id": block_id,
        "block_type": "text",
        "sequence_index": index,
        "label": item.get("label") or "text",
        "text": text,
        "display_label": f"{page_label(prov)} · 文本 {index:05d}",
        "source_span": {
            "source_span_id": source_span_id,
            "source_document": source_name,
            "page_no": page_no,
            "parser": "docling",
            "parser_ref": item.get("self_ref"),
            **bbox_to_span(prov),
        },
      }


def image_block(item: dict[str, Any], index: int, source_name: str) -> dict[str, Any]:
    prov = first_prov(item)
    page_no = prov.get("page_no")
    block_id = f"docling-picture-{index:05d}"
    source_span_id = f"span-{block_id}"
    captions = item.get("captions") if isinstance(item.get("captions"), list) else []
    caption_refs = [str(caption.get("$ref") or caption) for caption in captions]
    image = item.get("image") if isinstance(item.get("image"), dict) else {}
    size = image.get("size") if isinstance(image.get("size"), dict) else {}
    return {
        "block_id": block_id,
        "block_type": "image",
        "sequence_index": index,
        "label": item.get("label") or "picture",
        "text": "图片节点",
        "display_label": f"{page_label(prov)} · 图片 {index:05d}",
        "asset": {
            "asset_id": f"asset-{block_id}",
            "asset_type": "image",
            "file_name": f"{block_id}.png",
            "mime_type": image.get("mimetype"),
            "uri": image.get("uri"),
            "width": size.get("width"),
            "height": size.get("height"),
            "caption_refs": caption_refs,
        },
        "source_span": {
            "source_span_id": source_span_id,
            "source_document": source_name,
            "page_no": page_no,
            "parser": "docling",
            "parser_ref": item.get("self_ref"),
            **bbox_to_span(prov),
        },
    }


def limited_blocks(
    text_blocks: list[dict[str, Any]],
    image_blocks: list[dict[str, Any]],
    max_blocks: int | None,
    image_limit: int | None,
) -> list[dict[str, Any]]:
    if max_blocks is None:
        selected_text = text_blocks
    else:
        selected_text = text_blocks[:max_blocks]
    if image_limit is None:
        selected_images = image_blocks
    elif image_limit <= 0:
        selected_images = []
    else:
        selected_images = image_blocks[:image_limit]
    return selected_text + selected_images


def build_from_docling(path: Path, max_blocks: int | None = None, image_limit: int | None = 20) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_name = safe_name(path)
    text_blocks: list[dict[str, Any]] = []
    image_blocks: list[dict[str, Any]] = []
    for index, item in enumerate(data.get("texts") or [], start=1):
        if not isinstance(item, dict):
            continue
        block = text_block(item, index, source_name)
        if block:
            text_blocks.append(block)
    for index, item in enumerate(data.get("pictures") or [], start=1):
        if isinstance(item, dict):
            image_blocks.append(image_block(item, index, source_name))

    # Docling picture nodes often lack page provenance in this POC. Keeping a
    # bounded text sample plus a bounded image sample avoids both failure modes:
    # a preview filled only with unknown-page images, or a preview with no images.
    blocks = limited_blocks(text_blocks, image_blocks, max_blocks, image_limit)
    selected_image_count = sum(1 for block in blocks if block["block_type"] == "image")
    return {
        "schema": "document_blocks_poc.v2",
        "source_format": "docling",
        "source_file": path.name,
        "parser": "docling",
        "block_count": len(blocks),
        "text_block_count": len(blocks) - selected_image_count,
        "image_block_count": selected_image_count,
        "source_text_block_count": len(text_blocks),
        "source_image_block_count": len(image_blocks),
        "blocks": blocks,
    }


def _pdf_image_data_uri(doc: Any, xref: int) -> tuple[str, str, int, int]:
    """Extract a single image by xref and return (data_uri, mime_type, width, height).

    Returns empty strings and zero dimensions if extraction fails. This is a
    best-effort extraction: malformed images are skipped rather than aborting
    the whole document.
    """
    try:
        base_image = doc.extract_image(xref)
    except Exception:
        return "", "", 0, 0
    image_bytes = base_image.get("image") or b""
    if not image_bytes:
        return "", "", 0, 0
    mime_type = base_image.get("ext") or "png"
    if not mime_type.startswith("image/"):
        mime_type = f"image/{mime_type}"
    width = int(base_image.get("width") or 0)
    height = int(base_image.get("height") or 0)
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}", mime_type, width, height


def _pdf_render_image_region(page: Any, bbox: tuple[float, float, float, float], dpi: int = 300) -> tuple[str, int, int]:
    """Render a page region to PNG and return (data_uri, width, height).

    This is used when ``extract_image(xref)`` returns an unusable byte stream
    (typically because LibreOffice encodes images as vector drawing commands
    rather than embedded bitmaps). Rendering the bbox via ``get_pixmap`` is
    slower but produces a real PNG.
    """
    import pymupdf

    x0, y0, x1, y1 = bbox
    clip = pymupdf.Rect(x0, y0, x1, y1)
    pix = page.get_pixmap(clip=clip, dpi=dpi)
    png_bytes = pix.tobytes("png")
    encoded = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}", pix.width, pix.height


def _pdf_bbox_to_span(page_index: int, block_bbox: tuple[float, float, float, float]) -> dict[str, Any]:
    """Convert a PyMuPDF block bbox (x0, y0, x1, y1) to a source_span bbox.

    PyMuPDF uses top-left origin with y growing downward, matching the
    ``l, t, r, b`` convention used elsewhere in this POC.
    """
    x0, y0, x1, y1 = block_bbox
    return {
        "bbox": {
            "l": round(x0, 3),
            "t": round(y0, 3),
            "r": round(x1, 3),
            "b": round(y1, 3),
            "coord_origin": "top-left",
        }
    }


def build_from_pdf(path: Path, max_blocks: int | None = None, image_limit: int | None = 20) -> dict[str, Any]:
    """Build DocumentBlock JSON from a PDF produced by LibreOffice.

    Text blocks are extracted per page via ``page.get_text("blocks")``, which
    returns (x0, y0, x1, y1, text, block_no, block_type) tuples. Image blocks
    are extracted via ``page.get_image_info(xrefs=True)`` so each entry carries
    the image's actual on-page bbox. This is required because LibreOffice
    PDFs register every page's full resource table, so ``page.get_images()``
    returns the same xref list on every page even when the image is not
    visually present.

    Images are deduplicated across the document by (xref, rounded bbox) so the
    same embedded picture is only emitted once per visible location.
    """
    try:
        import pymupdf
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "PyMuPDF is not installed for this Python environment.\n"
            "Install it first:\n"
            "  python -m pip install pymupdf\n"
            "Then rerun this script."
        ) from exc

    doc = pymupdf.open(str(path))
    source_name = path.stem
    text_blocks: list[dict[str, Any]] = []
    image_blocks: list[dict[str, Any]] = []
    seen_image_keys: set[tuple[int, int, int, int]] = set()

    text_sequence = 0
    image_sequence = 0

    for page_index in range(doc.page_count):
        page = doc[page_index]
        page_no = page_index + 1
        page_label = f"第 {page_no} 页"

        # Text blocks: filter out empty or whitespace-only fragments.
        for raw_block in page.get_text("blocks") or []:
            if not isinstance(raw_block, (tuple, list)) or len(raw_block) < 5:
                continue
            block_type = raw_block[6] if len(raw_block) > 6 else 0
            # block_type 0 = text, 1 = image, 2 = lattice; only take text here.
            if block_type != 0:
                continue
            text = str(raw_block[4] or "").strip()
            if not text:
                continue
            text_sequence += 1
            block_id = f"pdf-text-{page_no:03d}-{text_sequence:05d}"
            bbox = (float(raw_block[0]), float(raw_block[1]), float(raw_block[2]), float(raw_block[3]))
            text_blocks.append({
                "block_id": block_id,
                "block_type": "text",
                "sequence_index": text_sequence,
                "label": "text",
                "text": text,
                "display_label": f"{page_label} · 文本 {text_sequence:05d}",
                "source_span": {
                    "source_span_id": f"span-{block_id}",
                    "source_document": source_name,
                    "page_no": page_no,
                    "parser": "libreoffice-pdf",
                    "parser_ref": f"page={page_no};block={text_sequence}",
                    **_pdf_bbox_to_span(page_index, bbox),
                },
            })

        # Image blocks: only emit images that are actually placed on this page.
        # ``get_images(full=True)`` is unreliable on LibreOffice PDFs because
        # the resource table is mirrored per page. ``get_image_info(xrefs=True)``
        # returns bbox + xref for every visually rendered image.
        for image_info in page.get_image_info(xrefs=True) or []:
            xref = image_info.get("xref")
            if xref is None:
                continue
            bbox_tuple = image_info.get("bbox") or ()
            if len(bbox_tuple) < 4:
                continue
            # Round bbox to integer pixels for stable deduplication across runs.
            key = (
                int(xref),
                round(float(bbox_tuple[0])),
                round(float(bbox_tuple[1])),
                round(float(bbox_tuple[2])),
                round(float(bbox_tuple[3])),
            )
            if key in seen_image_keys:
                continue
            seen_image_keys.add(key)
            data_uri, mime_type, width, height = _pdf_image_data_uri(doc, int(xref))
            if not data_uri:
                continue
            # Heuristic: LibreOffice PDFs often encode images as vector drawing
            # commands, so ``extract_image`` returns a tiny placeholder byte
            # stream (typically ~100 bytes for a 176x27 image). When the byte
            # count is implausibly small for the declared dimensions, fall
            # back to rendering the bbox region as a PNG via ``get_pixmap``.
            declared_pixels = max(width, 1) * max(height, 1)
            decoded_bytes = len(data_uri.split(",", 1)[-1]) * 3 // 4 if "," in data_uri else 0
            min_expected = max(declared_pixels // 4, 200)
            if decoded_bytes < min_expected:
                bbox_values = [float(v) for v in bbox_tuple]
                try:
                    rendered_uri, rendered_w, rendered_h = _pdf_render_image_region(page, bbox_values)
                    data_uri = rendered_uri
                    mime_type = "image/png"
                    width = rendered_w
                    height = rendered_h
                except Exception:
                    # If rendering also fails, skip this image entirely.
                    continue
            image_sequence += 1
            block_id = f"pdf-image-{page_no:03d}-{image_sequence:05d}"
            image_blocks.append({
                "block_id": block_id,
                "block_type": "image",
                "sequence_index": image_sequence,
                "label": "picture",
                "text": "图片节点",
                "display_label": f"{page_label} · 图片 {image_sequence:05d}",
                "asset": {
                    "asset_id": f"asset-{block_id}",
                    "asset_type": "image",
                    "file_name": f"{block_id}.png",
                    "mime_type": mime_type,
                    "uri": data_uri,
                    "width": int(image_info.get("width") or width),
                    "height": int(image_info.get("height") or height),
                    "caption_refs": [],
                },
                "source_span": {
                    "source_span_id": f"span-{block_id}",
                    "source_document": source_name,
                    "page_no": page_no,
                    "parser": "libreoffice-pdf",
                    "parser_ref": f"page={page_no};xref={xref};seq={image_info.get('number')}",
                    **_pdf_bbox_to_span(page_index, tuple(bbox_tuple)),
                },
            })

    doc.close()

    blocks = limited_blocks(text_blocks, image_blocks, max_blocks, image_limit)
    selected_image_count = sum(1 for block in blocks if block["block_type"] == "image")
    return {
        "schema": "document_blocks_poc.v2",
        "source_format": "libreoffice-pdf",
        "source_file": path.name,
        "parser": "libreoffice-pdf",
        "block_count": len(blocks),
        "text_block_count": len(blocks) - selected_image_count,
        "image_block_count": selected_image_count,
        "source_text_block_count": len(text_blocks),
        "source_image_block_count": len(image_blocks),
        "blocks": blocks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build local DocumentBlock JSON from Docling JSON or LibreOffice PDF."
    )
    parser.add_argument("input", type=Path, help="Docling JSON file/dir, or PDF file when --from-pdf is set.")
    parser.add_argument("--out-dir", type=Path, default=Path("docs/document-block-poc-results"))
    parser.add_argument("--max-blocks", type=int, default=None, help="Optional cap for text blocks in prototype smoke testing.")
    parser.add_argument("--image-limit", type=int, default=20, help="Number of image blocks to append for mixed content testing. Use 0 to omit images.")
    parser.add_argument(
        "--from-pdf",
        action="store_true",
        help="Build from a LibreOffice-produced PDF instead of Docling JSON. When set, input must be a single .pdf file.",
    )
    args = parser.parse_args()

    if args.from_pdf:
        if not args.input.is_file() or args.input.suffix.lower() != ".pdf":
            print(f"ERROR: --from-pdf requires a single .pdf file. Got: {args.input}")
            return 1
        inputs = [args.input]
    else:
        inputs = sorted(args.input.glob("*.docling.json")) if args.input.is_dir() else [args.input]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for source in inputs:
        if not source.exists():
            raise FileNotFoundError(source)
        if args.from_pdf:
            payload = build_from_pdf(source, args.max_blocks, args.image_limit)
        else:
            payload = build_from_docling(source, args.max_blocks, args.image_limit)
        out_path = args.out_dir / f"{safe_name(source)}.document-blocks.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"OK {source.name} blocks={payload['block_count']} "
            f"text={payload['text_block_count']} images={payload['image_block_count']} out={out_path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
