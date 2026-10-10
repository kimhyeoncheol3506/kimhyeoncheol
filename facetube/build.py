"""대본(YAML) -> 타임라인 -> 프레임 렌더 -> 오디오 믹스 -> mp4."""
import copy
import hashlib
import json
import math
import os
import subprocess
from multiprocessing import Pool

import cairo
import numpy as np
import soundfile as sf
import yaml

from . import audio as A
from .gfx import rgba, text_surface, blit, ease_out, pop_scale, missing_glyphs
from .scenes import DRAW, background, W, H
from .textnorm import split_chunks, wrap_lines, emphasis_spans, strip_markup, lint_subtitle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_style(path=None):
    st = yaml.safe_load(open(path or os.path.join(ROOT, "style.yaml"), encoding="utf-8"))
    for k, v in (st.get("measured") or {}).items():   # 참고영상 실측값 우선
        if isinstance(v, dict) and isinstance(st.get(k), dict):
            st[k].update(v)
    return st


# ====================================================================== 타임라인
def build_timeline(project, st, workdir, voice, log=print):
    os.makedirs(os.path.join(workdir, "tts"), exist_ok=True)
    pc = st["pacing"]
    scenes, t = [], 0.25
    voice_track_parts = []   # (start, samples)
    sfx_events = []
    tts_report = []
    for si, raw in enumerate(project["scenes"]):
        sc = copy.deepcopy(raw)
        sc.setdefault("type", "stage")
        sc["index"] = si
        if si > 0:
            t += pc["gap_scene"]
        sc["start"] = t
        t += sc.get("lead", 0.12)
        say = sc.get("say", [])
        sentences = [say] if isinstance(say, str) else say
        chunks = []
        for sent in sentences:
            for ck in split_chunks(sent, st["subtitle"]["max_chars_per_line"], st["subtitle"]["max_lines"]):
                key = hashlib.md5(f"{voice.backend}|{voice.voice}|{voice.speed}|{ck}".encode()).hexdigest()[:16]
                wav = os.path.join(workdir, "tts", key + ".wav")
                meta_p = wav + ".json"
                if os.path.exists(wav) and os.path.exists(meta_p):
                    x, _ = sf.read(wav, dtype="float32")
                    info = json.load(open(meta_p))
                else:
                    x, info = voice.say(ck)
                    sf.write(wav, x, A.SR)
                    json.dump(info, open(meta_p, "w"), ensure_ascii=False)
                dur = len(x) / A.SR
                chunks.append({"text": ck, "start": t, "end": t + dur, "scene": si})
                voice_track_parts.append((t, x))
                tts_report.append({"scene": si, "text": strip_markup(ck), **info, "start": round(t, 2), "dur": round(dur, 2)})
                log(f"  [{si}] {strip_markup(ck)}  ({dur:.2f}s, CER {info.get('cer')}, 시도 {info.get('tries')})")
                t += dur + pc["gap_in_sentence"]
            t += pc["gap_sentence"] - pc["gap_in_sentence"]
        # 자막은 다음 덩어리 시작 직전까지 유지(깜빡임 방지)
        for a, b in zip(chunks, chunks[1:]):
            a["show_end"] = b["start"]
        if chunks:
            chunks[-1]["show_end"] = chunks[-1]["end"] + 0.15
        t = max(t, sc["start"] + sc.get("min_dur", 0))
        t += sc.get("hold", 0)
        sc["chunks"] = chunks
        scenes.append(sc)
    # 장면 끝 = 다음 장면 시작
    for a, b in zip(scenes, scenes[1:]):
        a["end"] = b["start"]
    scenes[-1]["end"] = t + scenes[-1].get("tail", 0.6)
    total = scenes[-1]["end"]

    # 효과음 자동 배치(규칙집 §5)
    for sc in scenes:
        s0 = sc["start"]
        if sc["index"] > 0:
            sfx_events.append((max(0, s0 - 0.12), "whoosh", -3))
        if sc.get("big"):
            sfx_events.append((s0 + _chunk_off(sc, sc.get("big_at", 0)), "pop", 0))
        if sc["type"] == "number":
            ra = s0 + _chunk_off(sc, sc.get("reveal_at", 0))
            n = 8
            for k in range(n):
                sfx_events.append((ra + 0.05 + sc.get("count_sec", 0.8) * (k / n) ** 0.6, "tick", -10))
            sfx_events.append((ra + 0.05 + sc.get("count_sec", 0.8), sc.get("hit_sfx", "boom"), -2))
        if sc["type"] == "headline" and sc.get("highlight"):
            sfx_events.append((s0 + _chunk_off(sc, sc.get("highlight_at", 1)), "swish", -4))
        if sc["type"] == "compare":
            for k, it in enumerate(sc["items"]):
                sfx_events.append((s0 + _chunk_off(sc, it.get("at", 0)) + k * 0.15, "pop", -6))
        if sc["type"] == "list":
            for k, it in enumerate(sc["items"]):
                at = it.get("at", k) if isinstance(it, dict) else k
                sfx_events.append((s0 + _chunk_off(sc, at), "pop", -6))
        if sc["type"] == "title":
            sfx_events.append((s0 + 0.15, "tada", -6))
        if sc["type"] == "outro":
            sfx_events.append((s0 + sc.get("click_at", 1.6), "click", 0))
            sfx_events.append((s0 + sc.get("click_at", 1.6) + 0.05, "ding", -6))
        for p in sc.get("props", []):
            if p.get("sfx", True):
                sfx_events.append((s0 + _chunk_off(sc, p.get("at", 0)), "pop", -10))
        for e in sc.get("sfx", []):
            sfx_events.append((s0 + _chunk_off(sc, e.get("at", 0)) + e.get("offset", 0), e["name"], e.get("db", 0)))

    # 오디오 트랙
    n = int(math.ceil(total * A.SR)) + A.SR
    vtrack = np.zeros(n, np.float32)
    for s, x in voice_track_parts:
        A.place(vtrack, x, s)
    strack = np.zeros(n, np.float32)
    for s, name, db in sfx_events:
        A.place(strack, A.sfx(name), s, db)
    btrack = A.bgm(n / A.SR, bpm=project.get("bgm_bpm", 104), mood=project.get("bgm_mood", "bright"))
    A.write(os.path.join(workdir, "voice.wav"), vtrack)
    A.write(os.path.join(workdir, "sfx.wav"), strack)
    A.write(os.path.join(workdir, "bgm.wav"), btrack)

    # 입모양용 음량 곡선(프레임 단위)
    fps = st["video"]["fps"]
    hop = A.SR // fps
    nf = int(math.ceil(total * fps))
    env = np.array([np.sqrt(np.mean(vtrack[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(nf)])
    env = np.clip(env / (np.percentile(env[env > 1e-3], 90) if np.any(env > 1e-3) else 1), 0, 1.2)
    tl = {"scenes": scenes, "total": total, "fps": fps, "env": env.tolist(), "tts": tts_report,
          "sfx": [(round(a, 2), b) for a, b, _ in sorted(sfx_events)]}
    json.dump(tl, open(os.path.join(workdir, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    return tl


def _chunk_off(sc, i):
    ch = sc["chunks"]
    if not ch:
        return 0.0
    return ch[max(0, min(i, len(ch) - 1))]["start"] - sc["start"]


# ====================================================================== 프레임
def subtitle_surface(text, st):
    s = st["subtitle"]
    lines = wrap_lines(text, s["max_chars_per_line"])
    segs = []
    for ln in lines:
        plain, spans = emphasis_spans(ln)
        cur, pos = [], 0
        for a, b in spans:
            if a > pos:
                cur.append((plain[pos:a], s["color"]))
            cur.append((plain[a:b], s["emphasis_color"]))
            pos = b
        if pos < len(plain):
            cur.append((plain[pos:], s["color"]))
        segs.append(tuple(cur))
    return text_surface(tuple(segs), s["font"], s["size"], stroke=s["stroke"], stroke_color=s["stroke_color"],
                        shadow=tuple(s["shadow"]) if s.get("shadow") else None)


def big_surface(text, st):
    b = st["big_caption"]
    return text_surface(((((text, b["color"]),),)), b["font"], b["size"], stroke=b.get("stroke", 0),
                        box=b["box_color"])


def render_frame(ctx, content, content_ctx, sc, t_global, fi, tl, st):
    t = t_global - sc["start"]
    chunks = sc["chunks"]
    ci = 0
    for k, c in enumerate(chunks):
        if t_global >= c["start"] - 0.02:
            ci = k
    env = tl["env"]
    amp = env[fi] if fi < len(env) else 0.0
    # 1) 콘텐츠 레이어
    background(content_ctx, sc, t, st)
    DRAW[sc["type"]](content_ctx, sc, t, ci, amp, st)
    # 2) 카메라: 컷마다 번갈아 펀치인 + 컷 안에서 천천히 줌 + 장면 진입 줌
    pc = st["pacing"]
    zoom = 1.0
    if sc.get("camera", True):
        cut_idx = ci if not chunks else sum(1 for c in chunks[:ci + 1] if c["end"] - c["start"] >= pc["cut_min_sec"] * 0.5)
        zoom = pc["punch_zoom"] if cut_idx % 2 == 1 else 1.0
        if chunks:
            c = chunks[ci]
            span = max(0.3, c.get("show_end", c["end"]) - c["start"])
            zoom += pc["drift_zoom"] * max(0, min(1, (t_global - c["start"]) / span))
    zoom *= 1 + 0.16 * (1 - ease_out(min(1, t / st["transition"]["dur"])))  # 장면 진입
    fx, fy = sc.get("focus", (0.5, 0.45))
    ctx.save()
    ctx.translate(fx * W, fy * H)
    ctx.scale(zoom, zoom)
    ctx.translate(-fx * W, -fy * H)
    ctx.set_source_surface(content, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()
    # 3) 큰 강조 자막
    if sc.get("big"):
        bt = t - _chunk_off(sc, sc.get("big_at", 0))
        if bt >= 0:
            b = st["big_caption"]
            s = pop_scale(bt, b["pop_sec"], b["overshoot"])
            blit(ctx, big_surface(sc["big"], st), W / 2, b["y"] * H, scale=s, rot=math.radians(-2))
    # 4) 출처 표기
    if sc.get("source"):
        s = st["source_label"]
        surf = text_surface(((("출처: " + sc["source"], s["color"]),),), s["font"], s["size"], box=s["box"])
        blit(ctx, surf, W - 24 - surf.get_width() / 2, 24 + surf.get_height() / 2)
    # 5) 하단 자막
    for c in chunks:
        if c["start"] - 0.02 <= t_global < c.get("show_end", c["end"]):
            surf = subtitle_surface(c["text"], st)
            blit(ctx, surf, W / 2, st["subtitle"]["y"] * H - (surf.get_height() - 120) / 2 * 0.0)
            break


def _render_scene(args):
    si, tl, st, out = args
    sc = tl["scenes"][si]
    fps = tl["fps"]
    f0, f1 = int(round(sc["start"] * fps)), int(round(sc["end"] * fps))
    if si == 0:
        f0 = 0
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf",
                          str(st["video"]["crf"]), "-pix_fmt", "yuv420p", "-g", str(fps * 2), out],
                         stdin=subprocess.PIPE)
    frame = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    content = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx, cctx = cairo.Context(frame), cairo.Context(content)
    for fi in range(f0, f1):
        tg = fi / fps
        render_frame(ctx, content, cctx, sc, tg, fi, tl, st)
        frame.flush()
        p.stdin.write(bytes(frame.get_data()))
    p.stdin.close()
    p.wait()
    return out


def render_video(tl, st, workdir, out_mp4, procs=4, log=print):
    segs = []
    jobs = []
    for si in range(len(tl["scenes"])):
        seg = os.path.join(workdir, f"seg_{si:03d}.mp4")
        segs.append(seg)
        jobs.append((si, tl, st, seg))
    with Pool(procs) as pool:
        for k, _ in enumerate(pool.imap_unordered(_render_scene, jobs)):
            log(f"  장면 렌더 {k + 1}/{len(jobs)}")
    lst = os.path.join(workdir, "segs.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    silent = os.path.join(workdir, "video_silent.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    mixwav = os.path.join(workdir, "mix.wav")
    A.mix(os.path.join(workdir, "voice.wav"), os.path.join(workdir, "sfx.wav"), os.path.join(workdir, "bgm.wav"), mixwav, st)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", mixwav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{tl['total']:.3f}",
                    "-movflags", "+faststart", out_mp4], check=True)
    return out_mp4


def write_srt(tl, path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out, k = [], 1
    for sc in tl["scenes"]:
        for c in sc["chunks"]:
            out.append(f"{k}\n{ts(c['start'])} --> {ts(c.get('show_end', c['end']))}\n{strip_markup(c['text'])}\n")
            k += 1
    open(path, "w", encoding="utf-8").write("\n".join(out))


def preflight(project, st):
    """렌더 전 대본 검사: 자막 오타 의심, 글리프 누락, 규칙 위반."""
    issues = []
    for si, sc in enumerate(project["scenes"]):
        say = sc.get("say", [])
        for sent in ([say] if isinstance(say, str) else say):
            for ck in split_chunks(sent, st["subtitle"]["max_chars_per_line"], st["subtitle"]["max_lines"]):
                for i in lint_subtitle(ck):
                    issues.append(f"장면{si} 자막 '{strip_markup(ck)}': {i}")
                mg = missing_glyphs(st["subtitle"]["font"], strip_markup(ck))
                if mg:
                    issues.append(f"장면{si} 자막 글꼴에 없는 글자 {mg}")
        if sc.get("type") in ("headline", "image") and not sc.get("source"):
            issues.append(f"장면{si} 자료화면인데 출처(source) 없음")
    return issues
