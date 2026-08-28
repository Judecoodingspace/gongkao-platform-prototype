#!/usr/bin/env python3
"""Run the second-stage Docling POC on local exam DOCX files.

The script converts source documents with Docling and writes ignored POC
artifacts for manual inspection. It does not split questions, infer metadata,
or write to the database.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Iterable


def import_docling():
    try:
        from docling.document_converter import DocumentConverter
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Docling is not installed for this Python environment.\n"
            "Install it first, for example:\n"
            "  python -m pip install docling\n"
            "Then rerun this script."
        ) from exc
    return DocumentConverter


def iter_sources(inputs: Iterable[str]) -> list[Path]:
    sources: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            sources.extend(sorted(path.rglob("*.docx")))
        else:
            sources.append(path)
    return sources


def count_keys(value: Any, key_names: set[str]) -> int:
    if isinstance(value, dict):
        count = sum(1 for key in value if key in key_names)
        return count + sum(count_keys(item, key_names) for item in value.values())
    if isinstance(value, list):
        return sum(count_keys(item, key_names) for item in value)
    return 0


def count_label(value: Any, label_names: set[str]) -> int:
    if isinstance(value, dict):
        count = 0
        label = value.get("label") or value.get("type") or value.get("name")
        if isinstance(label, str) and label.lower() in label_names:
            count += 1
        return count + sum(count_label(item, label_names) for item in value.values())
    if isinstance(value, list):
        return sum(count_label(item, label_names) for item in value)
    return 0


def export_html(document: Any) -> str | None:
    exporter = getattr(document, "export_to_html", None)
    if callable(exporter):
        return exporter()
    return None


def convert_one(
    converter: Any,
    source: Path,
    out_dir: Path,
    write_markdown: bool,
    write_json: bool,
) -> dict[str, Any]:
    started_at = time.perf_counter()
    result = converter.convert(str(source))
    elapsed_ms = round((time.perf_counter() - started_at) * 1000)
    document = result.document
    doc_dict = document.export_to_dict()

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    markdown_path = out_dir / f"{stem}.docling.md"
    html_path = out_dir / f"{stem}.docling.html"
    json_path = out_dir / f"{stem}.docling.json"
    summary_path = out_dir / f"{stem}.docling-summary.json"

    markdown = document.export_to_markdown()
    html = export_html(document)

    if write_markdown:
        markdown_path.write_text(markdown, encoding="utf-8")
    if html:
        html_path.write_text(html, encoding="utf-8")
    if write_json:
        json_path.write_text(json.dumps(doc_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "source": str(source),
        "elapsed_ms": elapsed_ms,
        "markdown_chars": len(markdown),
        "html_exported": html is not None,
        "dict_top_level_keys": sorted(doc_dict.keys()),
        "text_like_nodes": count_keys(doc_dict, {"text", "orig", "content"}),
        "table_like_nodes": count_label(doc_dict, {"table", "table_cell"}),
        "picture_like_nodes": count_label(doc_dict, {"picture", "image"}),
        "markdown_path": str(markdown_path) if write_markdown else None,
        "html_path": str(html_path) if html else None,
        "json_path": str(json_path) if write_json else None,
        "inspection_questions": [
            "Does Markdown preserve the question reading order?",
            "Are option labels A-D separated or merged into nearby text?",
            "Are images represented as separate picture nodes?",
            "Can each image be assigned to stem, options, explanation, or an option image group?",
            "Is the output good enough for left-side preview, or only for structured assistance?",
        ],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert DOCX samples with Docling for visual-preview POC.")
    parser.add_argument("inputs", nargs="+", help="DOCX files or directories containing DOCX files.")
    parser.add_argument("--out-dir", default="docs/docling-poc-results", help="Ignored directory for POC artifacts.")
    parser.add_argument("--write-markdown", action="store_true", help="Write Markdown exports for manual preview checks.")
    parser.add_argument("--write-json", action="store_true", help="Write full Docling JSON exports. Use only in ignored local output.")
    args = parser.parse_args()

    DocumentConverter = import_docling()
    converter = DocumentConverter()
    sources = iter_sources(args.inputs)
    if not sources:
        print("No DOCX files found.", file=sys.stderr)
        return 1

    failures = 0
    out_dir = Path(args.out_dir)
    for source in sources:
        try:
            summary = convert_one(converter, source, out_dir, args.write_markdown, args.write_json)
        except Exception as exc:  # noqa: BLE001 - POC should continue across samples.
            failures += 1
            print(f"FAIL {source}: {exc}", file=sys.stderr)
            continue

        print(
            "OK "
            f"{source.name} | markdown_chars={summary['markdown_chars']} "
            f"pictures={summary['picture_like_nodes']} "
            f"tables={summary['table_like_nodes']} "
            f"elapsed_ms={summary['elapsed_ms']}"
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
