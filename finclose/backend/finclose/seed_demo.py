"""시연용 과거 결산 이력 생성(가상 데이터). 이미 실행 이력이 있으면 아무것도 하지 않는다.

python -m finclose.seed_demo
과거 4개 기준일(2025-09, 2025-12, 2026-06, 2026-08)의 채권 평가 업무를 실행·검토·승인·확정해
당기(2026-09) 실행 시 전월·전분기·전년동기·전기말 비교가 가능하도록 한다.
감사 로그에는 'demo-seed' 행위로 기록된다.
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import audit, intake, sample_data
from .config import BASE_DIR, load_settings
from .service import Service


def main() -> None:
    s = load_settings()
    svc = Service(s)
    sd = BASE_DIR / "sample_data"
    if not (sd / "bond_2026-09").exists():
        sample_data.generate_all(sd)
        print(f"가상 시연 데이터 생성: {sd}")
    if svc.db.one("SELECT 1 FROM runs LIMIT 1") and "--force" not in sys.argv:
        print("이미 실행 이력이 있어 시연 이력을 만들지 않았습니다(--force로 강제).")
        return
    audit.record(svc.db, "demo-seed", "admin", "DEMO_SEED_START", "system", "seed", {"note": "가상 데이터 시연 이력 생성"})
    for d in sorted(p for p in (sd / "history").iterdir() if p.is_dir()):
        roles = {}
        for role, pattern in (("holdings", "보유채권내역_*.xlsx"), ("prices", "외부평가단가_*.xlsx"), ("prior", "전월평가결과_*.xlsx")):
            p = next(d.glob(pattern))
            with open(p, "rb") as f:
                roles[role] = intake.save_upload(svc.db, s, f, p.name, "데모담당", "preparer")["id"]
        run = svc.create_run("BOND_EXT_PRICE_RECON", None, d.name, roles, {}, "데모담당", "preparer")
        if run["status"] != "READY_FOR_REVIEW":
            print(f"  {d.name}: {run['status']} — 시연 이력 확정 생략")
            continue
        for p in run["gate"]["pending_reviews"]:
            svc.act(run["id"], "ACKNOWLEDGE", p["check_id"], "[시연] 예시 산식·예시 계정임을 확인", "데모검토", "reviewer")
        svc.act(run["id"], "REVIEW", None, "[시연] 검토 완료", "데모검토", "reviewer")
        svc.act(run["id"], "APPROVE", None, "[시연] 승인", "데모승인", "approver")
        svc.finalize(run["id"], "[시연] 확정", "데모승인", "approver")
        print(f"  {d.name}: 확정 완료 ({run['id']})")
    print("시연 이력 생성 완료. 이제 sample_data/bond_2026-09 의 3개 파일로 당기 결산을 실행해 보세요.")


if __name__ == "__main__":
    main()
