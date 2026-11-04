"""최종본 세트(영상·유튜브 텍스트·썸네일)를 '주제 이름 + 버전'으로 내보낸다(현철님 2026-11-04, PUB-03).

    release/<주제>/<주제>_v4.mp4
    release/<주제>/<주제>_v4_유튜브.txt
    release/<주제>/<주제>_v4_썸네일.jpg
    release/<주제>/버전기록.md        ← 버전마다 날짜·길이·검수 결과·바뀐 점 한 줄씩 쌓인다

<주제> = 대본의 `name:` (예: "AI브라우저_어사이드_사용법"), 없으면 slug. 버전은 그 폴더의 가장 큰 vN + 1.
세트 중 하나라도 바뀌면(영상 재빌드, 썸네일 글자 수정 등) 새 버전으로 세트 전체를 다시 내보낸다(파일끼리 버전이 어긋나지 않게).
대본 `release_note:` 나 make_editorial --note 로 '바뀐 점'을 적는다.
"""
import datetime
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = [("final.mp4", ".mp4"), ("youtube.txt", "_유튜브.txt"), ("thumbnail.jpg", "_썸네일.jpg")]


def topic_name(proj):
    n = proj.get("name") or proj.get("slug") or "영상"
    n = re.sub(r'[\\/:*?"<>|]', "", str(n)).strip()          # Windows 에서 못 쓰는 글자 제거
    return re.sub(r"\s+", "_", n)


def next_version(folder, name):
    vs = [int(m.group(1)) for p in folder.glob(f"{name}_v*") if (m := re.match(rf"{re.escape(name)}_v(\d+)", p.name))]
    return max(vs, default=0) + 1


def _qc_line(out_dir):
    q = Path(out_dir) / "_work" / "qc.json"
    if not q.exists():
        return "검수 안 함"
    d = json.load(open(q, encoding="utf-8"))
    return (f"음성불일치 {len(d.get('asr_bad', []))} · 끊김 {len(d.get('gaps', []))} · 멈춤 {len(d.get('freeze', []))} · "
            f"검은화면 {len(d.get('black', []))} · 개인정보 {len(d.get('pii', []))} · 자막 {len(d.get('subtitle_lint', []))}")


def make(proj, out_dir, note=None, version=None, stand_in=False, log=print):
    out_dir = Path(out_dir)
    name = topic_name(proj) + ("_임시목소리" if stand_in else "")
    folder = ROOT / "release" / topic_name(proj)
    folder.mkdir(parents=True, exist_ok=True)
    v = version or next_version(folder, name)
    made = []
    for src, suf in PARTS:
        p = out_dir / src
        if p.exists():
            dst = folder / f"{name}_v{v}{suf}"
            shutil.copy2(p, dst)
            made.append(dst)
        else:
            log(f"  ⚠ 세트에 {src} 없음(PUB-03)")
    dur = ""
    try:
        import subprocess
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_dir / "final.mp4")],
                           capture_output=True, text=True)
        s = float(r.stdout.strip())
        dur = f"{int(s // 60)}:{int(s % 60):02d}"
    except Exception:
        pass
    log_md = folder / "버전기록.md"
    if not log_md.exists():
        log_md.write_text(f"# {topic_name(proj)} 버전 기록\n\n| 버전 | 날짜 | 길이 | 검수 | 바뀐 점 |\n|---|---|---|---|---|\n", encoding="utf-8")
    with open(log_md, "a", encoding="utf-8") as f:
        f.write(f"| v{v}{' (임시목소리)' if stand_in else ''} | {datetime.date.today()} | {dur} | {_qc_line(out_dir)} | "
                f"{(note or proj.get('release_note') or '').strip().replace('|', '/') or '-'} |\n")
    for m in made:
        log(f"  내보냄: {m.relative_to(ROOT)}")
    return v, made
