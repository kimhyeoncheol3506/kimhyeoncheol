"""파일 형식별 판독기 디스패처."""
from __future__ import annotations

from pathlib import Path

from .common import ParsedFile, ParsedTable, ParseError
from .csv_parser import parse_csv
from .excel import parse_excel
from .pdf import parse_pdf

__all__ = ["parse_file", "ParsedFile", "ParsedTable", "ParseError"]


def parse_file(path: Path, ext: str, filename: str, max_rows: int = 200_000) -> ParsedFile:
    if path.stat().st_size == 0:
        raise ParseError("빈 파일입니다.")
    if ext in ("xlsx", "xlsm"):
        return parse_excel(path, filename, max_rows)
    if ext in ("csv", "txt"):
        return parse_csv(path, filename, max_rows)
    if ext == "pdf":
        return parse_pdf(path, filename, max_rows)
    raise ParseError(f"지원하지 않는 형식: {ext}")
