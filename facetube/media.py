"""외부에서 만든 영상·이미지(Pavo AI, Digen AI, Pollo 등)를 프레임 이미지로 풀어 장면에 넣는다.

- 영상은 소리를 버리고(내레이션이 주인공) 30fps 로 상자 안에 맞춰 줄인 JPG 프레임으로 푼다.
- 장면보다 짧으면 반복 재생(정지 화면 금지), 길면 장면 길이만큼만 쓴다.
- 이미지(png/jpg/webp)는 한 장짜리로 취급한다.
"""
import glob
import json
import os
import shutil
import subprocess
from pathlib import Path

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def probe(path):
    """(너비, 높이, 길이초) — 회전 정보를 반영한다."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"영상/이미지를 읽을 수 없음: {path}")
    j = json.loads(r.stdout)
    st = (j.get("streams") or [{}])[0]
    w, h = int(st.get("width", 0)), int(st.get("height", 0))
    rot = 0
    for sd in st.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if abs(rot) in (90, 270):
        w, h = h, w
    dur = float((j.get("format") or {}).get("duration") or 0)
    if not w or not h:
        raise RuntimeError(f"화면 크기를 알 수 없음: {path}")
    return w, h, dur


def _even(x):
    x = int(round(x))
    return x if x % 2 == 0 else x + 1


def prep_frames(path, out_dir, box_w, box_h, dur, fps=30, start=0.0, loop=True, max_upscale=2.0):
    """path 의 영상/이미지를 box_w×box_h 안에 맞춰 out_dir/f_00001.jpg … 로 푼다."""
    path = str(path)
    if not os.path.exists(path):
        raise SystemExit(f"소재 파일이 없음: {path}\n  → `python tools/list_media_requests.py <프로젝트.yaml>` 로 사이트에서 만들어 올 소재 목록(프롬프트 포함)을 확인하세요")
    w, h, clip_dur = probe(path)
    ratio = min(box_w / w, box_h / h, max_upscale)
    ow, oh = _even(w * ratio), _even(h * ratio)
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)
    still = Path(path).suffix.lower() in IMG_EXT
    vf = f"scale={ow}:{oh}:flags=lanczos"
    if still:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", vf, "-frames:v", "1", "-q:v", "2",
                        os.path.join(out_dir, "f_00001.jpg")], check=True)
        return {"n": 1, "fps": fps, "w": ow, "h": oh, "loop": False, "still": True, "clip_dur": 0.0, "src_w": w, "src_h": h}
    avail = max(0.2, clip_dur - start)
    take = min(avail, dur)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", path, "-t", f"{take:.3f}", "-an",
                    "-vf", f"fps={fps},{vf}", "-q:v", "3", os.path.join(out_dir, "f_%05d.jpg")], check=True)
    n = len(glob.glob(os.path.join(out_dir, "f_*.jpg")))
    if n == 0:
        raise RuntimeError(f"프레임을 풀지 못함: {path}")
    return {"n": n, "fps": fps, "w": ow, "h": oh, "loop": loop, "still": False, "clip_dur": round(clip_dur, 2),
            "src_w": w, "src_h": h, "short_by": round(max(0.0, dur - avail), 2)}


def ai_issues(entries, st):
    """AI 소재 점검. entries: [(장면 이름, media dict, media_info 또는 None)] -> 위반 문자열 목록.
    기록(tool/model/generated_on), 도구 약관 확인 여부(style.yaml external_tools), 배지, 해상도를 본다."""
    reg, cfg, out = st.get("external_tools", {}), st.get("ai_media", {}), []
    for label, md, info in entries:
        if not md or not md.get("ai"):
            continue
        miss = [k for k in cfg.get("require_fields", []) if not md.get(k)]
        if miss:
            out.append(f"[AI] {label}: AI 소재의 {', '.join(miss)} 미기입 (어느 사이트·모델·언제 만들었는지 기록)")
        tk = str(md.get("tool", "")).lower()
        tool = next((v for k, v in reg.items() if k in tk or v["name"].lower() in tk), None)
        if tool is None:
            out.append(f"[AI] {label}: '{md.get('tool')}' 는 external_tools 에 없는 도구 — 약관(상업 이용)을 확인해 style.yaml 에 등록")
        elif not tool.get("terms_checked"):
            out.append(f"[AI] {label}: {tool['name']} 약관(상업 이용) 미확인 — 수익 채널에 쓰기 전에 사이트 약관에서 확인")
        if cfg.get("badge") and md.get("badge") is False:
            out.append(f"[AI] {label}: 'AI 생성' 배지를 껐음 — 표시 의무(도구 약관·플랫폼 정책) 확인")
        if info and info.get("src_w") and min(info["src_w"], info["src_h"]) < 480:
            out.append(f"[AI] {label}: 원본 해상도가 낮음({info['src_w']}x{info['src_h']}) — 흐릿할 수 있음")
    return out
