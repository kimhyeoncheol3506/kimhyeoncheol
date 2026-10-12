"""HTTP API (FastAPI). 사용자/역할은 헤더로 전달되는 데모용 값이며 인증이 아니다."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import unquote

from fastapi import Depends, FastAPI, File, Header, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, audit, intake
from . import templates as treg
from .config import BASE_DIR, Settings, load_settings
from .security import ROLE_LABELS, ROLES, PermissionDenied, require, sanitize_user
from .service import Service, ServiceError, to_api


class Actor(BaseModel):
    user: str
    role: str


class AnalyzeReq(BaseModel):
    file_ids: list[str]


class PlanReq(BaseModel):
    template_key: str
    version: int | None = None
    files: dict[str, str]
    base_date: str | None = None
    overrides: dict[str, dict[str, str]] = Field(default_factory=dict)


class RunReq(BaseModel):
    template_key: str
    version: int | None = None
    base_date: str
    files: dict[str, str]
    overrides: dict[str, dict[str, str]] = Field(default_factory=dict)
    confirm_changes: bool = False
    confirm_reason: str = ""
    rerun_reason: str = ""


class ActionReq(BaseModel):
    action: str
    check_id: str | None = None
    comment: str


class CommentReq(BaseModel):
    comment: str


class TemplateSaveReq(BaseModel):
    body: dict[str, Any]
    reason: str


class StatusReq(BaseModel):
    status: str
    reason: str


class CloneReq(BaseModel):
    new_key: str
    new_name: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    svc = Service(settings)
    app = FastAPI(title="FinClose AI", version=__version__)
    app.state.svc = svc

    @app.exception_handler(ServiceError)
    async def _svc_err(_: Request, e: ServiceError):
        return JSONResponse({"detail": str(e), **to_api(e.payload)}, status_code=e.status)

    @app.exception_handler(PermissionDenied)
    async def _perm(_: Request, e: PermissionDenied):
        return JSONResponse({"detail": str(e)}, status_code=403)

    @app.exception_handler(intake.IntakeError)
    async def _intake(_: Request, e: intake.IntakeError):
        return JSONResponse({"detail": str(e)}, status_code=e.status)

    @app.exception_handler(treg.TemplateRegistryError)
    async def _treg(_: Request, e: treg.TemplateRegistryError):
        return JSONResponse({"detail": str(e)}, status_code=400)

    def actor(x_finclose_user: str | None = Header(default=None), x_finclose_role: str | None = Header(default=None)) -> Actor:
        user = sanitize_user(unquote(x_finclose_user or ""))
        role = (x_finclose_role or "viewer").strip()
        if role not in ROLES:
            raise PermissionDenied(f"알 수 없는 역할: {role}")
        return Actor(user=user, role=role)

    @app.get("/api/health")
    def health():
        return {"ok": True, "version": __version__, "auth": "DEMO_ROLE_SWITCH_NOT_AUTHENTICATION",
                "external_network": "NONE", "data_dir": str(settings.data_dir)}

    @app.get("/api/roles")
    def roles():
        return [{"code": r, "label": ROLE_LABELS[r]} for r in ROLES]

    @app.post("/api/files")
    def upload(files: list[UploadFile] = File(...), a: Actor = Depends(actor)):
        require(a.role, "upload")
        out = []
        for f in files:
            try:
                rec = intake.save_upload(svc.db, settings, f.file, f.filename or "file", a.user, a.role)
                out.append({"ok": True, **svc._file_brief(intake.get_file(svc.db, rec["id"])), "duplicate_of": rec["duplicate_of"]})
            except intake.IntakeError as e:
                out.append({"ok": False, "name": f.filename, "error": str(e), "status_code": e.status})
        return out

    @app.get("/api/files")
    def list_files(a: Actor = Depends(actor)):
        rows = svc.db.query("SELECT id FROM files ORDER BY uploaded_at DESC LIMIT 200")
        return [svc._file_brief(intake.get_file(svc.db, r["id"])) for r in rows]

    @app.get("/api/files/{fid}")
    def file_detail(fid: str, a: Actor = Depends(actor)):
        f = intake.get_file(svc.db, fid)
        if not f:
            raise ServiceError("파일 없음", 404)
        f.pop("stored_path", None)
        return f

    @app.post("/api/analyze")
    def analyze(req: AnalyzeReq, a: Actor = Depends(actor)):
        require(a.role, "view")
        return to_api(svc.analyze(req.file_ids))

    @app.post("/api/plan")
    def plan(req: PlanReq, a: Actor = Depends(actor)):
        return to_api(svc.plan(req.template_key, req.version, req.files, req.base_date, req.overrides))

    @app.post("/api/runs")
    def create_run(req: RunReq, a: Actor = Depends(actor)):
        require(a.role, "run")
        return svc.create_run(req.template_key, req.version, req.base_date, req.files, req.overrides, a.user, a.role,
                              req.confirm_changes, req.confirm_reason, req.rerun_reason)

    @app.get("/api/runs")
    def runs(a: Actor = Depends(actor)):
        return to_api(svc.list_runs())

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str, a: Actor = Depends(actor)):
        return svc.get_run(run_id)

    @app.post("/api/runs/{run_id}/actions")
    def run_action(run_id: str, req: ActionReq, a: Actor = Depends(actor)):
        perm = {"REVIEW": "review", "ACKNOWLEDGE": "acknowledge", "EXCEPTION": "exception", "APPROVE": "approve",
                "REJECT": "approve"}.get(req.action)
        if not perm:
            raise ServiceError("알 수 없는 작업")
        require(a.role, perm)
        return svc.act(run_id, req.action, req.check_id, req.comment, a.user, a.role)

    @app.post("/api/runs/{run_id}/finalize")
    def finalize(run_id: str, req: CommentReq, a: Actor = Depends(actor)):
        require(a.role, "finalize")
        return svc.finalize(run_id, req.comment, a.user, a.role)

    @app.get("/api/runs/{run_id}/download/{name}")
    def download(run_id: str, name: str, a: Actor = Depends(actor)):
        p = svc.download_path(run_id, name)
        audit.record(svc.db, a.user, a.role, "DOWNLOAD", "run", run_id, {"file": name})
        return FileResponse(p, filename=p.name)

    @app.get("/api/runs/{run_id}/files/{name}")
    def download_get(run_id: str, name: str, u: str = "local-user", r: str = "viewer"):
        """<a href> 다운로드용(헤더를 못 보내는 경우). 조회 권한만 필요."""
        a = actor(u, r)
        p = svc.download_path(run_id, name)
        audit.record(svc.db, a.user, a.role, "DOWNLOAD", "run", run_id, {"file": name})
        return FileResponse(p, filename=p.name)

    @app.get("/api/templates")
    def templates(a: Actor = Depends(actor)):
        return treg.list_templates(svc.db)

    @app.get("/api/templates/{key}/{version}")
    def template(key: str, version: int, a: Actor = Depends(actor)):
        t = treg.get(svc.db, key, version)
        if not t:
            raise ServiceError("템플릿 없음", 404)
        return t

    @app.post("/api/templates")
    def save_template(req: TemplateSaveReq, a: Actor = Depends(actor)):
        require(a.role, "template_edit")
        return treg.save_version(svc.db, req.body, a.user, a.role, req.reason)

    @app.post("/api/templates/test")
    def test_template(body: dict[str, Any], a: Actor = Depends(actor)):
        return svc.rule_test(body)

    @app.post("/api/templates/{key}/{version}/status")
    def template_status(key: str, version: int, req: StatusReq, a: Actor = Depends(actor)):
        require(a.role, "template_activate")
        return treg.set_status(svc.db, key, version, req.status, a.user, a.role, req.reason)

    @app.post("/api/templates/{key}/{version}/clone")
    def template_clone(key: str, version: int, req: CloneReq, a: Actor = Depends(actor)):
        require(a.role, "template_edit")
        return treg.clone(svc.db, key, version, req.new_key, req.new_name, a.user, a.role)

    @app.get("/api/dashboard")
    def dashboard(a: Actor = Depends(actor)):
        return to_api(svc.dashboard())

    @app.get("/api/audit")
    def audit_list(entity_id: str | None = None, limit: int = 300, a: Actor = Depends(actor)):
        if entity_id:
            return svc.db.query("SELECT * FROM audit_log WHERE entity_id=? ORDER BY id DESC LIMIT ?", (entity_id, limit))
        return svc.db.query("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))

    @app.get("/api/audit/verify")
    def audit_verify(a: Actor = Depends(actor)):
        return audit.verify_chain(svc.db)

    @app.get("/api/settings/materiality")
    def get_mat(a: Actor = Depends(actor)):
        return svc.materiality()

    @app.put("/api/settings/materiality")
    def put_mat(body: dict[str, Any], a: Actor = Depends(actor)):
        require(a.role, "settings")
        return svc.set_materiality(body, a.user, a.role)

    dist = BASE_DIR / "frontend" / "dist"
    if dist.exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{path:path}")
        def spa(path: str):
            p = (dist / path).resolve()
            if path and p.is_file() and dist.resolve() in p.parents:
                headers = {"Cache-Control": "no-cache"} if p.name in ("sw.js", "manifest.webmanifest") else None
                return FileResponse(p, headers=headers)
            return FileResponse(dist / "index.html", headers={"Cache-Control": "no-cache"})

    return app
