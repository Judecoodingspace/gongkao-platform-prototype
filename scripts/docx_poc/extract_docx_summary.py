#!/usr/bin/env python3
"""Summarize DOCX structure for parser feasibility checks.

This POC intentionally avoids writing full exam text to versioned files. It
extracts structural signals that help decide whether a DOCX can support the
annotation workbench preview: paragraphs, tables, embedded images, and block
order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


@dataclass
class BlockSummary:
    index: int
    kind: str
    text_length: int
    image_refs: int
    rows: int | None = None
    cells: int | None = None
    snippet: str | None = None


@dataclass
class DocxSummary:
    path: str
    sha256: str
    paragraphs: int
    non_empty_paragraphs: int
    tables: int
    table_cells: int
    drawing_refs: int
    embedded_image_refs: int
    media_files: int
    ordered_blocks: int
    blocks: list[BlockSummary]
    warnings: list[str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_from(element: ET.Element) -> str:
    pieces: list[str] = []
    for node in element.iter():
        if node.tag == f"{{{NS['w']}}}t" and node.text:
            pieces.append(node.text)
        elif node.tag == f"{{{NS['w']}}}tab":
            pieces.append("\t")
        elif node.tag == f"{{{NS['w']}}}br":
            pieces.append("\n")
    return "".join(pieces).strip()


def image_refs_from(element: ET.Element) -> int:
    refs = set()
    for node in element.iter():
        embed = node.attrib.get(f"{{{NS['r']}}}embed")
        link = node.attrib.get(f"{{{NS['r']}}}link")
        if embed:
            refs.add(embed)
        if link:
            refs.add(link)
    return len(refs)


def snippet(text: str, enabled: bool) -> str | None:
    if not enabled:
        return None
    clean = " ".join(text.split())
    return clean[:80]


def iter_docx_paths(inputs: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.docx")))
        else:
            paths.append(path)
    return paths


def summarize_docx(path: Path, include_snippets: bool = False) -> DocxSummary:
    warnings: list[str] = []
    blocks: list[BlockSummary] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "word/document.xml" not in names:
            raise ValueError("word/document.xml is missing")

        root = ET.fromstring(archive.read("word/document.xml"))
        body = root.find("w:body", NS)
        if body is None:
            raise ValueError("w:body is missing")

        media_files = [name for name in names if name.startswith("word/media/")]
        paragraphs = root.findall(".//w:p", NS)
        tables = root.findall(".//w:tbl", NS)
        table_cells = root.findall(".//w:tc", NS)
        drawing_refs = len(root.findall(".//w:drawing", NS))
        embedded_image_refs = len(
            {
                node.attrib.get(f"{{{NS['r']}}}embed")
                for node in root.iter()
                if node.attrib.get(f"{{{NS['r']}}}embed")
            }
        )

        non_empty_paragraphs = 0
        for child in list(body):
            if child.tag == f"{{{NS['w']}}}p":
                text = text_from(child)
                if text:
                    non_empty_paragraphs += 1
                refs = image_refs_from(child)
                if text or refs:
                    blocks.append(
                        BlockSummary(
                            index=len(blocks) + 1,
                            kind="paragraph",
                            text_length=len(text),
                            image_refs=refs,
                            snippet=snippet(text, include_snippets),
                        )
                    )
            elif child.tag == f"{{{NS['w']}}}tbl":
                rows = child.findall(".//w:tr", NS)
                cells = child.findall(".//w:tc", NS)
                text = text_from(child)
                refs = image_refs_from(child)
                blocks.append(
                    BlockSummary(
                        index=len(blocks) + 1,
                        kind="table",
                        text_length=len(text),
                        image_refs=refs,
                        rows=len(rows),
                        cells=len(cells),
                        snippet=snippet(text, include_snippets),
                    )
                )

        if media_files and embedded_image_refs == 0:
            warnings.append("Media files exist but no embedded image refs were found in document.xml.")
        if tables:
            warnings.append("Tables are present; preview fidelity must be checked visually.")
        if drawing_refs or media_files:
            warnings.append("Images are present; ownership must be verified against nearby blocks.")

    return DocxSummary(
        path=str(path),
        sha256=sha256_file(path),
        paragraphs=len(paragraphs),
        non_empty_paragraphs=non_empty_paragraphs,
        tables=len(tables),
        table_cells=len(table_cells),
        drawing_refs=drawing_refs,
        embedded_image_refs=embedded_image_refs,
        media_files=len(media_files),
        ordered_blocks=len(blocks),
        blocks=blocks,
        warnings=warnings,
    )


def write_json(summary: DocxSummary, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{Path(summary.path).stem}.summary.json"
    payload = asdict(summary)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize DOCX structure for annotation-workbench parser POC.")
    parser.add_argument("inputs", nargs="+", help="DOCX files or directories containing DOCX files.")
    parser.add_argument("--out-dir", help="Optional directory for JSON summaries. Keep this directory ignored by git.")
    parser.add_argument("--include-snippets", action="store_true", help="Include short text snippets in JSON output. Do not use for private papers.")
    args = parser.parse_args()

    paths = iter_docx_paths(args.inputs)
    if not paths:
        print("No DOCX files found.", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir) if args.out_dir else None
    failures = 0
    for path in paths:
        try:
            summary = summarize_docx(path, include_snippets=args.include_snippets)
        except Exception as exc:  # noqa: BLE001 - CLI should continue across samples.
            failures += 1
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            continue

        print(
            "OK "
            f"{path.name} | blocks={summary.ordered_blocks} "
            f"paragraphs={summary.non_empty_paragraphs}/{summary.paragraphs} "
            f"tables={summary.tables} cells={summary.table_cells} "
            f"images={summary.embedded_image_refs} media={summary.media_files}"
        )
        for warning in summary.warnings:
            print(f"  WARN {warning}")
        if out_dir:
            print(f"  JSON {write_json(summary, out_dir)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
