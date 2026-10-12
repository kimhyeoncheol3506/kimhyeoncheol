from finclose.parsers.common import ParsedTable
from finclose.schema_mapper import detect_drift, layout_of, map_columns

SPEC = {
    "code": {"label": "종목코드", "type": "code", "required": True, "synonyms": ["ISIN"]},
    "quantity": {"label": "보유수량", "type": "decimal", "required": True, "synonyms": ["액면금액"]},
    "book": {"label": "장부금액", "type": "money", "required": True},
}


def t(cols, rows=None):
    return ParsedTable("S", cols, rows or [["KR1", "10", "100"]], ["R2"], 1)


def test_exact_and_synonym():
    m = map_columns(t(["종목코드", "액면금액", "장부금액"]), SPEC)
    assert m["fields"]["code"]["method"] == "exact"
    assert m["fields"]["quantity"]["method"] == "synonym"
    assert m["score"] == 1.0 and not m["needs_confirmation"]


def test_fuzzy_requires_confirmation_and_unmapped():
    m = map_columns(t(["종목 코드(표준)", "보유 수량합", "기타"]), SPEC)
    assert m["fields"]["code"]["method"] == "exact"  # 괄호·공백 정규화
    assert "quantity" in m["needs_confirmation"]
    assert m["unmapped_required"] == ["book"]


def test_manual_override_and_bad_override():
    m = map_columns(t(["A", "B", "C"]), SPEC, {"code": "A", "quantity": "B", "book": "Z"})
    assert m["fields"]["code"]["method"] == "manual"
    assert m["fields"]["book"]["error"]


def test_type_issue():
    m = map_columns(t(["종목코드", "보유수량", "장부금액"], [["KR1", "abc", "x"], ["KR2", "def", "y"]]), SPEC)
    assert {i["field"] for i in m["type_issues"]} == {"quantity", "book"}


def test_drift_detection():
    prev = layout_of(t(["종목코드", "보유수량", "장부금액"]), map_columns(t(["종목코드", "보유수량", "장부금액"]), SPEC), "보유_20260831.xlsx")
    cur_t = ParsedTable("Holdings", ["ISIN코드", "보유수량", "장부금액", "담보"], [["KR1", "1", "1", "Y"]] * 2, ["R"] * 2, 1,
                        {"unit": {"label": "천원"}})
    cur = layout_of(cur_t, map_columns(cur_t, SPEC), "holding_v2.xlsx")
    types = {c["type"] for c in detect_drift(cur, prev)}
    assert {"SHEET_RENAMED", "COLUMN_RENAMED", "COLUMN_ADDED", "MAPPING_CHANGED", "UNIT_CHANGED", "ROW_COUNT_CHANGED",
            "FILENAME_PATTERN_CHANGED"} <= types


def test_no_drift_same_layout_different_date_in_filename():
    tbl = t(["종목코드", "보유수량", "장부금액"])
    a = layout_of(tbl, map_columns(tbl, SPEC), "보유_20260831.xlsx")
    b = layout_of(tbl, map_columns(tbl, SPEC), "보유_20260930.xlsx")
    assert detect_drift(b, a) == []
