"""컬럼 매핑과 형식 변경(drift) 탐지.

매핑 방법: exact(정규화 후 일치) / synonym(동의어) / fuzzy(유사도, 사용자 확인 필요) / manual(사용자 지정)
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Mapping

from .normalize import CONVERTERS
from .parsers.common import ParsedTable

FUZZY_THRESHOLD = 0.72


def norm_header(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    return re.sub(r"[\s_\-./:]", "", s)


def _type_ok_ratio(values: list[Any], ctype: str) -> float:
    conv = CONVERTERS.get(ctype, CONVERTERS["text"])
    sample = [v for v in values[:200] if v is not None and str(v).strip() != ""]
    if not sample:
        return 1.0
    ok = sum(1 for v in sample if conv(v)[1] is None)
    return ok / len(sample)


def map_columns(table: ParsedTable, spec: Mapping[str, Mapping[str, Any]],
                overrides: Mapping[str, str] | None = None) -> dict[str, Any]:
    overrides = dict(overrides or {})
    src_norm = {c: norm_header(c) for c in table.columns}
    candidates: list[tuple[float, str, str, str]] = []  # (score, field, src, method)
    for field, fs in spec.items():
        if field in overrides:
            continue
        names = [fs.get("label", field), field] + list(fs.get("synonyms", []))
        nnames = {norm_header(n) for n in names}
        for src, ns in src_norm.items():
            if ns in nnames:
                method = "exact" if ns == norm_header(fs.get("label", field)) else "synonym"
                candidates.append((1.0, field, src, method))
            else:
                best = max(SequenceMatcher(None, ns, n).ratio() for n in nnames) if nnames else 0
                if best >= FUZZY_THRESHOLD:
                    candidates.append((round(best, 3), field, src, "fuzzy"))
    candidates.sort(key=lambda x: (-x[0], x[1]))
    assigned: dict[str, dict[str, Any]] = {}
    used_src: set[str] = set()
    for field, src in overrides.items():
        if src not in table.columns:
            assigned[field] = {"source": None, "method": "manual", "confidence": 0,
                               "error": f"지정한 원천 컬럼 '{src}'이 없습니다."}
            continue
        assigned[field] = {"source": src, "method": "manual", "confidence": 1.0}
        used_src.add(src)
    for score, field, src, method in candidates:
        if field in assigned or src in used_src:
            continue
        assigned[field] = {"source": src, "method": method, "confidence": score}
        used_src.add(src)
    result: dict[str, Any] = {"fields": {}, "unmapped_required": [], "needs_confirmation": [],
                              "type_issues": [], "extra_source_columns": []}
    for field, fs in spec.items():
        m = assigned.get(field, {"source": None, "method": "unmapped", "confidence": 0})
        if m.get("source"):
            idx = table.columns.index(m["source"])
            ratio = _type_ok_ratio([r[idx] for r in table.rows], fs.get("type", "text"))
            m["type_ok_ratio"] = round(ratio, 4)
            if ratio < 0.9:
                result["type_issues"].append({"field": field, "source": m["source"], "ok_ratio": round(ratio, 4)})
            if m["method"] == "fuzzy":
                result["needs_confirmation"].append(field)
        elif fs.get("required", False):
            result["unmapped_required"].append(field)
        m["label"] = fs.get("label", field)
        m["required"] = bool(fs.get("required", False))
        result["fields"][field] = m
    result["extra_source_columns"] = [c for c in table.columns if c not in used_src]
    req = [f for f, fs in spec.items() if fs.get("required")]
    hit = sum(1 for f in req if result["fields"][f].get("source"))
    result["score"] = round(hit / len(req), 4) if req else 0.0
    return result


def best_table(tables: list[ParsedTable], spec: Mapping[str, Mapping[str, Any]],
               overrides: Mapping[str, str] | None = None) -> tuple[ParsedTable | None, dict[str, Any] | None]:
    best: tuple[ParsedTable | None, dict[str, Any] | None] = (None, None)
    for t in tables:
        m = map_columns(t, spec, overrides)
        if best[1] is None or m["score"] > best[1]["score"]:
            best = (t, m)
    return best


def layout_of(table: ParsedTable, mapping: Mapping[str, Any], filename: str) -> dict[str, Any]:
    return {
        "table": table.name, "columns": list(table.columns), "row_count": len(table.rows),
        "unit": (table.meta.get("unit") or {}).get("label"), "filename": filename,
        "field_sources": {f: m.get("source") for f, m in mapping["fields"].items()},
    }


def detect_drift(current: Mapping[str, Any], previous: Mapping[str, Any] | None,
                 row_change_threshold: float = 0.3) -> list[dict[str, Any]]:
    """이전 승인 실행의 입력 레이아웃과 비교한 변경 목록."""
    if not previous:
        return []
    changes: list[dict[str, Any]] = []
    if current["table"] != previous["table"]:
        changes.append({"type": "SHEET_RENAMED", "detail": f"시트/표 '{previous['table']}' → '{current['table']}'"})
    prev_cols, cur_cols = list(previous["columns"]), list(current["columns"])
    removed = [c for c in prev_cols if c not in cur_cols]
    added = [c for c in cur_cols if c not in prev_cols]
    for r in list(removed):
        match = max(added, key=lambda a: SequenceMatcher(None, norm_header(r), norm_header(a)).ratio(), default=None)
        if match and SequenceMatcher(None, norm_header(r), norm_header(match)).ratio() >= 0.4:
            changes.append({"type": "COLUMN_RENAMED", "detail": f"'{r}' → '{match}' (추정)"})
            removed.remove(r)
            added.remove(match)
    for r in removed:
        changes.append({"type": "COLUMN_REMOVED", "detail": f"'{r}' 삭제"})
    for a in added:
        changes.append({"type": "COLUMN_ADDED", "detail": f"'{a}' 추가"})
    if not removed and not added and prev_cols != cur_cols and set(prev_cols) == set(cur_cols):
        changes.append({"type": "COLUMN_ORDER_CHANGED", "detail": "컬럼 순서 변경"})
    for f, src in current.get("field_sources", {}).items():
        psrc = previous.get("field_sources", {}).get(f)
        if psrc and src and psrc != src:
            changes.append({"type": "MAPPING_CHANGED", "detail": f"필드 '{f}': '{psrc}' → '{src}'"})
    if current.get("unit") != previous.get("unit"):
        changes.append({"type": "UNIT_CHANGED", "detail": f"단위 표기 {previous.get('unit')} → {current.get('unit')}"})
    pr, cr = previous.get("row_count") or 0, current.get("row_count") or 0
    if pr and abs(cr - pr) / pr > row_change_threshold:
        changes.append({"type": "ROW_COUNT_CHANGED", "detail": f"행 수 {pr} → {cr} ({(cr - pr) / pr:+.0%})"})
    if norm_header(re.sub(r"\d", "", previous.get("filename", ""))) != norm_header(re.sub(r"\d", "", current.get("filename", ""))):
        changes.append({"type": "FILENAME_PATTERN_CHANGED",
                        "detail": f"파일명 패턴 '{previous.get('filename')}' → '{current.get('filename')}'"})
    return changes
