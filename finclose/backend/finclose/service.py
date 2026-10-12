"""업무 오케스트레이션: 분석 → 계획 → 실행 → 검증 → 보고 → 승인 → 확정. DB·파일 저장을 담당한다."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from . import approval, audit, discovery, intake, periods
from . import templates as treg
from .config import Settings
from .db import Database, dumps, loads, now_iso
from .engine import RunContext, TemplateError, execute
from .parsers import ParseError, parse_file
from .report import build_html, build_workbook, read_back_totals, write_upload_files
from .rules import CalcRule
from .schema_mapper import best_table, detect_drift, layout_of
from .validation import summarize

ACCEPTED = ("APPROVED", "FINALIZED")
DEFAULT_MATERIALITY = {"abs_amount": "100000000", "pct": "0.1", "share_pp": "0.05", "qty_pct": "0.1"}


class ServiceError(Exception):
    def __init__(self, message: str, status: int = 400, payload: dict[str, Any] | None = None):
        super().__init__(message)
        self.status = status
        self.payload = payload or {}


# ---- 타입 보존 JSON (Decimal/date 복원 가능)

def enc(o: Any) -> Any:
    if isinstance(o, Decimal):
        return {"$d": str(o)}
    if isinstance(o, date):
        return {"$date": o.isoformat()}
    if isinstance(o, dict):
        return {str(k): enc(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [enc(v) for v in o]
    return o


def dec(o: Any) -> Any:
    if isinstance(o, dict):
        if set(o) == {"$d"}:
            return Decimal(o["$d"])
        if set(o) == {"$date"}:
            return date.fromisoformat(o["$date"])
        return {k: dec(v) for k, v in o.items()}
    if isinstance(o, list):
        return [dec(v) for v in o]
    return o


def to_api(o: Any) -> Any:
    if isinstance(o, Decimal):
        return format(o, "f")
    if isinstance(o, date):
        return o.isoformat()
    if isinstance(o, dict):
        return {str(k): to_api(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [to_api(v) for v in o]
    return o


def result_hash(result: dict[str, Any]) -> str:
    core = {"processed": [{k: v for k, v in r.items() if k not in ("_src", "_price_src")} for r in result["processed"]],
            "upload": [{k: v for k, v in r.items() if k not in ("run_id", "source_row")} for r in result["upload_rows"]],
            "checks": [(c["check_id"], c["status"], len(c["details"])) for c in result["checks"]]}
    return hashlib.sha256(json.dumps(to_api(core), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Service:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.ensure_dirs()
        self.db = Database(settings.db_path)
        treg.seed_builtin(self.db)
        self.recover()

    # ------------------------------------------------------------------ 복구
    def recover(self) -> None:
        stuck = self.db.query("SELECT id FROM runs WHERE status='RUNNING'")
        for r in stuck:
            self.db.execute("UPDATE runs SET status='FAILED', error=?, finished_at=? WHERE id=?",
                            ("비정상 종료(처리 중 서버 중단) — 결과 미생성, 원본 영향 없음", now_iso(), r["id"]))
            audit.record(self.db, "system", "admin", "RUN_RECOVERED_AS_FAILED", "run", r["id"], {})
        for p in self.settings.runs_dir.glob("*.tmp"):
            shutil.rmtree(p, ignore_errors=True)
        for p in self.settings.upload_dir.glob("*.part"):
            p.unlink(missing_ok=True)

    # ------------------------------------------------------------------ 설정
    def materiality(self) -> dict[str, Any]:
        r = self.db.one("SELECT value_json FROM settings WHERE key='materiality'")
        return {**DEFAULT_MATERIALITY, **(loads(r["value_json"]) if r else {})}

    def set_materiality(self, value: dict[str, Any], actor: str, role: str) -> dict[str, Any]:
        clean = {}
        for k in DEFAULT_MATERIALITY:
            if k in value:
                d = Decimal(str(value[k]))
                if d < 0:
                    raise ServiceError(f"{k}는 0 이상이어야 합니다.")
                clean[k] = str(d)
        before = self.materiality()
        self.db.execute("INSERT INTO settings(key, value_json, updated_at, updated_by) VALUES('materiality',?,?,?)"
                        " ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at,"
                        " updated_by=excluded.updated_by", (dumps({**before, **clean}), now_iso(), actor))
        audit.record(self.db, actor, role, "SETTINGS_CHANGED", "settings", "materiality", {"before": before, "after": clean})
        return self.materiality()

    # ------------------------------------------------------------------ 파일
    def files(self, ids: list[str]) -> list[dict[str, Any]]:
        out = []
        for i in ids:
            f = intake.get_file(self.db, i)
            if not f:
                raise ServiceError(f"파일 없음: {i}", 404)
            out.append(f)
        return out

    # ------------------------------------------------------------------ 이력
    def _accepted_run(self, key: str, base_date: date) -> dict[str, Any] | None:
        return self.db.one(
            "SELECT * FROM runs WHERE template_key=? AND base_date=? AND status IN ('APPROVED','FINALIZED')"
            " ORDER BY (status='FINALIZED') DESC, finished_at DESC LIMIT 1", (key, base_date.isoformat()))

    def _load_result(self, run_id: str) -> dict[str, Any]:
        p = self.settings.runs_dir / run_id / "result.json"
        if not p.exists():
            raise ServiceError("실행 결과 파일이 없습니다.", 404)
        return dec(json.loads(p.read_text(encoding="utf-8")))

    def _history(self, key: str, base_date: date) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        hist = {}
        for code, target in periods.comparison_targets(base_date).items():
            r = self._accepted_run(key, target)
            if r:
                hist[code] = {"run_id": r["id"], "base_date": target.isoformat(), "items": self._load_result(r["id"])["items"]}
        trend = []
        for d in periods.last_n_month_ends(base_date, 12)[:-1]:
            r = self._accepted_run(key, d)
            if r:
                items = self._load_result(r["id"])["items"]
                trend.append({"base_date": d.isoformat(), "run_id": r["id"], "count": len(items),
                              "total": sum((i["amount"] for i in items.values() if i.get("amount") is not None), Decimal(0))})
        return hist, trend

    def _prior_layouts(self, key: str, base_date: date) -> dict[str, Any]:
        r = self.db.one("SELECT id FROM runs WHERE template_key=? AND base_date<? AND status IN ('APPROVED','FINALIZED')"
                        " ORDER BY base_date DESC, finished_at DESC LIMIT 1", (key, base_date.isoformat()))
        if not r:
            return {}
        res = self._load_result(r["id"])
        return {role: i["layout"] for role, i in res["inputs"].items() if i.get("layout")}

    # ------------------------------------------------------------------ 분석·계획
    def analyze(self, file_ids: list[str]) -> dict[str, Any]:
        files = self.files(file_ids)
        active = [t for t in treg.list_templates(self.db) if t["status"] == "ACTIVE"]
        matches = discovery.match_templates(files, active)
        out: dict[str, Any] = {"files": [self._file_brief(f) for f in files], "candidates": matches}
        best = next((m for m in matches if m["is_candidate"]), None)
        if best:
            out["plan"] = self.plan(best["template_key"], best["version"],
                                    {r: a["file_id"] for r, a in best["assignments"].items()}, None, {})
        else:
            out["new_workflow"] = discovery.draft_new_workflow(files, self.settings.max_rows)
        return out

    def _file_brief(self, f: dict[str, Any]) -> dict[str, Any]:
        m = f.get("metadata") or {}
        return {"id": f["id"], "name": f["original_name"], "ext": f["ext"], "size": f["size"], "sha256": f["sha256"],
                "status": f["status"], "error": f["error"], "uploaded_at": f["uploaded_at"],
                "base_date": (m.get("metadata", {}).get("base_date") or {}).get("date"),
                "sheets": [s["name"] for s in m.get("metadata", {}).get("sheets", [])],
                "tables": [{"name": t["name"], "rows": t["row_count"], "columns": t["columns"]} for t in m.get("tables", [])],
                "warnings": m.get("warnings", [])}

    def plan(self, key: str, version: int | None, assignment: dict[str, str], base_date: str | None,
             overrides: dict[str, dict[str, str]]) -> dict[str, Any]:
        t = treg.get(self.db, key, version)
        if not t:
            raise ServiceError("활성 템플릿이 없습니다.", 404)
        body = t["body"]
        roles: dict[str, Any] = {}
        detected_dates = []
        uncertainties: list[str] = []
        for role, spec in body["inputs"].items():
            fid = assignment.get(role)
            if not fid:
                roles[role] = {"label": spec.get("label", role), "file_id": None, "required": spec.get("required", True)}
                if spec.get("required", True):
                    uncertainties.append(f"필수 입력 '{spec.get('label', role)}' 파일이 지정되지 않았습니다.")
                continue
            f = self.files([fid])[0]
            entry: dict[str, Any] = {"label": spec.get("label", role), "file_id": fid, "file": f["original_name"],
                                     "required": spec.get("required", True)}
            try:
                pf = parse_file(Path(f["stored_path"]), f["ext"], f["original_name"], self.settings.max_rows)
                table, mapping = best_table(pf.tables, spec["columns"], overrides.get(role))
                if table is None or mapping is None:
                    entry["error"] = "표를 찾지 못했습니다."
                else:
                    entry.update({"table": table.name, "rows": len(table.rows), "columns": table.columns, "mapping": mapping,
                                  "unit": table.meta.get("unit"), "base_date": (pf.metadata.get("base_date") or {}).get("date")})
                    if entry["base_date"] and role in body.get("base_date_rules", {}).get("current_inputs", []):
                        detected_dates.append(entry["base_date"])
                    for fld in mapping["needs_confirmation"]:
                        uncertainties.append(f"{spec.get('label', role)}: '{mapping['fields'][fld]['source']}' → "
                                             f"{mapping['fields'][fld]['label']} 유사도 매핑 확인 필요")
                    for fld in mapping["unmapped_required"]:
                        uncertainties.append(f"{spec.get('label', role)}: 필수 컬럼 '{spec['columns'][fld].get('label', fld)}'를 찾지 못함")
                    entry["layout"] = layout_of(table, mapping, f["original_name"])
            except ParseError as e:
                entry["error"] = str(e)
            roles[role] = entry
        bd = base_date or (sorted(detected_dates)[-1] if detected_dates else None)
        drift: dict[str, list] = {}
        if bd:
            prior = self._prior_layouts(key, date.fromisoformat(bd))
            for role, e in roles.items():
                if e.get("layout"):
                    d = detect_drift(e["layout"], prior.get(role))
                    if d:
                        drift[role] = d
                        uncertainties.append(f"{e['label']}: 이전 승인 실행 대비 형식 변경 {len(d)}건")
        else:
            uncertainties.append("결산 기준일을 파일에서 찾지 못했습니다. 직접 입력하세요.")
        for c in body.get("calculations", []):
            if c.get("approval_status") != "APPROVED":
                uncertainties.append(f"계산 규칙 {c['rule_id']}는 '{c.get('approval_status')}' 상태(회사 미승인) — 결과는 검토용")
        steps = ["원본 파일 해시 재확인", "시트/표 판독 및 컬럼 매핑", "값 정규화(금액 Decimal, 날짜, 통화, 코드)", "기준일 일관성 확인",
                 "필수값·키 중복·범위 검증"]
        if body["workflow_type"] == "valuation_recon":
            steps += [f"결합: {body['join']['left']} × {body['join']['right']} (키 {body['join']['keys']})"]
            steps += [f"계산 {c['rule_id']}: {c['target']} = {c['expression']} {c.get('params') or ''}" for c in body.get("calculations", [])]
            steps += ["독립 재계산(Fraction)·역산·비율·반올림 검증", "합계·건수 대사", "전월 결과 대사", "분개 초안(예시) 차대 검증"]
        elif body["workflow_type"] == "generic_recon":
            steps += [f"대사: 키 {body['recon']['keys']}, 비교 {[c['field'] for c in body['recon']['compare']]}"]
        else:
            steps += ["라인 차대 구분", "전표별 차변=대변", "계정코드 유효성"]
        steps += ["기간 비교(전월·전분기·전년동기·전기말·12개월)", "검토 보고서·Excel 생성", "검토·승인 후 업로드 파일 생성"]
        return {"template_key": key, "version": t["version"], "name": t["name"], "workflow_type": body["workflow_type"],
                "description": body.get("description"), "base_date": bd, "roles": roles, "drift": drift,
                "steps": steps, "uncertainties": uncertainties, "confirm_items": body.get("confirm_items", []),
                "outputs": body.get("output_sheets", []),
                "rules": [{k: c.get(k) for k in ("rule_id", "name", "expression", "params", "approval_status", "basis", "version")}
                          for c in body.get("calculations", [])],
                "needs_confirmation": bool(drift) or any(e.get("mapping", {}).get("needs_confirmation") for e in roles.values())}

    # ------------------------------------------------------------------ 실행
    def create_run(self, key: str, version: int | None, base_date: str, files: dict[str, str],
                   overrides: dict[str, dict[str, str]], actor: str, role: str, confirm_changes: bool = False,
                   confirm_reason: str = "", rerun_reason: str = "") -> dict[str, Any]:
        t = treg.get(self.db, key, version)
        if not t:
            raise ServiceError("템플릿(활성 또는 지정 버전)이 없습니다.", 404)
        if t["status"] not in ("ACTIVE",) and version is None:
            raise ServiceError("활성 템플릿만 실행할 수 있습니다.")
        if t["status"] == "INACTIVE":
            raise ServiceError("비활성화된 템플릿 버전입니다.")
        try:
            bd = date.fromisoformat(base_date)
        except (TypeError, ValueError) as e:
            raise ServiceError("결산 기준일 형식이 올바르지 않습니다(YYYY-MM-DD).") from e
        unknown = set(files) - set(t["body"]["inputs"])
        if unknown:
            raise ServiceError(f"템플릿에 없는 입력 역할: {sorted(unknown)}")
        frecs = {r: self.files([fid])[0] for r, fid in files.items()}
        for r, f in frecs.items():
            if f["status"] != "PARSED":
                raise ServiceError(f"'{f['original_name']}'은 판독 오류 상태입니다: {f['error']}")
            if not intake.file_sha_ok(f):
                raise ServiceError(f"원본 파일 '{f['original_name']}'의 해시가 업로드 시점과 다릅니다(변조 의심).", 409)
        pl = self.plan(key, t["version"], files, base_date, overrides)
        if pl["needs_confirmation"]:
            if not confirm_changes or len(confirm_reason.strip()) < 2:
                raise ServiceError("형식 변경 또는 유사도 매핑이 있어 자동 처리를 중단했습니다. 변경 내용을 확인하고 사유와 함께 승인하세요.",
                                   409, {"drift": pl["drift"], "uncertainties": pl["uncertainties"], "code": "NEEDS_CONFIRMATION"})
        fp_src = {"t": key, "v": t["version"], "d": base_date, "f": sorted((r, f["sha256"]) for r, f in frecs.items()),
                  "o": overrides}
        fingerprint = hashlib.sha256(dumps(fp_src).encode()).hexdigest()
        dup = self.db.query("SELECT id, status FROM runs WHERE fingerprint=? AND status NOT IN ('FAILED','REJECTED')", (fingerprint,))
        if dup and len(rerun_reason.strip()) < 2:
            raise ServiceError("동일 입력·동일 규칙으로 실행한 이력이 있습니다(중복 실행). 재실행하려면 사유를 입력하세요.",
                               409, {"code": "DUPLICATE_RUN", "runs": dup})
        run_id = f"R{bd.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
        now = now_iso()
        self.db.execute(
            "INSERT INTO runs(id, template_key, template_version, base_date, status, created_at, created_by, input_files_json,"
            " mapping_overrides_json, fingerprint, rerun_reason) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, key, t["version"], base_date, "RUNNING", now, actor,
             dumps({r: {"file_id": f["id"], "name": f["original_name"], "sha256": f["sha256"]} for r, f in frecs.items()}),
             dumps(overrides), fingerprint, rerun_reason or None))
        audit.record(self.db, actor, role, "RUN_STARTED", "run", run_id,
                     {"template": f"{key}v{t['version']}", "base_date": base_date,
                      "files": {r: f["sha256"] for r, f in frecs.items()}, "overrides": overrides,
                      "confirmed_changes": pl["drift"] if confirm_changes else None, "confirm_reason": confirm_reason or None,
                      "rerun_reason": rerun_reason or None})
        tmp = self.settings.runs_dir / f"{run_id}.tmp"
        try:
            hist, trend = self._history(key, bd)
            ctx = RunContext(run_id=run_id, template=t["body"], base_date=bd, files=frecs, overrides=overrides,
                             prior_layouts=self._prior_layouts(key, bd), history=hist, trend=trend,
                             materiality=self.materiality(), max_rows=self.settings.max_rows)
            result = execute(ctx)
            result["confirm_items"] = t["body"].get("confirm_items", [])
            result["output_sheets"] = t["body"].get("output_sheets", [])
            result["upload_columns_all"] = self._upload_columns(t["body"], result)
            result["confirmed_changes"] = {"by": actor, "reason": confirm_reason, "drift": pl["drift"]} if confirm_changes else None
            rhash = result_hash(result)
            other = self._other_finalized(key, base_date, run_id)
            pseudo = {"status": "RUNNING", "created_by": actor}
            g = approval.gate(pseudo, result["checks"], [], other)
            status = g["status_after_checks"]
            run_row = {**self._run_row_basic(run_id), "status": status, "result_hash": rhash, "template_name": t["name"]}
            tmp.mkdir(parents=True)
            (tmp / "result.json").write_text(json.dumps(enc(result), ensure_ascii=False), encoding="utf-8")
            build_workbook(tmp / "review.xlsx", run_row, result, g, [], self._audit_rows(run_id), final=False)
            (tmp / "report.html").write_text(build_html(run_row, result, g, []), encoding="utf-8")
            os.replace(tmp, self.settings.runs_dir / run_id)
            self.db.execute("UPDATE runs SET status=?, finished_at=?, summary_json=?, checks_json=?, gate_json=?, result_hash=?"
                            " WHERE id=?", (status, now_iso(), dumps(to_api(result["summary"])),
                                            dumps(to_api([{k: v for k, v in c.items() if k != "details"} for c in result["checks"]])),
                                            dumps(g), rhash, run_id))
            audit.record(self.db, actor, role, "RUN_COMPLETED", "run", run_id,
                         {"status": status, "result_hash": rhash, "checks": summarize(result["checks"])["by_status"]})
        except (TemplateError, ServiceError, ParseError, OSError, ValueError, ArithmeticError, KeyError) as e:
            shutil.rmtree(tmp, ignore_errors=True)
            msg = f"{type(e).__name__}: {e}"
            self.db.execute("UPDATE runs SET status='FAILED', error=?, finished_at=? WHERE id=?", (msg[:1000], now_iso(), run_id))
            audit.record(self.db, actor, role, "RUN_FAILED", "run", run_id, {"error": msg[:500]})
        return self.get_run(run_id)

    def _upload_columns(self, body: dict[str, Any], result: dict[str, Any]) -> list[str]:
        if body.get("upload_columns"):
            return list(body["upload_columns"]) + ["rule_versions", "run_id", "source_row"]
        cols: list[str] = []
        for r in result.get("upload_rows", []):
            for k in r:
                if k not in cols and not k.startswith("_"):
                    cols.append(k)
        return cols

    def _run_row_basic(self, run_id: str) -> dict[str, Any]:
        r = self.db.one("SELECT r.*, t.name AS template_name FROM runs r JOIN templates t ON t.template_key=r.template_key"
                        " AND t.version=r.template_version WHERE r.id=?", (run_id,))
        if not r:
            raise ServiceError("실행이 없습니다.", 404)
        return r

    def _other_finalized(self, key: str, base_date: str, run_id: str) -> list[str]:
        return [r["id"] for r in self.db.query("SELECT id FROM runs WHERE template_key=? AND base_date=? AND status='FINALIZED' AND id<>?",
                                               (key, base_date, run_id))]

    def _approvals(self, run_id: str) -> list[dict[str, Any]]:
        return self.db.query("SELECT * FROM approvals WHERE run_id=? ORDER BY id", (run_id,))

    def _audit_rows(self, run_id: str) -> list[dict[str, Any]]:
        return self.db.query("SELECT id, at, actor, role, action, entity_id, details_json, hash FROM audit_log WHERE entity_id=? ORDER BY id",
                             (run_id,))

    def get_run(self, run_id: str, full: bool = True) -> dict[str, Any]:
        r = self._run_row_basic(run_id)
        out = {k: v for k, v in r.items() if not k.endswith("_json")}
        out["input_files"] = loads(r["input_files_json"])
        out["summary"] = loads(r["summary_json"])
        out["approvals"] = self._approvals(run_id)
        if r["status"] in ("RUNNING", "FAILED"):
            out["checks"], out["gate"] = [], None
            return out
        result = self._load_result(run_id)
        g = approval.gate(r, result["checks"], out["approvals"], self._other_finalized(r["template_key"], r["base_date"], run_id))
        out["gate"] = g
        out["check_summary"] = summarize(result["checks"])
        out["downloads"] = [p.name for p in sorted((self.settings.runs_dir / run_id).glob("*")) if p.suffix in (".xlsx", ".html", ".csv")]
        if full:
            keys = ("checks", "inputs", "summary", "exceptions", "reconciliation", "journal", "variance", "rule_versions",
                    "confirm_items", "confirmed_changes", "upload_columns_all", "finalized")
            out.update({k: result.get(k) for k in keys})
            out["processed"] = result["processed"][:2000]
            out["processed_total"] = len(result["processed"])
            out["upload_preview"] = result["upload_rows"][:200]
        return to_api(out)

    def list_runs(self, limit: int = 200) -> list[dict[str, Any]]:
        rows = self.db.query("SELECT r.id, r.template_key, r.template_version, r.base_date, r.status, r.created_at, r.created_by,"
                             " r.finished_at, r.summary_json, r.checks_json, r.result_hash, r.error, r.input_files_json, t.name AS template_name"
                             " FROM runs r JOIN templates t ON t.template_key=r.template_key AND t.version=r.template_version"
                             " ORDER BY r.created_at DESC LIMIT ?", (limit,))
        out = []
        for r in rows:
            checks = loads(r.pop("checks_json"), [])
            r["summary"] = loads(r.pop("summary_json"))
            r["input_files"] = loads(r.pop("input_files_json"))
            r["check_summary"] = summarize(checks)["by_status"] if checks else None
            out.append(r)
        return out

    # ------------------------------------------------------------------ 승인
    def act(self, run_id: str, action: str, check_id: str | None, comment: str, actor: str, role: str) -> dict[str, Any]:
        run = self._run_row_basic(run_id)
        if run["status"] in ("RUNNING", "FAILED"):
            raise ServiceError("처리되지 않은 실행입니다.")
        result = self._load_result(run_id)
        check = next((c for c in result["checks"] if c["check_id"] == check_id), None) if check_id else None
        if check_id and not check:
            raise ServiceError(f"검증 항목 없음: {check_id}", 404)
        apps = self._approvals(run_id)
        if action in ("ACKNOWLEDGE", "EXCEPTION") and any(a["action"] == action and a["check_id"] == check_id for a in apps):
            raise ServiceError("이미 처리된 항목입니다.")
        g = approval.gate(run, result["checks"], apps, self._other_finalized(run["template_key"], run["base_date"], run_id))
        try:
            nxt = approval.validate_action(action, run, check, actor, role, comment, g)
        except approval.ApprovalError as e:
            raise ServiceError(str(e), 403 if "직무분리" in str(e) else 400) from e
        with self.db.tx() as c:
            c.execute("INSERT INTO approvals(run_id, action, check_id, actor, role, comment, at) VALUES (?,?,?,?,?,?,?)",
                      (run_id, action, check_id, actor, role, comment.strip(), now_iso()))
            if nxt:
                c.execute("UPDATE runs SET status=? WHERE id=?", (nxt, run_id))
            elif run["status"] in ("BLOCKED", "READY_FOR_REVIEW"):
                g2 = approval.gate(run, result["checks"], apps + [{"action": action, "check_id": check_id}],
                                   self._other_finalized(run["template_key"], run["base_date"], run_id))
                c.execute("UPDATE runs SET status=? WHERE id=?", (g2["status_after_checks"], run_id))
        audit.record(self.db, actor, role, f"RUN_{action}", "run", run_id,
                     {"check_id": check_id, "comment": comment.strip(), "original_status": check and check["status"],
                      "original_severity": check and check["severity"], "from": run["status"], "to": nxt})
        return self.get_run(run_id)

    def finalize(self, run_id: str, comment: str, actor: str, role: str) -> dict[str, Any]:
        run = self._run_row_basic(run_id)
        result = self._load_result(run_id)
        apps = self._approvals(run_id)
        g = approval.gate(run, result["checks"], apps, self._other_finalized(run["template_key"], run["base_date"], run_id))
        if not g["can_finalize"]:
            reasons = [b["reason"] for b in g["blockers"] + g["pending_reviews"]]
            if run["status"] != "APPROVED":
                reasons.insert(0, f"승인(APPROVED) 상태가 아닙니다(현재 {run['status']}).")
            audit.record(self.db, actor, role, "FINALIZE_BLOCKED", "run", run_id, {"reasons": reasons[:20]})
            raise ServiceError("확정이 차단되었습니다: " + " / ".join(reasons)[:800], 409, {"code": "BLOCKED", "reasons": reasons})
        if not comment or len(comment.strip()) < 2:
            raise ServiceError("확정 의견을 입력하세요.")
        rdir = self.settings.runs_dir / run_id
        stem = f"upload_{run['template_key']}_{run['base_date'].replace('-', '')}"
        cols = result["upload_columns_all"]
        files = write_upload_files(rdir, stem, cols, result["upload_rows"])
        amount_cols = [c for c in cols if result["upload_rows"] and isinstance(result["upload_rows"][0].get(c), Decimal)]
        rb = read_back_totals(files["xlsx"], files["csv"], cols, amount_cols)
        expected = {c: sum((r.get(c) or Decimal(0) for r in result["upload_rows"]), Decimal(0)) for c in amount_cols}
        n = len(result["upload_rows"])
        if rb["xlsx_count"] != n or rb["csv_count"] != n or rb["xlsx_sums"] != expected or rb["csv_sums"] != expected:
            for p in files.values():
                p.unlink(missing_ok=True)
            audit.record(self.db, actor, role, "FINALIZE_FAILED_READBACK", "run", run_id, {"readback": to_api(rb)})
            raise ServiceError("업로드 파일 재판독 검증(T05) 실패 — 파일을 폐기했습니다.", 500, {"readback": to_api(rb)})
        with self.db.tx() as c:
            c.execute("INSERT INTO approvals(run_id, action, check_id, actor, role, comment, at) VALUES (?,?,?,?,?,?,?)",
                      (run_id, "FINALIZE", None, actor, role, comment.strip(), now_iso()))
            c.execute("UPDATE runs SET status='FINALIZED' WHERE id=?", (run_id,))
        result["finalized"] = {"by": actor, "at": now_iso(), "files": [p.name for p in files.values()],
                               "readback": to_api(rb), "check": "T05 업로드 파일 재판독 건수·합계 일치",
                               "note": "업로드 파일만 생성했습니다. 원장/외부 시스템에는 반영하지 않았습니다."}
        (rdir / "result.json").write_text(json.dumps(enc(result), ensure_ascii=False), encoding="utf-8")
        audit.record(self.db, actor, role, "RUN_FINALIZED", "run", run_id,
                     {"files": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in files.items()}, "rows": n})
        run = self._run_row_basic(run_id)
        apps = self._approvals(run_id)
        g = approval.gate(run, result["checks"], apps, [])
        build_workbook(rdir / "final.xlsx", run, result, g, apps, self._audit_rows(run_id), final=True)
        (rdir / "report.html").write_text(build_html(run, result, g, apps), encoding="utf-8")
        return self.get_run(run_id)

    def download_path(self, run_id: str, name: str) -> Path:
        rdir = (self.settings.runs_dir / run_id).resolve()
        p = (rdir / name).resolve()
        if p.parent != rdir or not p.exists() or p.suffix not in (".xlsx", ".html", ".csv"):
            raise ServiceError("파일이 없습니다.", 404)
        return p

    # ------------------------------------------------------------------ 대시보드
    def dashboard(self) -> dict[str, Any]:
        runs = self.list_runs(500)
        by_status: dict[str, int] = {}
        for r in runs:
            by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        pending = [r for r in runs if r["status"] in ("READY_FOR_REVIEW", "BLOCKED", "REVIEWED", "APPROVED")]
        fail_counts: dict[str, int] = {}
        for r in runs[:50]:
            for c in loads(self.db.one("SELECT checks_json FROM runs WHERE id=?", (r["id"],))["checks_json"], []) or []:
                if c["status"] == "FAIL":
                    k = f"{c['check_id']} {c['name']}"
                    fail_counts[k] = fail_counts.get(k, 0) + 1
        per_tpl: dict[str, dict[str, Any]] = {}
        for r in runs:
            d = per_tpl.setdefault(r["template_key"], {"template_key": r["template_key"], "name": r["template_name"],
                                                       "runs": 0, "finalized": 0, "last_run": None, "last_status": None})
            d["runs"] += 1
            d["finalized"] += r["status"] == "FINALIZED"
            if d["last_run"] is None:
                d["last_run"], d["last_status"] = r["created_at"], r["status"]
        done = sum(1 for r in runs if r["status"] == "FINALIZED")
        considered = sum(1 for r in runs if r["status"] not in ("FAILED", "REJECTED"))
        tpls = treg.list_templates(self.db)
        return {"by_status": by_status, "pending": pending[:20], "recent": runs[:10],
                "top_failures": sorted(([k, v] for k, v in fail_counts.items()), key=lambda x: -x[1])[:10],
                "completion_rate": round(done / considered, 4) if considered else None,
                "per_template": list(per_tpl.values()),
                "template_count": len({t["template_key"] for t in tpls}),
                "active_templates": sum(1 for t in tpls if t["status"] == "ACTIVE"),
                "audit": audit.verify_chain(self.db)}

    def rule_test(self, body: dict[str, Any]) -> dict[str, Any]:
        from .engine import validate_template
        from .rules import run_rule_tests
        errs = validate_template(body)
        tests = run_rule_tests(body.get("calculations", [])) if body.get("calculations") else {"ok": True, "results": []}
        for c in body.get("calculations", []):
            try:
                CalcRule.from_dict(c)
            except Exception as e:  # noqa: BLE001 — 사용자 입력 검증
                errs.append(f"{c.get('rule_id')}: {e}")
        return {"ok": not errs and tests["ok"], "errors": errs, "tests": tests}
