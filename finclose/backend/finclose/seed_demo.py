"""시연용 과거 결산 이력 생성(가상 데이터).

python -m finclose.seed_demo [--force]
과거 4개 기준일(2025-09, 2025-12, 2026-06, 2026-08)의 채권 평가 업무를 실행·검토·승인·확정해
당기(2026-09) 실행 시 전월·전분기·전년동기·전기말 비교가 가능하도록 한다.
감사 로그에는 'demo-seed' 행위로 기록된다. 실제 업무 데이터 폴더에는 쓰지 말 것(데스크톱 앱은 연습 모드 전용 폴더 사용).
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import audit, intake, sample_data
from .config import BASE_DIR, load_settings
from .service import Service


def seed(svc: Service, sd: Path, force: bool = False, log=print) -> bool:
    if not (sd / "history").exists():
        sample_data.generate_all(sd)
        log(f"가상 시연 데이터 생성: {sd}")
    if svc.db.one("SELECT 1 FROM runs LIMIT 1") and not force:
        log("이미 실행 이력이 있어 시연 이력을 만들지 않았습니다.")
        return False
    s = svc.settings
    audit.record(svc.db, "demo-seed", "admin", "DEMO_SEED_START", "system", "seed", {"note": "가상 데이터 시연 이력 생성"})
    for d in sorted(p for p in (sd / "history").iterdir() if p.is_dir()):
        roles = {}
        for role, pattern in (("holdings", "보유채권내역_*.xlsx"), ("prices", "외부평가단가_*.xlsx"), ("prior", "전월평가결과_*.xlsx")):
            p = next(d.glob(pattern))
            with open(p, "rb") as f:
                roles[role] = intake.save_upload(svc.db, s, f, p.name, "데모담당", "preparer")["id"]
        run = svc.create_run("BOND_EXT_PRICE_RECON", None, d.name, roles, {}, "데모담당", "preparer")
        if run["status"] != "READY_FOR_REVIEW":
            log(f"  {d.name}: {run['status']} — 시연 이력 확정 생략")
            continue
        for p in run["gate"]["pending_reviews"]:
            svc.act(run["id"], "ACKNOWLEDGE", p["check_id"], "[시연] 예시 산식·예시 계정임을 확인", "데모검토", "reviewer")
        svc.act(run["id"], "REVIEW", None, "[시연] 검토 완료", "데모검토", "reviewer")
        svc.act(run["id"], "APPROVE", None, "[시연] 승인", "데모승인", "approver")
        svc.finalize(run["id"], "[시연] 확정", "데모승인", "approver")
        log(f"  {d.name}: 확정 완료 ({run['id']})")
    return True


def main() -> None:
    svc = Service(load_settings())
    if seed(svc, BASE_DIR / "sample_data", force="--force" in sys.argv):
        print("시연 이력 생성 완료. 이제 sample_data/bond_2026-09 의 3개 파일로 당기 결산을 실행해 보세요.")


if __name__ == "__main__":
    main()
