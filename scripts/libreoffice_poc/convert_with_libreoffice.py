#!/usr/bin/env python3
"""Convert local DOCX samples with LibreOffice headless for visual-preview POC.

This script checks whether LibreOffice can render source papers into visual
preview artifacts such as PDF or HTML. It does not parse questions, infer
metadata, or write any data to a database.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


SUPPORTED_SUFFIXES = {".doc", ".docx"}
DEFAULT_FORMATS = ["pdf"]


def iter_sources(inputs: Iterable[str]) -> list[Path]:
    sources: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            for suffix in SUPPORTED_SUFFIXES:
                sources.extend(sorted(path.rglob(f"*{suffix}")))
        else:
            sources.append(path)
    return sorted(dict.fromkeys(sources))


def find_soffice(explicit: str | None = None) -> Path | str:
    if explicit:
        path = Path(explicit)
        return path if path.exists() else explicit

    for command in ("soffice", "libreoffice"):
        found = shutil.which(command)
        if found:
            return found

    common_paths = [
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
    ]
    for path in common_paths:
        if path.exists():
            return path

    raise SystemExit(
        "LibreOffice was not found.\n"
        "Install LibreOffice, or rerun with --soffice pointing to soffice.exe.\n"
        r"Common Windows path: C:\Program Files\LibreOffice\program\soffice.exe"
    )


def output_extension(convert_format: str) -> str:
    base = convert_format.split(":", 1)[0].lower()
    if base in {"html", "xhtml"}:
        return ".html"
    return f".{base}"


def safe_run_dir(out_dir: Path, source: Path, index: int) -> Path:
    name = f"{index:02d}-{source.stem}"
    run_dir = out_dir / name
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def run_convert(
    soffice: Path | str,
    source: Path,
    run_dir: Path,
    convert_format: str,
    timeout_seconds: int,
) -> dict[str, object]:
    profile_dir = run_dir / "_lo-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    before = {path.resolve() for path in run_dir.rglob("*") if path.is_file()}

    command = [
        str(soffice),
        "--headless",
        "--nologo",
        "--nodefault",
        "--nofirststartwizard",
        "--nolockcheck",
        "--norestore",
        f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
        "--convert-to",
        convert_format,
        "--outdir",
        str(run_dir),
        str(source),
    ]

    started_at = time.perf_counter()
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    elapsed_ms = round((time.perf_counter() - started_at) * 1000)
    after = {path.resolve() for path in run_dir.rglob("*") if path.is_file()}
    created = sorted(path for path in after - before if "_lo-profile" not in path.parts)
    expected = run_dir / f"{source.stem}{output_extension(convert_format)}"

    return {
        "format": convert_format,
        "elapsed_ms": elapsed_ms,
        "returncode": completed.returncode,
        "expected_output": str(expected),
        "expected_output_exists": expected.exists(),
        "created_files": [
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
            }
            for path in created
        ],
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def convert_one(
    soffice: Path | str,
    source: Path,
    out_dir: Path,
    index: int,
    formats: list[str],
    timeout_seconds: int,
) -> dict[str, object]:
    run_dir = safe_run_dir(out_dir, source, index)
    results = []
    for convert_format in formats:
        results.append(run_convert(soffice, source, run_dir, convert_format, timeout_seconds))

    summary = {
        "source": str(source),
        "run_dir": str(run_dir),
        "soffice": str(soffice),
        "formats": results,
        "manual_inspection_questions": [
            "Does the PDF or HTML visually match the Word source order?",
            "Are embedded images visible and close to their original positions?",
            "Are question numbers and A-D option labels readable in the preview?",
            "Is the output suitable as the left-side annotation preview?",
            "Can the visual output be paired with parser source blocks for provenance?",
        ],
    }
    summary_path = run_dir / "libreoffice-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert DOCX samples with LibreOffice for visual-preview POC.")
    parser.add_argument("inputs", nargs="+", help="DOC or DOCX files, or directories containing them.")
    parser.add_argument("--out-dir", default="docs/libreoffice-poc-results", help="Ignored directory for POC artifacts.")
    parser.add_argument("--format", dest="formats", action="append", help="LibreOffice --convert-to format. Can be repeated.")
    parser.add_argument("--soffice", help="Path to soffice.exe or a command name available on PATH.")
    parser.add_argument("--timeout-seconds", type=int, default=120, help="Timeout per source file and format.")
    args = parser.parse_args()

    soffice = find_soffice(args.soffice)
    sources = iter_sources(args.inputs)
    if not sources:
        print("No DOC/DOCX files found.", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    formats = args.formats or DEFAULT_FORMATS
    failures = 0
    for index, source in enumerate(sources, start=1):
        if source.suffix.lower() not in SUPPORTED_SUFFIXES:
            failures += 1
            print(f"SKIP {source}: unsupported file type", file=sys.stderr)
            continue

        try:
            summary = convert_one(soffice, source, out_dir, index, formats, args.timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            failures += 1
            print(f"FAIL {source}: timed out after {exc.timeout} seconds", file=sys.stderr)
            continue
        except Exception as exc:  # noqa: BLE001 - POC should continue across samples.
            failures += 1
            print(f"FAIL {source}: {exc}", file=sys.stderr)
            continue

        ok_formats = [
            result["format"]
            for result in summary["formats"]
            if result["returncode"] == 0 and result["expected_output_exists"]
        ]
        failed_formats = [
            result["format"]
            for result in summary["formats"]
            if result["returncode"] != 0 or not result["expected_output_exists"]
        ]
        if failed_formats:
            failures += 1
        print(
            "OK "
            f"{source.name} | ok_formats={','.join(ok_formats) or '-'} "
            f"failed_formats={','.join(failed_formats) or '-'} "
            f"run_dir={summary['run_dir']}"
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
