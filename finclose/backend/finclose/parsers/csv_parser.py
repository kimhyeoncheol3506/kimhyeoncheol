"""CSV 판독. 국내 시스템에서 흔한 CP949(EUC-KR) 인코딩을 지원한다."""
from __future__ import annotations

import csv
import io
from pathlib import Path

from .common import ParsedFile, ParseError, build_table, detect_base_date, detect_unit

ENCODINGS = ("utf-8-sig", "cp949")


def parse_csv(path: Path, filename: str, max_rows: int) -> ParsedFile:
    raw = path.read_bytes()
    if b"\x00" in raw[:4096]:
        raise ParseError("텍스트 CSV가 아닙니다(이진 데이터 포함).")
    text = None
    used = None
    for enc in ENCODINGS:
        try:
            text = raw.decode(enc)
            used = enc
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise ParseError("문자 인코딩을 판별할 수 없습니다(UTF-8, CP949 지원).")
    if not text.strip():
        raise ParseError("빈 파일입니다.")
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=",\t;|")
        delim = dialect.delimiter
    except csv.Error:
        delim = ","
    grid = [row for row in csv.reader(io.StringIO(text), delimiter=delim)]
    positions = [f"R{i + 1}" for i in range(len(grid))]
    table, warnings = build_table("CSV", grid, positions, max_rows)
    texts = [" ".join(r) for r in grid[:15]]
    meta = {"encoding": used, "delimiter": delim, "line_count": len(grid),
            "base_date": detect_base_date(texts, filename), "unit": detect_unit(texts)}
    tables = []
    if table:
        table.meta["unit"] = detect_unit(table.meta.get("pre_header_text", []) + table.columns)
        tables.append(table)
    return ParsedFile("csv", tables, meta, warnings)
