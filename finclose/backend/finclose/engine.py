"""변환·계산·검증 실행 엔진.

템플릿의 workflow_type에 따라 파이프라인을 선택한다.
- valuation_recon : 보유내역 × 외부단가 결합 → 평가금액 계산 → 대사·검증·증감·분개초안 (채권 시연 업무)
- generic_recon   : 두 자료를 키로 대사하고 지정 필드 차이를 검증 (신규 업무 초안의 기본형)
- journal_check   : 전표 업로드 파일의 차변·대변·계정코드 검증

엔진은 순수 함수에 가깝게 유지한다: 입력(원본 파일 경로, 템플릿, 이력) → 결과 dict. DB에 쓰지 않는다.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from . import journal as jr
from . import periods
from .normalize import CONVERTERS, to_decimal
from .parsers import ParseError, ParsedTable, parse_file
from .rules import CalcError, CalcRule, RuleError, currency_decimals, run_rule_tests
from .schema_mapper import best_table, detect_drift, layout_of
from .validation import (CRITICAL, FAIL, HIGH, LOW, MEDIUM, NOT_APPLICABLE, PASS, REVIEW_REQUIRED, WARNING,
                         CheckBook, frac_to_dec, fraction_eval, fraction_round)
from .variance import compare

WORKFLOW_TYPES = ("valuation_recon", "generic_recon", "journal_check")


class TemplateError(Exception):
    pass


@dataclass
class RunContext:
    run_id: str
    template: dict[str, Any]
    base_date: date
    files: dict[str, dict[str, Any]]                    # role -> file record(stored_path, ext, original_name, sha256, id)
    overrides: dict[str, dict[str, str]] = field(default_factory=dict)
    prior_layouts: dict[str, dict[str, Any]] = field(default_factory=dict)
    history: dict[str, dict[str, Any]] = field(default_factory=dict)
    trend: list[dict[str, Any]] = field(default_factory=list)
    materiality: dict[str, Any] = field(default_factory=dict)
    max_rows: int = 200_000


@dataclass
class InputData:
    role: str
    spec: dict[str, Any]
    file: dict[str, Any] | None = None
    table: ParsedTable | None = None
    mapping: dict[str, Any] | None = None
    records: list[dict[str, Any]] = field(default_factory=list)
    layout: dict[str, Any] | None = None
    drift: list[dict[str, Any]] = field(default_factory=list)
    parse_meta: dict[str, Any] = field(default_factory=dict)
    usable: bool = False

    @property
    def columns(self) -> dict[str, Any]:
        return self.spec["columns"]


def _key(rec: Mapping[str, Any], fields: list[str]) -> tuple | None:
    vals = tuple(rec.get(f) for f in fields)
    return None if any(v is None for v in vals) else vals


def _kstr(k: tuple) -> str:
    return "|".join(str(x) for x in k)


def validate_template(t: Mapping[str, Any]) -> list[str]:
    errs: list[str] = []
    for k in ("template_key", "name", "workflow_type", "inputs"):
        if k not in t:
            errs.append(f"필수 항목 누락: {k}")
    if errs:
        return errs
    if t["workflow_type"] not in WORKFLOW_TYPES:
        errs.append(f"알 수 없는 workflow_type: {t['workflow_type']}")
    if not re.fullmatch(r"[A-Z0-9_]{3,60}", str(t["template_key"])):
        errs.append("template_key는 영문 대문자/숫자/_ 3~60자")
    for role, spec in t["inputs"].items():
        if "columns" not in spec or not spec["columns"]:
            errs.append(f"입력 '{role}'에 columns 정의 없음")
            continue
        for f, cs in spec["columns"].items():
            if cs.get("type", "text") not in CONVERTERS:
                errs.append(f"입력 '{role}.{f}' 알 수 없는 type: {cs.get('type')}")
        for kf in spec.get("key", []):
            if kf not in spec["columns"]:
                errs.append(f"입력 '{role}' key 필드 '{kf}'가 columns에 없음")
    for rd in t.get("calculations", []):
        try:
            CalcRule.from_dict(rd)
        except (RuleError, ArithmeticError, ValueError) as e:
            errs.append(f"규칙 {rd.get('rule_id')}: {e}")
    req_roles = {"valuation_recon": ("holdings", "prices"), "generic_recon": ("left", "right"),
                 "journal_check": ("journal",)}.get(t["workflow_type"], ())
    for r in req_roles:
        if r not in t["inputs"]:
            errs.append(f"{t['workflow_type']}에는 입력 역할 '{r}'이 필요")
    return errs


# --------------------------------------------------------------------------- 입력 적재 & 공통 검증

def load_inputs(ctx: RunContext, book: CheckBook) -> dict[str, InputData]:
    tpl = ctx.template
    inputs: dict[str, InputData] = {r: InputData(r, s) for r, s in tpl["inputs"].items()}
    missing = [{"role": r, "label": s.get("label", r), "reason": "필수 파일 미제출"}
               for r, s in tpl["inputs"].items() if s.get("required", True) and r not in ctx.files]
    book.result("F01", "필수 입력 파일 존재", missing, CRITICAL, "모든 필수 파일이 제출되었습니다.",
                "필수 파일 {n}개가 누락되었습니다.", method="템플릿 입력 명세와 제출 파일 비교")

    shas: dict[str, list[str]] = defaultdict(list)
    for r, f in ctx.files.items():
        shas[f["sha256"]].append(r)
    dup = [{"roles": rs, "sha256": s[:16], "reason": "같은 파일이 여러 역할로 투입됨"} for s, rs in shas.items() if len(rs) > 1]
    book.result("F02", "파일 중복 투입", dup, HIGH, "역할별 파일이 모두 서로 다릅니다.",
                "동일 파일(해시 일치)이 {n}건 중복 투입되었습니다.", method="SHA-256 비교")

    parse_fail, empty, unmapped, type_issues = [], [], [], []
    unit_fail, unit_info, review_items, drift_items = [], [], [], []
    row_missing, row_date, row_ccy, row_num, row_code = [], [], [], [], []

    for role, inp in inputs.items():
        f = ctx.files.get(role)
        if not f:
            continue
        inp.file = f
        try:
            parsed = parse_file(Path(f["stored_path"]), f["ext"], f["original_name"], ctx.max_rows)
        except ParseError as e:
            parse_fail.append({"role": role, "file": f["original_name"], "reason": str(e)})
            continue
        inp.parse_meta = parsed.metadata
        if not parsed.tables:
            empty.append({"role": role, "file": f["original_name"], "reason": "표/데이터 행 없음"})
            continue
        table, mapping = best_table(parsed.tables, inp.columns, ctx.overrides.get(role))
        assert table is not None and mapping is not None
        inp.table, inp.mapping = table, mapping
        if not table.rows:
            empty.append({"role": role, "file": f["original_name"], "table": table.name, "reason": "데이터 행 0건"})
            continue
        for fld in mapping["unmapped_required"]:
            unmapped.append({"role": role, "file": f["original_name"], "table": table.name, "column": fld,
                             "reason": f"필수 컬럼 '{inp.columns[fld].get('label', fld)}' 매핑 실패"})
        for fld, m in mapping["fields"].items():
            if m.get("error"):
                unmapped.append({"role": role, "file": f["original_name"], "column": fld, "reason": m["error"]})
        for ti in mapping["type_issues"]:
            type_issues.append({"role": role, "file": f["original_name"], **ti})
        # 단위
        detected = (table.meta.get("unit") or parsed.metadata.get("unit") or {})
        expected_unit = inp.spec.get("unit_label", "원")
        if detected.get("label") and detected["label"] != expected_unit:
            unit_fail.append({"role": role, "file": f["original_name"], "source_value": detected.get("evidence"),
                              "compared": expected_unit, "reason": f"파일 단위 '{detected['label']}' ≠ 명세 '{expected_unit}'"})
        elif not detected.get("label"):
            unit_info.append(role)
        # 형식 변경/유사 매핑
        inp.layout = layout_of(table, mapping, f["original_name"])
        inp.drift = detect_drift(inp.layout, ctx.prior_layouts.get(role))
        for d in inp.drift:
            drift_items.append({"role": role, "file": f["original_name"], **d})
        for fld in mapping["needs_confirmation"]:
            m = mapping["fields"][fld]
            drift_items.append({"role": role, "file": f["original_name"], "type": "FUZZY_MAPPING",
                                "detail": f"'{m['source']}' → {m['label']} (유사도 {m['confidence']})"})
        if table.meta.get("formula_cells_without_cached_value"):
            review_items.append({"role": role, "file": f["original_name"], "table": table.name,
                                 "reason": f"수식 캐시값 없는 셀 {table.meta['formula_cells_without_cached_value']}개"})
        if table.meta.get("review_status") == "EXTRACTED_UNVERIFIED":
            review_items.append({"role": role, "file": f["original_name"], "table": table.name,
                                 "reason": f"PDF 추출값(페이지 {table.meta.get('pages')}) — 원문 대조 필요"})
        if any(u["role"] == role for u in unmapped):
            continue
        # 행 정규화
        src_idx = {fld: (table.columns.index(m["source"]) if m.get("source") else None)
                   for fld, m in mapping["fields"].items()}
        for ri, (row, pos) in enumerate(zip(table.rows, table.source_rows)):
            rec: dict[str, Any] = {"_src": f"{f['original_name']} {pos}", "_row": ri, "_errors": []}
            for fld, cs in inp.columns.items():
                idx = src_idx.get(fld)
                raw = row[idx] if idx is not None and idx < len(row) else None
                val, err = CONVERTERS[cs.get("type", "text")](raw)
                rec[fld] = val
                where = {"role": role, "file": f["original_name"], "table": table.name, "source_row": pos,
                         "column": mapping["fields"][fld].get("source") or cs.get("label", fld),
                         "source_value": None if raw is None else str(raw)[:60]}
                if err:
                    rec["_errors"].append((fld, err))
                    t = cs.get("type", "text")
                    bucket = {"date": row_date, "currency": row_ccy}.get(t, row_num if t in ("decimal", "money") else None)
                    if bucket is not None:
                        bucket.append({**where, "reason": err})
                elif val is None and cs.get("required"):
                    rec["_errors"].append((fld, "필수값 누락"))
                    row_missing.append({**where, "reason": "필수값 누락"})
                if val is not None and cs.get("pattern") and not re.fullmatch(cs["pattern"], str(val)):
                    row_code.append({**where, "reason": f"형식 불일치(기대 패턴 {cs['pattern']})"})
            inp.records.append(rec)
        inp.usable = True

    book.result("F03", "파일 판독 및 필수 컬럼 매핑", parse_fail + unmapped, CRITICAL,
                "모든 파일을 판독했고 필수 컬럼이 매핑되었습니다.", "판독 실패 또는 필수 컬럼 미매핑 {n}건",
                method="동의어·유사도 기반 헤더 매핑 + 사용자 지정")
    book.result("F04", "빈 파일/데이터 없음", empty, CRITICAL, "모든 입력에 데이터 행이 있습니다.", "데이터가 없는 입력 {n}건")
    book.result("F06", "금액 단위 표기 확인", unit_fail, HIGH,
                "단위 표기가 명세와 일치합니다." + (f" (단위 표기 없음: {', '.join(unit_info)} — 명세 단위로 간주)" if unit_info else ""),
                "단위 불일치 {n}건 — 자동 환산하지 않았습니다.", method="'(단위: …)' 표기 탐지")
    if drift_items:
        book.add("F07", "형식 변경·유사 매핑 확인", REVIEW_REQUIRED, HIGH,
                 f"이전 승인 실행 대비 형식 변경 또는 확인 필요한 매핑 {len(drift_items)}건", details=drift_items,
                 method="이전 승인 실행의 입력 레이아웃과 비교")
    elif not ctx.prior_layouts:
        book.add("F07", "형식 변경·유사 매핑 확인", NOT_APPLICABLE, LOW,
                 "비교할 이전 승인 실행이 없습니다(최초 실행).", mandatory=False)
    else:
        book.add("F07", "형식 변경·유사 매핑 확인", PASS, HIGH, "이전 승인 실행과 입력 형식이 같습니다.")
    if review_items:
        book.add("F08", "수식 캐시·PDF 추출값 확인", REVIEW_REQUIRED, MEDIUM,
                 f"사람의 원문 대조가 필요한 입력 {len(review_items)}건", details=review_items, mandatory=False)
    else:
        book.add("F08", "수식 캐시·PDF 추출값 확인", PASS, MEDIUM, "수식 캐시 누락·PDF 추출값 없음", mandatory=False)
    book.result("D01", "필수값 누락", row_missing, HIGH, "필수값 누락 없음", "필수값 누락 {n}건")
    book.result("D03", "날짜 형식", row_date, HIGH, "날짜 형식 오류 없음", "날짜 형식 오류 {n}건")
    book.result("D04", "통화코드 유효성", row_ccy, HIGH, "통화코드 오류 없음", "통화코드 오류 {n}건")
    book.result("D05", "코드 형식", row_code, MEDIUM, "코드 형식 오류 없음", "코드 형식 불일치 {n}건")
    book.result("D06", "숫자 필드 문자 입력", row_num + [{**t, "reason": "타입 적합률 90% 미만"} for t in type_issues],
                HIGH, "숫자 필드 오류 없음", "숫자 변환 실패 {n}건")
    return inputs


def _dup_keys(inp: InputData) -> list[dict[str, Any]]:
    keyf = inp.spec.get("key", [])
    if not keyf or not inp.usable:
        return []
    seen: dict[tuple, list[str]] = defaultdict(list)
    for r in inp.records:
        k = _key(r, keyf)
        if k is not None:
            seen[k].append(r["_src"])
    return [{"role": inp.role, "key": _kstr(k), "rows": srcs, "reason": f"키 중복 {len(srcs)}행"}
            for k, srcs in seen.items() if len(srcs) > 1]


def _range_checks(inputs: dict[str, InputData]) -> tuple[list, list]:
    neg, rng = [], []
    for inp in inputs.values():
        if not inp.usable:
            continue
        for fld, cs in inp.columns.items():
            mn = cs.get("min")
            wr = cs.get("warn_range")
            for r in inp.records:
                v = r.get(fld)
                if not isinstance(v, Decimal):
                    continue
                base = {"role": inp.role, "source_row": r["_src"], "column": cs.get("label", fld), "source_value": str(v)}
                if mn is not None and v < Decimal(str(mn)):
                    neg.append({**base, "reason": f"최소값 {mn} 미만(음수 등)"})
                if wr and not (Decimal(str(wr[0])) <= v <= Decimal(str(wr[1]))):
                    rng.append({**base, "reason": f"정상범위 {wr[0]}~{wr[1]} 이탈"})
    return neg, rng


def _base_date_check(ctx: RunContext, inputs: dict[str, InputData], book: CheckBook) -> None:
    rules = ctx.template.get("base_date_rules", {})
    expected = ctx.base_date
    fails, warns = [], []
    if not periods.is_month_end(expected):
        warns.append({"reason": f"결산 기준일 {expected}이 월말이 아닙니다."})
    for role in rules.get("current_inputs", []):
        inp = inputs.get(role)
        if not inp or not inp.usable:
            continue
        fld = rules.get("field", "base_date")
        vals = {r.get(fld) for r in inp.records if r.get(fld) is not None}
        if vals and vals != {expected}:
            fails.append({"role": role, "source_value": ", ".join(sorted(map(str, vals)))[:120],
                          "compared": str(expected), "reason": "입력 기준일 ≠ 결산 기준일"})
        meta_bd = (inp.parse_meta.get("base_date") or {}).get("date")
        if meta_bd and meta_bd != expected.isoformat():
            warns.append({"role": role, "source_value": meta_bd, "compared": str(expected),
                          "reason": f"파일 표기 기준일({(inp.parse_meta.get('base_date') or {}).get('source')}) 불일치"})
    prior_role = rules.get("prior_input")
    if prior_role and inputs.get(prior_role) and inputs[prior_role].usable:
        exp_prior = periods.prev_month_end(expected)
        vals = {r.get("base_date") for r in inputs[prior_role].records if r.get("base_date") is not None}
        if vals and vals != {exp_prior}:
            fails.append({"role": prior_role, "source_value": ", ".join(sorted(map(str, vals)))[:120],
                          "compared": str(exp_prior), "reason": "전월 결과파일 기준일 ≠ 전월말"})
    period_rule = rules.get("entries_within_month")
    if period_rule:
        inp = inputs.get(period_rule["input"])
        if inp and inp.usable:
            start = date(expected.year, expected.month, 1)
            for r in inp.records:
                d = r.get(period_rule["field"])
                if d is not None and not (start <= d <= expected):
                    fails.append({"role": inp.role, "source_row": r["_src"], "source_value": str(d),
                                  "compared": f"{start}~{expected}", "reason": "결산월 밖의 일자"})
    if fails:
        book.add("F05", "기준일 일관성", FAIL, HIGH, f"기준일 불일치 {len(fails)}건", details=fails + warns,
                 method="입력 기준일 컬럼·파일 표기 기준일·결산 기준일 비교")
    elif warns:
        book.add("F05", "기준일 일관성", WARNING, MEDIUM, f"확인 필요 {len(warns)}건", details=warns)
    else:
        book.add("F05", "기준일 일관성", PASS, HIGH, f"모든 입력 기준일이 {expected}과 일치")


# --------------------------------------------------------------------------- 공통 후처리

def _rule_checks(tpl: Mapping[str, Any], book: CheckBook) -> list[CalcRule]:
    calcs = tpl.get("calculations", [])
    if not calcs:
        book.add("C05", "계산 규칙 테스트", NOT_APPLICABLE, LOW, "이 업무에는 계산 규칙이 없습니다.", mandatory=False)
        book.add("C06", "계산 규칙 승인 상태", NOT_APPLICABLE, LOW, "이 업무에는 계산 규칙이 없습니다.", mandatory=False)
        return []
    tests = run_rule_tests(calcs)
    bad = [r for r in tests["results"] if not r["ok"]]
    book.result("C05", "계산 규칙 테스트", bad, CRITICAL, f"규칙 테스트 {len(tests['results'])}건 통과",
                "규칙 테스트 실패 {n}건", method="템플릿에 등록된 test_cases 재실행")
    rules = [CalcRule.from_dict(d) for d in calcs] if not bad else []
    unapproved = [{"rule_id": d["rule_id"], "status": d.get("approval_status", "DRAFT"),
                   "basis": d.get("basis", ""), "reason": "회사 승인 전 규칙(예시/초안)"}
                  for d in calcs if d.get("approval_status") != "APPROVED"]
    if unapproved:
        book.add("C06", "계산 규칙 승인 상태", REVIEW_REQUIRED, HIGH,
                 f"승인되지 않은 규칙 {len(unapproved)}건 사용 — 결과는 예시 산식 기준입니다.", details=unapproved)
    else:
        book.add("C06", "계산 규칙 승인 상태", PASS, HIGH, "모든 규칙이 승인(APPROVED) 상태")
    return rules


def _variances(ctx: RunContext, current_items: dict[str, dict[str, Any]], book: CheckBook,
               file_base: dict[str, dict[str, Any]] | None, mandatory: bool) -> dict[str, Any]:
    tpl_mat = (ctx.template.get("variance") or {}).get("materiality") or {}
    mat = {**ctx.materiality, **tpl_mat}
    out: dict[str, Any] = {}
    done, missing = [], []
    if file_base is not None:
        out["PRIOR_FILE"] = {"label": periods.PERIOD_LABELS["PRIOR_FILE"],
                             "base_date": str(periods.prev_month_end(ctx.base_date)), "source": "전월 결과파일",
                             "result": compare(current_items, file_base, mat)}
        done.append("PRIOR_FILE")
    for code, target in periods.comparison_targets(ctx.base_date).items():
        h = ctx.history.get(code)
        if h:
            out[code] = {"label": periods.PERIOD_LABELS[code], "base_date": str(target),
                         "source": f"실행이력 {h['run_id']}", "result": compare(current_items, h["items"], mat)}
            done.append(code)
        else:
            out[code] = {"label": periods.PERIOD_LABELS[code], "base_date": str(target), "source": None,
                         "not_run_reason": f"{target} 기준 승인된 실행 이력 없음"}
            missing.append(f"{periods.PERIOD_LABELS[code]}({target})")
    if done:
        msg = f"비교 수행: {', '.join(periods.PERIOD_LABELS[c] for c in done)}"
        if missing:
            msg += f" / 미수행: {', '.join(missing)}"
        book.add("V01", "기간 비교 수행", PASS, MEDIUM, msg, mandatory=mandatory)
    else:
        book.not_run("V01", "기간 비교 수행", "비교할 전기 자료(파일·실행이력)가 없습니다.", MEDIUM, mandatory)
    anomalies = []
    count_flags = []
    for code, v in out.items():
        res = v.get("result")
        if not res:
            continue
        for r in res["rows"]:
            if r["anomaly"]:
                anomalies.append({"period": v["label"], "key": r["key"], "label": r["label"],
                                  "computed": r["current"], "compared": r["base"], "difference": r["delta"],
                                  "rate_status": r["rate_status"], "rate": r["rate"],
                                  "reason": "; ".join(r["flags"]), "cause_candidates": r["cause_candidates"]})
        if res["total"]["count_changed_amount_same"]:
            count_flags.append({"period": v["label"], "reason": "합계 금액은 같으나 건수가 다름"})
    book.result("V02", "이상 증감", anomalies, MEDIUM, "중요성 기준을 넘는 증감 없음",
                "검토 후보 증감 {n}건 (오류 단정 아님)", fail_status=WARNING, mandatory=False,
                method=f"절대금액≥{mat.get('abs_amount')}, 증감률≥{mat.get('pct')}, 구성비, 수량-금액 괴리")
    book.result("V03", "건수-금액 정합", count_flags, MEDIUM, "건수·금액 변화 정합", "확인 필요 {n}건",
                fail_status=WARNING, mandatory=False)
    trend = list(ctx.trend)
    trend.append({"base_date": str(ctx.base_date), "total": sum((i["amount"] for i in current_items.values()
                                                                  if i.get("amount") is not None), Decimal(0)),
                  "count": len(current_items), "run_id": ctx.run_id, "current": True})
    return {"periods": out, "trend": trend}


# --------------------------------------------------------------------------- valuation_recon

def _pipeline_valuation(ctx: RunContext, book: CheckBook, inputs: dict[str, InputData]) -> dict[str, Any]:
    tpl = ctx.template
    hold, prices = inputs["holdings"], inputs["prices"]
    prior = inputs.get("prior")
    join = tpl["join"]
    keys = join["keys"]
    rules = _rule_checks(tpl, book)
    _base_date_check(ctx, inputs, book)

    dups = []
    for inp in inputs.values():
        dups += _dup_keys(inp)
    if hold.usable and prices.usable:
        book.result("D02", "키 중복", dups, CRITICAL, "키 중복 없음", "키 중복 {n}건", method=f"키 {keys}")
    else:
        book.not_run("D02", "키 중복", "보유내역 또는 단가 파일을 사용할 수 없습니다.", CRITICAL)
    neg, rng = _range_checks(inputs)
    book.result("D07", "음수·최소값 위반", neg, HIGH, "음수 수량·단가 없음", "최소값 위반 {n}건")
    book.result("D08", "정상범위 이탈", rng, MEDIUM, "정상범위 이탈 없음", "정상범위 이탈 {n}건",
                fail_status=WARNING, mandatory=False)

    processed: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    recon: list[dict[str, Any]] = []
    if not (hold.usable and prices.usable and rules is not None):
        for cid, name in (("R01", "단가 미매칭"), ("D10", "결합 행 수 증가"), ("T01", "건수 대사"),
                          ("T02", "장부금액 합계 대사"), ("T03", "평가금액 독립 집계"), ("C01", "독립 재계산"),
                          ("C02", "역산 검증"), ("C03", "단위 오류 탐지(비율)"), ("C04", "반올림 영향"),
                          ("T04", "업로드 합계 대사"), ("A01", "차변·대변 일치")):
            book.not_run(cid, name, "선행 단계(파일 판독/매핑/규칙)가 실패해 수행하지 못했습니다.", CRITICAL)
        return {"processed": [], "exceptions": [], "reconciliation": [], "journal": [], "upload_rows": [],
                "items": {}, "variance": {"periods": {}, "trend": []}, "summary": {}}

    price_idx: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for p in prices.records:
        k = _key(p, keys)
        if k is not None:
            price_idx[k].append(p)
    naive_join = 0
    keyed_hold = 0
    unmatched = []
    rule_err_fields = set()
    for r in rules:
        rule_err_fields |= set(r.inputs)
    for h in hold.records:
        k = _key(h, keys)
        base_row = {"code": h.get("code"), "name": h.get("name"), "currency": h.get("currency"), "_src": h["_src"]}
        if k is None:
            exceptions.append({**base_row, "reason": "키(종목코드/통화) 누락 또는 오류", "errors": h["_errors"]})
            continue
        keyed_hold += 1
        matches = price_idx.get(k, [])
        naive_join += len(matches)
        if not matches:
            unmatched.append({"key": _kstr(k), "source_row": h["_src"], "reason": "외부 단가 없음"})
            exceptions.append({**base_row, "reason": "외부 단가 미매칭"})
            recon.append({"key": _kstr(k), "status": "HOLDING_ONLY", "holding_src": h["_src"], "price_src": None})
            continue
        if len(matches) > 1:
            exceptions.append({**base_row, "reason": f"외부 단가 복수 매칭({len(matches)}건) — 임의 선택하지 않음"})
            recon.append({"key": _kstr(k), "status": "MULTIPLE_PRICES", "holding_src": h["_src"],
                          "price_src": ", ".join(m["_src"] for m in matches)})
            continue
        p = matches[0]
        recon.append({"key": _kstr(k), "status": "MATCHED", "holding_src": h["_src"], "price_src": p["_src"]})
        env = {**{f: v for f, v in h.items() if not f.startswith("_")},
               **{f: v for f, v in p.items() if not f.startswith("_") and f not in keys and f != "base_date"}}
        env["price_base_date"] = p.get("base_date")
        bad_fields = [e for e in h["_errors"] + p["_errors"] if e[0] in rule_err_fields]
        if bad_fields:
            exceptions.append({**base_row, "reason": "계산 입력 오류: " + "; ".join(f"{a}:{b}" for a, b in bad_fields)})
            continue
        neg_inputs = [f for f in rule_err_fields if isinstance(env.get(f), Decimal) and env[f] < 0]
        if neg_inputs:
            exceptions.append({**base_row, "reason": f"음수 입력값({', '.join(sorted(neg_inputs))}) — 계산 제외"})
            continue
        try:
            calc_trace = []
            for rule in rules:
                raw, rounded = rule.evaluate(env, env.get("currency"))
                env[rule.target] = rounded
                env[f"_{rule.target}_unrounded"] = raw
                calc_trace.append(f"{rule.rule_id}v{rule.version}: {rule.expression} = {rounded}")
        except CalcError as e:
            exceptions.append({**base_row, "reason": f"계산 불가: {e}"})
            continue
        env["_src"] = h["_src"]
        env["_price_src"] = p["_src"]
        env["_trace"] = " | ".join(calc_trace)
        processed.append(env)

    book.result("R01", "보유종목 단가 매칭", unmatched, HIGH, "모든 보유종목에 외부 단가가 매칭되었습니다.",
                "단가 미매칭 보유종목 {n}건", method=f"키 {keys} 기준 left join")
    hold_keys = {_key(h, keys) for h in hold.records} - {None}
    price_only = [{"key": _kstr(k), "source_row": v[0]["_src"], "reason": "보유내역에 없는 단가"}
                  for k, v in price_idx.items() if k not in hold_keys]
    book.result("R02", "단가 파일에만 있는 종목", price_only, LOW, "단가 파일 종목이 모두 보유내역에 있습니다.",
                "보유내역에 없는 단가 {n}건(정보)", fail_status=WARNING, mandatory=False)
    explosion = [{"reason": f"결합 결과 {naive_join}행 > 보유 {keyed_hold}행", "computed": naive_join,
                  "compared": keyed_hold}] if naive_join > keyed_hold else []
    book.result("D10", "결합 행 수 증가(중복 결합)", explosion, CRITICAL, f"결합 행 수 정상({naive_join} ≤ {keyed_hold})",
                "중복 결합 위험 — 복수 매칭 건은 계산에서 제외됨", method="naive join 행 수 vs 보유 행 수")

    # ---- 전월 결과파일 대사
    file_base = None
    if prior is not None and prior.usable:
        pidx = {}
        for r in prior.records:
            k = _key(r, keys)
            if k is not None:
                pidx[k] = r
        file_base = {_kstr(k): {"amount": r.get("prev_eval_amount"), "quantity": None, "label": None}
                     for k, r in pidx.items()}
        if hold.mapping and hold.mapping["fields"].get("prev_eval_amount", {}).get("source"):
            mism = []
            for h in hold.records:
                k = _key(h, keys)
                if k is None or k not in pidx:
                    continue
                a, b = h.get("prev_eval_amount"), pidx[k].get("prev_eval_amount")
                if a is not None and b is not None and a != b:
                    mism.append({"key": _kstr(k), "source_row": h["_src"], "source_value": a, "compared": b,
                                 "difference": a - b, "reason": "보유내역 전월평가금액 ≠ 전월 결과파일"})
            book.result("R03", "전월 평가금액 대사(기초 잔액)", mism, MEDIUM, "보유내역의 전월 평가금액이 전월 결과와 일치",
                        "전월 평가금액 불일치 {n}건", method="보유내역.전월평가금액 vs 전월결과.전월평가금액")
        else:
            book.add("R03", "전월 평가금액 대사(기초 잔액)", NOT_APPLICABLE, MEDIUM,
                     "보유내역에 전월 평가금액 컬럼이 없습니다.", mandatory=False)
        new_items = [{"key": _kstr(k), "reason": "전월에 없던 종목(신규)"} for k in hold_keys if k not in pidx]
        gone = [{"key": _kstr(k), "reason": "당월 보유내역에 없음(소멸)"} for k in pidx if k not in hold_keys]
        book.result("R04", "신규·소멸 종목", new_items + gone, LOW, "전월 대비 종목 구성 동일",
                    "신규/소멸 {n}건(정보)", fail_status=WARNING, mandatory=False)
        pc, cc = len(prior.records), len(hold.records)
        th = Decimal(str((tpl.get("variance") or {}).get("row_change_pct", "0.3")))
        jump = [{"computed": cc, "compared": pc, "reason": f"건수 변동 {(cc - pc) / pc:+.1%}"}] \
            if pc and abs(Decimal(cc - pc) / pc) > th else []
        book.result("D09", "데이터 건수 급변", jump, MEDIUM, f"건수 변동 정상({pc}→{cc})", "건수 급변",
                    fail_status=WARNING, mandatory=False)
    else:
        book.not_run("R03", "전월 평가금액 대사(기초 잔액)", "전월 결과파일 없음", MEDIUM, mandatory=False)
        book.not_run("D09", "데이터 건수 급변", "전월 결과파일 없음", MEDIUM, mandatory=False)

    # ---- 합계·계산 검증
    tgt = rules[0].target if rules else None
    book.result("T01", "건수 대사", [] if len(hold.records) == len(processed) + len(exceptions) else
                [{"computed": len(processed) + len(exceptions), "compared": len(hold.records),
                  "reason": "원천 건수 ≠ 처리 + 예외"}], CRITICAL,
                f"원천 {len(hold.records)} = 처리 {len(processed)} + 예외 {len(exceptions)}", "건수 불일치")

    # 원천 합계는 파싱된 표에서 직접 다시 집계(레코드 생성 경로와 분리)
    src_sum: dict[str, Decimal] = defaultdict(Decimal)
    t = hold.table
    assert t is not None and hold.mapping is not None
    bi = t.columns.index(hold.mapping["fields"]["book_amount"]["source"])
    ci = t.columns.index(hold.mapping["fields"]["currency"]["source"])
    for row in t.rows:
        v, _ = to_decimal(row[bi])
        ccy, _ = CONVERTERS["currency"](row[ci])
        if v is not None:
            src_sum[str(ccy)] += v
    proc_sum: dict[str, Decimal] = defaultdict(Decimal)
    for r in processed:
        if r.get("book_amount") is not None:
            proc_sum[str(r["currency"])] += r["book_amount"]
    exc_src = {e["_src"] for e in exceptions}
    for h in hold.records:
        if h["_src"] in exc_src and h.get("book_amount") is not None:
            proc_sum[str(h.get("currency"))] += h["book_amount"]
    t2 = [{"currency": c, "computed": proc_sum.get(c, Decimal(0)), "compared": src_sum.get(c, Decimal(0)),
           "difference": proc_sum.get(c, Decimal(0)) - src_sum.get(c, Decimal(0)), "reason": "장부금액 합계 불일치"}
          for c in sorted(set(src_sum) | set(proc_sum)) if proc_sum.get(c, Decimal(0)) != src_sum.get(c, Decimal(0))]
    book.result("T02", "장부금액 합계 대사(통화별)", t2, CRITICAL,
                "원천 = 처리 + 예외 장부금액 합계 일치(통화별): " + ", ".join(f"{c} {v:,}" for c, v in sorted(src_sum.items())),
                "통화별 장부금액 합계 불일치 {n}건", method="원천 표 직접 집계 vs 처리·예외 레코드 합계")

    c01, c02, c03 = [], [], []
    t3_frac: dict[str, Fraction] = defaultdict(Fraction)
    t3_engine: dict[str, Decimal] = defaultdict(Decimal)
    rounded_sum: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    ver = tpl.get("verification", {})
    if rules:
        r0 = rules[0]
        for r in processed:
            ccy = r["currency"]
            env = {k: r[k] for k in r0.inputs}
            env.update(r0.params)
            exact = fraction_eval(r0.expression, env)
            d = r0.decimals_for(ccy)
            indep = fraction_round(exact, d, r0.rounding_mode)
            if frac_to_dec(indep) != r[r0.target]:
                c01.append({"key": f"{r['code']}|{ccy}", "source_row": r["_src"], "computed": r[r0.target],
                            "compared": frac_to_dec(indep), "formula": r0.expression, "reason": "독립 재계산 불일치"})
            t3_frac[ccy] += exact
            t3_engine[ccy] += r[f"_{r0.target}_unrounded"]
            rounded_sum[ccy] += r[r0.target]
            counts[ccy] += 1
            rev = ver.get("reverse")
            if rev:
                unit = Fraction(1, 10 ** d)
                renv = {**{k: v for k, v in r.items() if isinstance(v, Decimal)}, **r0.params, "unit": unit}
                try:
                    back = fraction_eval(rev["expression"], renv)
                    tol = fraction_eval(rev["tolerance_expression"], renv)
                    if abs(back - Fraction(str(r[rev["compare_to"]]))) > tol:
                        c02.append({"key": f"{r['code']}|{ccy}", "source_row": r["_src"], "computed": frac_to_dec(back),
                                    "compared": r[rev["compare_to"]], "formula": rev["expression"], "reason": "역산값이 허용오차 밖"})
                except ZeroDivisionError:
                    pass
            ratio = ver.get("ratio")
            if ratio:
                num, den = r.get(ratio["numerator"]), r.get(ratio["denominator"])
                if num is not None and den not in (None, Decimal(0)):
                    q = num / den
                    if not (Decimal(ratio["min"]) <= q <= Decimal(ratio["max"])):
                        c03.append({"key": f"{r['code']}|{ccy}", "source_row": r["_src"], "computed": num, "compared": den,
                                    "formula": f"{ratio['numerator']}/{ratio['denominator']} = {q:.4f}",
                                    "reason": f"비율 {ratio['min']}~{ratio['max']} 밖 — 단위(천원/원) 오류 또는 단가 오류 의심"})
        book.result("C01", "독립 재계산", c01, CRITICAL, f"{len(processed)}건 Fraction 독립 재계산 일치", "재계산 불일치 {n}건",
                    method="fractions.Fraction + 정수 반올림(별도 구현)")
        if ver.get("reverse"):
            book.result("C02", "역산 검증", c02, HIGH, "역산 단가가 모두 허용오차 내", "역산 불일치 {n}건",
                        method=ver["reverse"]["expression"])
        else:
            book.add("C02", "역산 검증", NOT_APPLICABLE, LOW, "템플릿에 역산 규칙 없음", mandatory=False)
        if ver.get("ratio"):
            book.result("C03", "단위 오류 탐지(비율)", c03, HIGH, "평가/장부 비율 정상", "비율 이상 {n}건",
                        method=f"{ver['ratio']['numerator']}/{ver['ratio']['denominator']} ∈ [{ver['ratio']['min']}, {ver['ratio']['max']}]")
        else:
            book.add("C03", "단위 오류 탐지(비율)", NOT_APPLICABLE, LOW, "템플릿에 비율 검증 없음", mandatory=False)
        t3 = []
        c04 = []
        for ccy in sorted(t3_frac):
            diff = abs(frac_to_dec(t3_frac[ccy]) - t3_engine[ccy])
            if diff > Decimal("1e-20"):
                t3.append({"currency": ccy, "computed": t3_engine[ccy], "compared": frac_to_dec(t3_frac[ccy]),
                           "difference": diff, "reason": "독립 집계 불일치"})
            d = r0.decimals_for(ccy)
            impact = rounded_sum[ccy] - frac_to_dec(t3_frac[ccy])
            limit = Decimal(counts[ccy]) * Decimal("0.5") * Decimal(1).scaleb(-d)
            if abs(impact) > limit:
                c04.append({"currency": ccy, "computed": impact, "compared": limit, "reason": "반올림 영향 한도 초과"})
        book.result("T03", "평가금액 독립 집계(통화별)", t3, CRITICAL, "행 계산 합계 = 통화별 독립 집계", "집계 불일치 {n}건",
                    method="Σ(Fraction 원식) vs Σ(엔진 반올림 전 값)")
        impacts = ", ".join(f"{c} {(rounded_sum[c] - frac_to_dec(t3_frac[c])):+.6f}" for c in sorted(t3_frac))
        book.result("C04", "반올림 영향", c04, MEDIUM, f"반올림 영향 한도 내 ({impacts})", "반올림 영향 초과 {n}건",
                    method="|Σ반올림 − Σ원값| ≤ 건수×0.5×최소단위")

    # ---- 분개 초안
    jcfg = tpl.get("journal") or {}
    journal_lines: list[dict[str, Any]] = []
    if jcfg.get("enabled"):
        journal_lines = jr.build_valuation_journal(processed, jcfg, str(ctx.base_date), ctx.run_id)
        bad = jr.balance_check(journal_lines)
        book.result("A01", "분개 초안 차변·대변 일치", bad, CRITICAL, f"전표 {len({l['voucher_no'] for l in journal_lines})}건 차대 일치",
                    "차대 불일치 전표 {n}건", method="전표·통화별 Σ차변 = Σ대변")
        fld = jcfg["amount_field"]
        a2 = []
        for ccy in sorted({r["currency"] for r in processed}):
            src = sum((abs(r[fld]) for r in processed if r["currency"] == ccy and r.get(fld)), Decimal(0))
            dr = sum((l["debit"] for l in journal_lines if l["currency"] == ccy), Decimal(0))
            if src != dr:
                a2.append({"currency": ccy, "computed": dr, "compared": src, "difference": dr - src,
                           "reason": "분개 합계 ≠ 평가손익 절대값 합계"})
        book.result("A02", "분개 합계 = 평가손익 합계", a2, HIGH, "분개 합계가 평가손익과 일치", "불일치 {n}건")
        if jcfg.get("policy_status") != "APPROVED":
            book.add("A03", "분개 회계정책 상태", REVIEW_REQUIRED, HIGH,
                     "분개 계정은 예시(가상 계정)입니다. 금융상품 분류·계정 매핑을 회사 정책으로 확인하세요.",
                     details=[{"reason": f"policy_status={jcfg.get('policy_status')}",
                               "accounts": [jcfg["positive"], jcfg["negative"]]}])
        else:
            book.add("A03", "분개 회계정책 상태", PASS, HIGH, "승인된 분개 정책")
    else:
        book.add("A01", "분개 초안 차변·대변 일치", NOT_APPLICABLE, LOW, "이 업무는 분개 초안을 만들지 않습니다.", mandatory=False)

    items = {f"{r['code']}|{r['currency']}": {"amount": r.get(tgt), "quantity": r.get("quantity"), "label": r.get("name")}
             for r in processed}
    variance = _variances(ctx, items, book, file_base, mandatory=True)

    up_cols = tpl.get("upload_columns") or ["base_date", "code", "name", "currency", "quantity", "price", "eval_amount",
                                            "book_amount", "valuation_gain"]
    upload_rows = []
    for r in processed:
        row = {c: r.get(c) for c in up_cols}
        row["base_date"] = str(ctx.base_date)
        row.update({"rule_versions": ",".join(f"{x.rule_id}v{x.version}" for x in rules), "run_id": ctx.run_id,
                    "source_row": r["_src"]})
        upload_rows.append(row)
    up_sum = defaultdict(Decimal)
    for u in upload_rows:
        up_sum[u["currency"]] += u.get(tgt) or Decimal(0)
    t4 = [{"currency": c, "computed": up_sum[c], "compared": rounded_sum.get(c, Decimal(0)), "reason": "업로드 합계 불일치"}
          for c in set(up_sum) | set(rounded_sum) if up_sum[c] != rounded_sum.get(c, Decimal(0))]
    book.result("T04", "업로드 대상 합계 대사", t4, CRITICAL, "업로드 대상 합계 = 처리 결과 합계", "불일치 {n}건",
                method="업로드 행 합계 vs 처리 행 합계 (Excel 기록 후 재판독 검증은 T05)")

    summary = {
        "source_count": len(hold.records), "processed_count": len(processed), "exception_count": len(exceptions),
        "unmatched_count": len(unmatched), "price_count": len(prices.records),
        "prior_count": len(prior.records) if prior and prior.usable else None,
        "totals_by_currency": {
            c: {"book_amount_source": src_sum.get(c, Decimal(0)), "eval_amount": rounded_sum.get(c, Decimal(0)),
                "valuation_gain": sum((r.get("valuation_gain") or Decimal(0) for r in processed if r["currency"] == c), Decimal(0)),
                "count": counts.get(c, 0)}
            for c in sorted(set(src_sum) | set(rounded_sum))},
    }
    return {"processed": processed, "exceptions": exceptions, "reconciliation": recon, "journal": journal_lines,
            "upload_rows": upload_rows, "items": items, "variance": variance, "summary": summary,
            "amount_field": tgt}


# --------------------------------------------------------------------------- generic_recon

def _pipeline_generic(ctx: RunContext, book: CheckBook, inputs: dict[str, InputData]) -> dict[str, Any]:
    tpl = ctx.template
    left, right = inputs["left"], inputs["right"]
    rc = tpl["recon"]
    keys = rc["keys"]
    amount_field = rc.get("amount_field")
    _rule_checks(tpl, book)
    _base_date_check(ctx, inputs, book)
    if not (left.usable and right.usable):
        for cid, name in (("D02", "키 중복"), ("R01", "좌측에만 있는 항목"), ("R02", "우측에만 있는 항목"),
                          ("R05", "필드 값 차이"), ("T01", "건수 대사"), ("T02", "합계 대사")):
            book.not_run(cid, name, "선행 단계(파일 판독/매핑)가 실패해 수행하지 못했습니다.", CRITICAL)
        return {"processed": [], "exceptions": [], "reconciliation": [], "journal": [], "upload_rows": [],
                "items": {}, "variance": {"periods": {}, "trend": []}, "summary": {}}
    book.result("D02", "키 중복", _dup_keys(left) + _dup_keys(right), CRITICAL, "키 중복 없음", "키 중복 {n}건")
    neg, rng = _range_checks(inputs)
    book.result("D07", "음수·최소값 위반", neg, HIGH, "최소값 위반 없음", "최소값 위반 {n}건")
    book.result("D08", "정상범위 이탈", rng, MEDIUM, "정상범위 이탈 없음", "정상범위 이탈 {n}건", fail_status=WARNING, mandatory=False)
    li = {}
    for r in left.records:
        k = _key(r, keys)
        if k is not None:
            li.setdefault(k, r)
    ri = {}
    for r in right.records:
        k = _key(r, keys)
        if k is not None:
            ri.setdefault(k, r)
    rows, l_only, r_only, diffs, exceptions = [], [], [], [], []
    for k in sorted(set(li) | set(ri), key=str):
        a, b = li.get(k), ri.get(k)
        row: dict[str, Any] = {"key": _kstr(k), "left_src": a and a["_src"], "right_src": b and b["_src"]}
        if a is None:
            row["status"] = "RIGHT_ONLY"
            r_only.append({"key": _kstr(k), "source_row": b["_src"], "reason": f"{right.spec.get('label', '우측')}에만 존재"})
        elif b is None:
            row["status"] = "LEFT_ONLY"
            l_only.append({"key": _kstr(k), "source_row": a["_src"], "reason": f"{left.spec.get('label', '좌측')}에만 존재"})
        else:
            row["status"] = "MATCHED"
            for cmpf in rc.get("compare", []):
                f = cmpf["field"]
                tol = Decimal(str(cmpf.get("tolerance", "0")))
                va, vb = a.get(f), b.get(f)
                row[f"left_{f}"], row[f"right_{f}"] = va, vb
                if isinstance(va, Decimal) and isinstance(vb, Decimal):
                    row[f"diff_{f}"] = va - vb
                    if abs(va - vb) > tol:
                        row["status"] = "DIFFERENT"
                        diffs.append({"key": _kstr(k), "column": f, "source_value": va, "compared": vb,
                                      "difference": va - vb, "source_row": a["_src"], "reason": f"차이 > 허용오차 {tol}"})
                elif va != vb:
                    row["status"] = "DIFFERENT"
                    diffs.append({"key": _kstr(k), "column": f, "source_value": va, "compared": vb,
                                  "source_row": a["_src"], "reason": "값 불일치"})
        for f in rc.get("carry", []):
            row[f] = (a or b or {}).get(f)
        rows.append(row)
    for inp in (left, right):
        for r in inp.records:
            if _key(r, keys) is None:
                exceptions.append({"role": inp.role, "_src": r["_src"], "reason": "키 누락/오류"})
    book.result("R01", "좌측에만 있는 항목", l_only, HIGH, "좌측 항목이 모두 매칭", "좌측 단독 {n}건")
    book.result("R02", "우측에만 있는 항목", r_only, HIGH, "우측 항목이 모두 매칭", "우측 단독 {n}건")
    book.result("R05", "필드 값 차이", diffs, HIGH, "매칭 항목의 비교 필드가 모두 일치", "값 차이 {n}건")
    lk = sum(1 for r in left.records if _key(r, keys) is not None)
    matched_left = sum(1 for r in rows if r["status"] in ("MATCHED", "DIFFERENT", "LEFT_ONLY"))
    book.result("T01", "건수 대사", [] if lk == matched_left or _dup_keys(left) else
                [{"computed": matched_left, "compared": lk, "reason": "좌측 건수 불일치"}], CRITICAL,
                f"좌측 {lk}건 = 결과 반영 {matched_left}건", "건수 불일치")
    t2 = []
    if amount_field:
        for side, idx, inp in (("left", li, left), ("right", ri, right)):
            s_src = sum((r.get(amount_field) or Decimal(0) for r in inp.records if _key(r, keys) is not None), Decimal(0))
            s_idx = sum((r.get(amount_field) or Decimal(0) for r in idx.values()), Decimal(0))
            if s_src != s_idx:
                t2.append({"side": side, "computed": s_idx, "compared": s_src, "reason": "합계 불일치(중복키 영향 가능)"})
        book.result("T02", "합계 대사", t2, CRITICAL, "양측 합계가 결과에 모두 반영됨", "합계 불일치 {n}건")
    items = {_kstr(k): {"amount": r.get(amount_field) if amount_field else None, "quantity": None,
                        "label": r.get(rc.get("label_field", ""))} for k, r in li.items()}
    variance = _variances(ctx, items, book, None, mandatory=bool((tpl.get("variance") or {}).get("mandatory", False)))
    upload_rows = [{**r, "base_date": str(ctx.base_date), "run_id": ctx.run_id} for r in rows]
    summary = {"left_count": len(left.records), "right_count": len(right.records),
               "matched": sum(1 for r in rows if r["status"] == "MATCHED"),
               "different": sum(1 for r in rows if r["status"] == "DIFFERENT"),
               "left_only": len(l_only), "right_only": len(r_only),
               "source_count": len(left.records), "processed_count": len(rows), "exception_count": len(exceptions)}
    return {"processed": rows, "exceptions": exceptions, "reconciliation": rows, "journal": [], "upload_rows": upload_rows,
            "items": items, "variance": variance, "summary": summary, "amount_field": amount_field}


# --------------------------------------------------------------------------- journal_check

def _pipeline_journal(ctx: RunContext, book: CheckBook, inputs: dict[str, InputData]) -> dict[str, Any]:
    tpl = ctx.template
    jn, coa = inputs["journal"], inputs.get("coa")
    _rule_checks(tpl, book)
    _base_date_check(ctx, inputs, book)
    if not jn.usable:
        for cid, name in (("A01", "전표별 차변·대변 일치"), ("T01", "건수 대사"), ("T02", "차변 합계 = 대변 합계")):
            book.not_run(cid, name, "전표 파일을 사용할 수 없습니다.", CRITICAL)
        return {"processed": [], "exceptions": [], "reconciliation": [], "journal": [], "upload_rows": [],
                "items": {}, "variance": {"periods": {}, "trend": []}, "summary": {}}
    neg, rng = _range_checks(inputs)
    book.result("D07", "음수 금액", neg, HIGH, "음수 금액 없음", "음수 금액 {n}건")
    lines, exceptions, j01 = [], [], []
    for r in jn.records:
        dr, cr = r.get("debit") or Decimal(0), r.get("credit") or Decimal(0)
        if (dr != 0) == (cr != 0):
            j01.append({"source_row": r["_src"], "source_value": f"차변 {dr} / 대변 {cr}",
                        "reason": "한 줄에 차변·대변이 모두 있거나 모두 0"})
        line = {k: v for k, v in r.items() if not k.startswith("_")}
        line.update({"debit": dr, "credit": cr, "source_row": r["_src"]})
        if r["_errors"]:
            exceptions.append({**line, "reason": "; ".join(f"{a}:{b}" for a, b in r["_errors"])})
        lines.append(line)
    book.result("J01", "라인 차대 구분", j01, MEDIUM, "모든 라인이 차변 또는 대변 한쪽만 가짐", "라인 오류 {n}건")
    bad = jr.balance_check(lines)
    book.result("A01", "전표별 차변·대변 일치", bad, CRITICAL, f"전표 {len({l.get('voucher_no') for l in lines})}건 차대 일치",
                "차대 불일치 전표 {n}건", method="전표번호·통화별 Σ차변 = Σ대변")
    tdr = sum((l["debit"] for l in lines), Decimal(0))
    tcr = sum((l["credit"] for l in lines), Decimal(0))
    book.result("T02", "차변 합계 = 대변 합계", [] if tdr == tcr else
                [{"computed": tdr, "compared": tcr, "difference": tdr - tcr, "reason": "전체 차대 불일치"}],
                CRITICAL, f"전체 차변 {tdr:,} = 대변 {tcr:,}", "전체 차대 불일치")
    book.result("T01", "건수 대사", [] if len(lines) == len(jn.records) else [{"reason": "라인 수 불일치"}],
                CRITICAL, f"라인 {len(lines)}건 처리", "건수 불일치")
    if coa is not None and coa.usable:
        cmap = {r.get("account_code"): r for r in coa.records if r.get("account_code")}
        missing = [{"source_row": l["source_row"], "source_value": l.get("account_code"), "reason": "계정과목표에 없는 계정"}
                   for l in lines if l.get("account_code") not in cmap]
        book.result("A04", "계정코드 유효성", missing, HIGH, "모든 계정코드가 계정과목표에 있음", "미등록 계정 {n}건")
        nm = [{"source_row": l["source_row"], "source_value": l.get("account_name"),
               "compared": cmap[l["account_code"]].get("account_name"), "reason": "계정명 불일치"}
              for l in lines if l.get("account_code") in cmap and l.get("account_name")
              and cmap[l["account_code"]].get("account_name") and l["account_name"] != cmap[l["account_code"]]["account_name"]]
        book.result("A05", "계정명 일치", nm, LOW, "계정명 일치", "계정명 불일치 {n}건", fail_status=WARNING, mandatory=False)
    else:
        book.not_run("A04", "계정코드 유효성", "계정과목표 파일이 제출되지 않았습니다.", HIGH, mandatory=False)
    by_acct: dict[str, dict[str, Any]] = {}
    for l in lines:
        a = by_acct.setdefault(l.get("account_code") or "?", {"amount": Decimal(0), "quantity": None, "label": l.get("account_name")})
        a["amount"] += l["debit"] - l["credit"]
    variance = _variances(ctx, by_acct, book, None, mandatory=False)
    summary = {"source_count": len(jn.records), "processed_count": len(lines), "exception_count": len(exceptions),
               "voucher_count": len({l.get("voucher_no") for l in lines}), "total_debit": tdr, "total_credit": tcr}
    return {"processed": lines, "exceptions": exceptions, "reconciliation": [], "journal": lines, "upload_rows": lines,
            "items": by_acct, "variance": variance, "summary": summary, "amount_field": "amount"}


PIPELINES = {"valuation_recon": _pipeline_valuation, "generic_recon": _pipeline_generic, "journal_check": _pipeline_journal}


def execute(ctx: RunContext) -> dict[str, Any]:
    errs = validate_template(ctx.template)
    if errs:
        raise TemplateError("; ".join(errs))
    book = CheckBook(ctx.template.get("validation_overrides"))
    inputs = load_inputs(ctx, book)
    out = PIPELINES[ctx.template["workflow_type"]](ctx, book, inputs)
    out["checks"] = book.list()
    out["inputs"] = {
        r: {"label": i.spec.get("label", r), "file_id": i.file and i.file["id"], "file": i.file and i.file["original_name"],
            "sha256": i.file and i.file["sha256"], "table": i.table and i.table.name,
            "rows": len(i.records), "mapping": i.mapping, "layout": i.layout, "drift": i.drift,
            "base_date_detected": (i.parse_meta.get("base_date") or {}).get("date") if i.parse_meta else None}
        for r, i in inputs.items()}
    out["source_data"] = {r: [{k: v for k, v in rec.items() if k not in ("_errors",)} for rec in i.records]
                          for r, i in inputs.items()}
    out["rule_versions"] = [{"rule_id": d["rule_id"], "version": d.get("version", 1),
                             "approval_status": d.get("approval_status")} for d in ctx.template.get("calculations", [])]
    return out
