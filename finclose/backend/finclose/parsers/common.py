"""파서 공통 구조와 헤더/기준일/단위 탐지."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from ..normalize import is_blank, to_date


class ParseError(Exception):
    """판독 불가(손상, 암호화, 미지원 형식). 사용자에게 그대로 보여줄 메시지를 담는다."""


@dataclass
class ParsedTable:
    name: str                        # 시트명 또는 'page1-3:table1'
    columns: list[str]
    rows: list[list[Any]]
    source_rows: list[str]           # 원천 위치(예: '시트1!R5', 'p2 표1 r3')
    header_row: int | None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_records(self) -> list[dict[str, Any]]:
        return [dict(zip(self.columns, r)) for r in self.rows]


@dataclass
class ParsedFile:
    kind: str
    tables: list[ParsedTable]
    metadata: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "metadata": self.metadata,
            "warnings": self.warnings,
            "tables": [
                {"name": t.name, "columns": t.columns, "row_count": len(t.rows), "header_row": t.header_row,
                 "meta": t.meta, "preview": [[_jsonable(v) for v in r] for r in t.rows[:5]]}
                for t in self.tables
            ],
        }


def _jsonable(v: Any) -> Any:
    if isinstance(v, (date,)):
        return v.isoformat()
    if isinstance(v, float) and v != v:
        return None
    if v is None or isinstance(v, (int, float, str, bool)):
        return v
    return str(v)


_META_CELL = re.compile(r"[:：]|단위|^\(.*\)$")


def detect_header(rows: list[list[Any]], scan: int = 30) -> int | None:
    """헤더 행 추정(0-based).

    - 문자열 셀 수가 상위권인 첫 행을 고른다. '기준일: …', '(단위: 천원)' 같은 메타 셀은 세지 않는다.
    - 다음 데이터 행(빈 행 1개까지 허용)이 헤더 위치의 절반 이상을 채워야 한다(제목·메타 행 오인 방지).
    """
    def score(r: list[Any]) -> int:
        n = 0
        for v in r:
            if isinstance(v, str) and v.strip() and not re.fullmatch(r"[-+0-9.,\s()%]+", v.strip()) \
                    and not _META_CELL.search(v.strip()):
                n += 1
        return n

    head = rows[:scan]
    if not head:
        return None
    scores = [score(r) for r in head]
    best = max(scores)
    if best < 2:
        return None
    need = max(2, -(-best * 4 // 5))  # ceil(best*0.8)
    for i, s in enumerate(scores):
        if s < need:
            continue
        pos = [j for j, v in enumerate(head[i]) if not is_blank(v)]
        following = [r for r in rows[i + 1:i + 3] if any(not is_blank(v) for v in r)]
        nxt = following[0] if following else []
        filled = sum(1 for j in pos if j < len(nxt) and not is_blank(nxt[j]))
        if pos and filled * 2 >= len(pos):
            return i
    return None


def make_columns(header: list[Any]) -> list[str]:
    cols: list[str] = []
    seen: dict[str, int] = {}
    for i, v in enumerate(header):
        name = str(v).strip() if not is_blank(v) else f"열{i + 1}"
        name = re.sub(r"\s+", " ", name)
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        cols.append(name)
    return cols


def trim_trailing_empty_columns(header: list[Any], rows: list[list[Any]]) -> int:
    width = len(header)
    while width > 0 and is_blank(header[width - 1]) and all(
        len(r) < width or is_blank(r[width - 1]) for r in rows
    ):
        width -= 1
    return width


_UNIT_RE = re.compile(r"단위\s*[:：]?\s*(원|천\s*원|백만\s*원|억\s*원)")
_UNITS = {"원": 1, "천원": 1000, "백만원": 1_000_000, "억원": 100_000_000}


def detect_unit(texts: list[str]) -> dict[str, Any] | None:
    for t in texts:
        m = _UNIT_RE.search(t or "")
        if m:
            label = m.group(1).replace(" ", "")
            return {"label": label, "multiplier": _UNITS[label], "evidence": t.strip()[:80]}
    return None


_BASE_DATE_RE = re.compile(r"(기준일|평가일|기준일자|as of)\s*[:：]?\s*(\d{4}[-./]\d{1,2}[-./]\d{1,2}|\d{8})", re.I)
_FILENAME_DATE_RE = re.compile(r"(20\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])")


def detect_base_date(texts: list[str], filename: str) -> dict[str, Any] | None:
    for t in texts:
        m = _BASE_DATE_RE.search(t or "")
        if m:
            d, _ = to_date(m.group(2).replace("/", "-").replace(".", "-"))
            if d:
                return {"date": d.isoformat(), "source": "content", "evidence": t.strip()[:80]}
    m = _FILENAME_DATE_RE.search(filename)
    if m:
        try:
            d = date(int(m[1]), int(m[2]), int(m[3]))
            return {"date": d.isoformat(), "source": "filename", "evidence": filename}
        except ValueError:
            pass
    return None


def build_table(name: str, grid: list[list[Any]], positions: list[str], max_rows: int,
                meta: dict[str, Any] | None = None) -> tuple[ParsedTable | None, list[str]]:
    """2차원 셀 목록 → ParsedTable. 헤더 위 행은 메타 텍스트(단위·기준일 탐지용)로 남긴다."""
    warnings: list[str] = []
    hi = detect_header(grid)
    if hi is None:
        return None, [f"[{name}] 헤더 행을 찾지 못했습니다."]
    header = grid[hi]
    body_raw = grid[hi + 1:]
    width = trim_trailing_empty_columns(header, body_raw)
    header = header[:width]
    columns = make_columns(header)
    rows: list[list[Any]] = []
    src: list[str] = []
    empty_rows = 0
    for r, pos in zip(body_raw, positions[hi + 1:]):
        r = (list(r) + [None] * width)[:width]
        if all(is_blank(v) for v in r):
            empty_rows += 1
            continue
        # 합계 행은 데이터로 취급하지 않고 메타로 분리
        first = next((v for v in r if not is_blank(v)), "")
        if isinstance(first, str) and first.strip().replace(" ", "") in ("합계", "총계", "소계", "Total", "TOTAL"):
            warnings.append(f"[{name}] {pos} 합계 행을 데이터에서 제외했습니다.")
            continue
        rows.append(r)
        src.append(pos)
        if len(rows) > max_rows:
            raise ParseError(f"[{name}] 행 수가 제한({max_rows:,})을 초과합니다.")
    pre_texts = [" ".join(str(v) for v in g if not is_blank(v)) for g in grid[:hi]]
    m = dict(meta or {})
    m.update({"empty_rows_skipped": empty_rows, "pre_header_text": pre_texts[:10]})
    return ParsedTable(name, columns, rows, src, hi + 1, m), warnings
