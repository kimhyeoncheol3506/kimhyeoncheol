"""파일 수집. 원본은 UUID 이름으로 읽기전용 저장하고 SHA-256을 기록한다. 업로드만으로 아무것도 실행하지 않는다."""
from __future__ import annotations

import errno
import hashlib
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, BinaryIO

from . import audit
from .config import Settings
from .db import Database, dumps, loads, now_iso
from .parsers import ParseError, parse_file
from .profiler import profile_table
from .security import sanitize_filename

ALLOWED_EXT = {"xlsx", "xlsm", "csv", "txt", "pdf"}
CHUNK = 1024 * 1024


class IntakeError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def save_upload(db: Database, settings: Settings, stream: BinaryIO, filename: str, actor: str, role: str) -> dict[str, Any]:
    display = sanitize_filename(filename)
    ext = _ext(display)
    if ext == "xls":
        raise IntakeError("구형 .xls는 지원하지 않습니다. Excel에서 .xlsx로 저장 후 업로드하세요.")
    if ext not in ALLOWED_EXT:
        raise IntakeError(f"허용되지 않는 파일 형식입니다: .{ext or '(없음)'} (허용: {', '.join(sorted(ALLOWED_EXT))})")
    settings.ensure_dirs()
    free_mb = shutil.disk_usage(settings.upload_dir).free / 1024 / 1024
    if free_mb < settings.min_free_disk_mb:
        raise IntakeError(f"저장 공간이 부족합니다(여유 {free_mb:.0f}MB).", 507)

    fid = uuid.uuid4().hex
    dest = settings.upload_dir / f"{fid}.{ext}"
    tmp = dest.with_suffix(dest.suffix + ".part")
    h = hashlib.sha256()
    size = 0
    limit = settings.max_upload_mb * 1024 * 1024
    try:
        with open(tmp, "xb") as out:
            while True:
                chunk = stream.read(CHUNK)
                if not chunk:
                    break
                size += len(chunk)
                if size > limit:
                    raise IntakeError(f"파일 크기 제한({settings.max_upload_mb}MB)을 초과했습니다.", 413)
                h.update(chunk)
                out.write(chunk)
        if size == 0:
            raise IntakeError("빈 파일입니다.")
        os.replace(tmp, dest)
        os.chmod(dest, 0o444)
    except OSError as e:
        tmp.unlink(missing_ok=True)
        if e.errno == errno.ENOSPC:
            raise IntakeError("저장 공간이 부족해 업로드를 중단했습니다. 원본 데이터는 변경되지 않았습니다.", 507) from e
        raise IntakeError(f"파일 저장 실패: {e.strerror}", 500) from e
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise

    sha = h.hexdigest()
    dups = db.query("SELECT id, original_name, uploaded_at FROM files WHERE sha256=? AND status='PARSED'", (sha,))
    status, error, metadata, profile = "PARSED", None, None, None
    try:
        parsed = parse_file(dest, ext, display, settings.max_rows)
        metadata = parsed.summary()
        profile = [profile_table(t) for t in parsed.tables]
    except ParseError as e:
        status, error = "ERROR", str(e)
    rec = {
        "id": fid, "original_name": display, "stored_path": str(dest), "ext": ext, "size": size, "sha256": sha,
        "uploaded_at": now_iso(), "uploaded_by": actor, "status": status, "error": error,
    }
    db.execute(
        "INSERT INTO files(id, original_name, stored_path, ext, size, sha256, uploaded_at, uploaded_by, status, error,"
        " metadata_json, profile_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (fid, display, str(dest), ext, size, sha, rec["uploaded_at"], actor, status, error,
         dumps(metadata) if metadata else None, dumps(profile) if profile else None),
    )
    audit.record(db, actor, role, "FILE_UPLOADED", "file", fid,
                 {"name": display, "sha256": sha, "size": size, "status": status, "error": error,
                  "duplicate_of": [d["id"] for d in dups]})
    rec["duplicate_of"] = dups
    return rec


def get_file(db: Database, fid: str) -> dict[str, Any] | None:
    r = db.one("SELECT * FROM files WHERE id=?", (fid,))
    if not r:
        return None
    r["metadata"] = loads(r.pop("metadata_json"))
    r["profile"] = loads(r.pop("profile_json"))
    return r


def file_sha_ok(rec: dict[str, Any]) -> bool:
    h = hashlib.sha256()
    with open(rec["stored_path"], "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest() == rec["sha256"]
