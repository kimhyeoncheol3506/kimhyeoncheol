"""수정 도구 (v1.13.8): 고칠 장면만 바꿔서 다시 만든다. 토큰·시간 절약용.

사용:
  python tools/fix_scenes.py projects/<폴더>/project.json  "s012=새 문장"  "s030:pose=놀람"  "s031:room=sky"  [--clips] [--package]
    sNNN=새 문장        그 장면 대사(자막·음성)를 바꾼다 → 그 장면 음성만 다시 녹음
    sNNN:키=값          그 장면 visual의 키를 바꾼다 (pose, room, ant_x, image …). 숫자는 자동 변환
    --clips             바뀐 장면만 짧은 미리보기 mp4로 잘라 output/fix/ 에 저장 (보낼 때 이 파일만 보낸다)
    --package           끝나면 다운로드 묶음(버전 +1) 생성

동작: project.json을 고친 뒤 make_video를 다시 돌린다. make_video의 장면 클립 캐시와 장면별 음성 캐시 덕분에
바뀐 장면만 새로 그리고 새로 녹음하고, 나머지는 그대로 이어 붙인다(화질 손실 없음). 통합 음량·싱크 점검은 이어서 한 번 돌린다.
출력은 몇 줄로 줄여서 보여 준다.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def conv(v):
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("edits", nargs="*")
    ap.add_argument("--clips", action="store_true")
    ap.add_argument("--package", action="store_true")
    a = ap.parse_args()
    pj = os.path.abspath(a.project)
    p = json.load(open(pj, encoding="utf-8"))
    by = {s["id"]: s for s in p["scenes"]}
    changed = []
    for e in a.edits:
        left, _, val = e.partition("=")
        sid, _, key = left.partition(":")
        if sid not in by:
            sys.exit(f"없는 장면: {sid}")
        if key:
            by[sid].setdefault("visual", {})[key] = conv(val)
        else:
            by[sid]["text"] = val
        changed.append(sid)
    json.dump(p, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pdir = os.path.dirname(pj)
    cmd = [sys.executable, os.path.join(ROOT, "make_video.py"), pj] + ([] if a.package else ["--no-package"])
    r = subprocess.run(cmd, capture_output=True, text=True)
    tail = [ln for ln in r.stdout.splitlines() if ln.startswith(("완료", "⚠", "   ⚠")) or "실패" in ln]
    print("\n".join(tail[-6:]) or r.stdout[-400:])
    if r.returncode:
        print(r.stderr[-800:])
        sys.exit(1)
    video = os.path.join(pdir, "output", "video.mp4")
    if a.clips and changed:
        os.makedirs(os.path.join(pdir, "output", "fix"), exist_ok=True)
        cdir = os.path.join(pdir, "clipcache")
        start = 0.0
        for s in p["scenes"]:
            meta = [f for f in os.listdir(cdir) if f.startswith(s["id"] + "_") and f.endswith(".json")]
            T = json.load(open(os.path.join(cdir, meta[0]), encoding="utf-8"))["T"]
            if s["id"] in changed:
                out = os.path.join(pdir, "output", "fix", f"{s['id']}.mp4")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, start - 0.4):.2f}", "-t", f"{T + 0.8:.2f}", "-i", video,
                                "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-c:a", "aac", out])
                print("미리보기:", out)
            start += T
    q = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "verify_video.py"), video], capture_output=True, text=True)
    print("\n".join(ln for ln in q.stdout.splitlines() if ln.startswith(("WARN", "FAIL", "결과"))))


if __name__ == "__main__":
    main()
