"""역할 기반 권한(데모 수준). 인증이 아니라 '선택된 역할'에 대한 권한 검사다."""
from __future__ import annotations

import re
import unicodedata

ROLES = ("admin", "preparer", "reviewer", "approver", "viewer")
ROLE_LABELS = {
    "admin": "관리자", "preparer": "업무 담당자", "reviewer": "검토자",
    "approver": "승인자", "viewer": "조회 전용",
}

PERMISSIONS: dict[str, set[str]] = {
    "upload": {"admin", "preparer"},
    "run": {"admin", "preparer"},
    "template_edit": {"admin", "preparer", "approver"},
    "template_activate": {"admin", "approver"},
    "review": {"admin", "reviewer", "approver"},
    "acknowledge": {"admin", "reviewer", "approver"},
    "exception": {"admin", "approver"},
    "approve": {"admin", "approver"},
    "finalize": {"admin", "approver"},
    "settings": {"admin"},
    "view": set(ROLES),
}


class PermissionDenied(Exception):
    pass


def require(role: str, permission: str) -> None:
    if role not in ROLES:
        raise PermissionDenied(f"알 수 없는 역할: {role}")
    if role not in PERMISSIONS[permission]:
        raise PermissionDenied(f"'{ROLE_LABELS[role]}' 역할은 '{permission}' 권한이 없습니다.")


_SAFE_USER = re.compile(r"^[\w가-힣.\-@ ]{1,40}$")


def sanitize_user(name: str | None) -> str:
    name = (name or "").strip() or "local-user"
    if not _SAFE_USER.match(name):
        raise PermissionDenied("사용자 이름에 허용되지 않는 문자가 있습니다.")
    return name


def sanitize_filename(name: str) -> str:
    """표시용 파일명 정화. 저장 경로에는 절대 사용하지 않는다."""
    name = unicodedata.normalize("NFC", name or "file")
    name = name.replace("\\", "/").split("/")[-1]
    name = re.sub(r"[\x00-\x1f<>:\"|?*]", "_", name).strip(" .")
    return (name or "file")[:200]
