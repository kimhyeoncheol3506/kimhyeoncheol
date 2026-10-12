"""업무 식별(기존 템플릿 매칭)과 신규 업무 초안 제안.

로컬 휴리스틱만 사용한다(외부 AI 미사용). 결과는 '추정'이며 사용자가 확인·승인해야 한다.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .normalize import is_blank
from .parsers import ParseError, ParsedTable, parse_file
from .profiler import profile_column
from .schema_mapper import map_columns, norm_header

MATCH_THRESHOLD = 0.6


def _table_from_meta(t: dict[str, Any]) -> ParsedTable:
    return ParsedTable(t["name"], t["columns"], t.get("preview", []), [], t.get("header_row"), t.get("meta", {}))


def score_file_for_role(file_rec: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    meta = file_rec.get("metadata") or {}
    best = {"score": 0.0, "table": None, "mapping": None}
    for t in meta.get("tables", []):
        m = map_columns(_table_from_meta(t), spec["columns"])
        if m["score"] > best["score"] or best["table"] is None:
            best = {"score": m["score"], "table": t["name"], "mapping": m}
    name = file_rec["original_name"].lower()
    hints = [h for h in spec.get("filename_hints", []) if h.lower() in name]
    total = round(best["score"] * 0.85 + (0.15 if hints else 0), 4)
    matched = [f for f, v in (best["mapping"] or {}).get("fields", {}).items() if v.get("source")]
    return {"score": total, "column_score": best["score"], "table": best["table"], "filename_hints": hints,
            "matched_fields": matched, "missing_required": (best["mapping"] or {}).get("unmapped_required", [])}


def match_templates(files: list[dict[str, Any]], templates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    usable = [f for f in files if f["status"] == "PARSED"]
    out = []
    for t in templates:
        body = t["body"]
        pairs = []
        for role, spec in body["inputs"].items():
            for f in usable:
                s = score_file_for_role(f, spec)
                pairs.append((s["score"], role, f["id"], s))
        pairs.sort(key=lambda x: -x[0])
        assigned: dict[str, dict[str, Any]] = {}
        used: set[str] = set()
        for score, role, fid, s in pairs:
            if role in assigned or fid in used or score < 0.3:
                continue
            assigned[role] = {"file_id": fid, **s}
            used.add(fid)
        req = [r for r, s in body["inputs"].items() if s.get("required", True)]
        score = sum(assigned[r]["score"] if r in assigned else 0 for r in req) / max(1, len(req))
        evidence = []
        for r, a in assigned.items():
            evidence.append(f"{body['inputs'][r].get('label', r)} ← 파일 {a['file_id'][:8]}: 컬럼 {len(a['matched_fields'])}개 매칭"
                            + (f", 파일명 키워드 {a['filename_hints']}" if a['filename_hints'] else ""))
        missing_roles = [r for r in req if r not in assigned]
        out.append({"template_key": t["template_key"], "version": t["version"], "name": t["name"],
                    "score": round(score, 4), "assignments": assigned, "missing_roles": missing_roles,
                    "evidence": evidence, "is_candidate": score >= MATCH_THRESHOLD and not missing_roles})
    out.sort(key=lambda x: -x["score"])
    return out


def _type_of(profile: dict[str, Any]) -> str:
    t = profile.get("inferred_type")
    return {"number": "decimal", "date": "date"}.get(t, "text")


def draft_new_workflow(files: list[dict[str, Any]], max_rows: int = 200_000) -> dict[str, Any]:
    """두 개 이상의 표 파일에서 공통 키·비교 금액을 추정해 generic_recon 초안을 만든다."""
    tabs = []
    for f in files:
        if f["status"] != "PARSED" or len(tabs) == 2:
            continue
        try:
            pf = parse_file(Path(f["stored_path"]), f["ext"], f["original_name"], max_rows)
        except ParseError:
            continue
        if pf.tables:
            t = max(pf.tables, key=lambda x: len(x.rows))
            tabs.append((f, t))
    if len(tabs) < 2:
        return {"ok": False, "reason": "대사형 업무를 추정하려면 표 데이터가 있는 파일 2개 이상이 필요합니다.",
                "uncertainties": ["업무 목적을 판단할 근거가 부족합니다. 업무 설명과 계산 규칙을 직접 입력하세요."]}
    (fa, ta), (fb, tb) = tabs
    nb = {norm_header(c): c for c in tb.columns}
    common = [(c, nb[norm_header(c)]) for c in ta.columns if norm_header(c) in nb]
    uncertainties: list[str] = []
    cols_a = {c: [r[i] for r in ta.rows] for i, c in enumerate(ta.columns)}
    cols_b = {c: [r[i] for r in tb.rows] for i, c in enumerate(tb.columns)}
    fields: dict[str, dict[str, Any]] = {}
    key_fields, compare_fields, date_field = [], [], None
    for i, (ca, cb) in enumerate(common):
        pa, pb = profile_column(cols_a[ca]), profile_column(cols_b[cb])
        ftype = _type_of(pa)
        fname = f"f{i + 1}"
        fields[fname] = {"label": ca, "type": ftype, "required": False, "synonyms": [cb] if cb != ca else []}
        va = {str(v).strip() for v in cols_a[ca] if not is_blank(v)}
        vb = {str(v).strip() for v in cols_b[cb] if not is_blank(v)}
        overlap = len(va & vb) / max(1, min(len(va), len(vb)))
        uniq = pa["unique"] / max(1, pa["count"] - pa["missing"])
        if ftype == "text" and uniq >= 0.95 and overlap >= 0.5:
            key_fields.append(fname)
            fields[fname]["type"] = "code"
        elif ftype == "decimal":
            compare_fields.append(fname)
        elif ftype == "date" and date_field is None:
            date_field = fname
    for k in key_fields:
        fields[k]["required"] = True
    for c in compare_fields:
        fields[c]["required"] = True
    if not key_fields:
        uncertainties.append("두 파일을 연결할 고유 키 컬럼을 찾지 못했습니다. 결합 키를 직접 지정하세요.")
    if not compare_fields:
        uncertainties.append("비교할 공통 숫자 컬럼을 찾지 못했습니다.")
    uncertainties.append("업무 목적·계산 규칙·중요성 기준은 시스템이 확정하지 않습니다. 담당자가 확인 후 저장하세요.")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    body = {
        "template_key": f"DRAFT_RECON_{ts}",
        "name": f"(초안) {fa['original_name']} ↔ {fb['original_name']} 대사",
        "description": "시스템이 공통 컬럼을 근거로 추정한 대사 업무 초안입니다. 검토·수정 후 저장하세요.",
        "department": "회계팀", "frequency": "MONTHLY", "workflow_type": "generic_recon", "approver_role": "approver",
        "inputs": {
            "left": {"label": f"자료 A ({fa['original_name']})", "required": True, "key": key_fields,
                     "filename_hints": [re.sub(r"[\d_\-.]+", "", fa['original_name'].rsplit('.', 1)[0])[:10]], "columns": fields},
            "right": {"label": f"자료 B ({fb['original_name']})", "required": True, "key": key_fields,
                      "filename_hints": [re.sub(r"[\d_\-.]+", "", fb['original_name'].rsplit('.', 1)[0])[:10]],
                      "columns": {k: {**v, "synonyms": list({*v.get("synonyms", []), v["label"]})} for k, v in fields.items()}},
        },
        "base_date_rules": {"current_inputs": ["left", "right"], "field": date_field} if date_field else {"current_inputs": []},
        "recon": {"keys": key_fields, "compare": [{"field": c, "tolerance": "0"} for c in compare_fields],
                  "amount_field": compare_fields[0] if compare_fields else None, "carry": []},
        "calculations": [],
        "variance": {"mandatory": False, "materiality": {}},
    }
    return {"ok": bool(key_fields), "template": body, "common_columns": common, "key_fields": key_fields,
            "compare_fields": compare_fields, "date_field": date_field, "uncertainties": uncertainties,
            "files": [fa["id"], fb["id"]]}
