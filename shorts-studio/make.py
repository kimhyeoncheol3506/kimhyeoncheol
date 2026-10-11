"""연애 듀토리얼 영상 제작 CLI.

  python make.py projects/<프로젝트>                # 렌더 (narration/ 있으면 음성 포함)
  python make.py projects/<프로젝트> --voice cloud  # Qwen3-TTS 직접 구동으로 음성 생성 후 렌더
  python make.py projects/<프로젝트> --voice voicebox  # PC Voicebox로 음성 생성 후 렌더
  python make.py projects/<프로젝트> --frames 1.0,5.5  # 특정 시점 프레임만 PNG로 (빠른 확인)

결과: output/<프로젝트>/video.mp4, thumbnail.jpg, upload.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--voice", choices=["none", "cloud", "voicebox"], default="none")
    ap.add_argument("--tts-python", default=os.environ.get("TTS_PYTHON", sys.executable))
    ap.add_argument("--models", default=os.environ.get("QWEN_TTS_MODELS", "models"))
    ap.add_argument("--frames", default="")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    if a.voice == "cloud":
        subprocess.check_call([a.tts_python, str(ROOT / "voice/qwen_local.py"), str(proj), "--models", a.models])
        subprocess.call([a.tts_python, str(ROOT / "voice/qa.py"), str(proj)])
    elif a.voice == "voicebox":
        subprocess.check_call([sys.executable, str(ROOT / "voice/voicebox_client.py"), str(proj)])

    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    out = ROOT / "output" / proj.name
    out.mkdir(parents=True, exist_ok=True)
    if script["format"] == "short":
        from studio.short import ShortRenderer as R
    else:
        from studio.long import LongRenderer as R
    r = R(proj)
    if not any(s.audio for s in r.scenes):
        print("! narration/ 없음 → 무음(효과음+BGM) 가이드 버전으로 렌더합니다", flush=True)
    if a.frames:
        r.render(out / "video.mp4", preview_only_frames=[float(x) for x in a.frames.split(",")])
        return
    print(f"렌더: {script['title']} ({r.total:.1f}s)", flush=True)
    r.render(out / "video.mp4")
    if script["format"] == "short":
        st = next((s for s in r.scenes if s.visual.get("mode") == "judge"), r.scenes[0])
        t = r.stamp_time(st) or st.start
        r.render_frame(t + 0.5).convert("RGB").save(out / "thumbnail.jpg", quality=95)
    else:
        from studio.long import thumbnail
        thumbnail(r, out / "thumbnail.jpg")
    upload = dict(script.get("upload", {}))
    if script.get("chapters") and "{CHAPTERS}" in upload.get("description", ""):
        at = {s.id: s.start for s in r.scenes}
        lines = [f"{int(at[i] // 60):02d}:{int(at[i] % 60):02d} {name}" for i, name in script["chapters"]]
        lines[0] = "00:00" + lines[0][5:]
        upload["description"] = upload["description"].replace("{CHAPTERS}", "\n".join(lines))
    upload["duration_sec"] = round(r.total, 1)
    (out / "upload.json").write_text(json.dumps(upload, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    print("완료:", out)


if __name__ == "__main__":
    main()
