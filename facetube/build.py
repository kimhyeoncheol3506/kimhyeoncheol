"""대본(YAML) -> 타임라인 -> 프레임 렌더 -> 오디오 믹스 -> mp4."""
import copy
import re
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
from .textnorm import split_chunks, wrap_lines, emphasis_spans, strip_markup, lint_subtitle, to_speech

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
        # 자막: 목소리 시작 +start_delay 에 뜨고, 다음 덩어리 직전(또는 말 끝 +end_hold)까지 유지
        sd = st["subtitle"].get("start_delay", 0.0)
        for c in chunks:
            c["show_start"] = c["start"] + sd
        for a, b in zip(chunks, chunks[1:]):
            a["show_end"] = b["start"] + sd
        if chunks:
            chunks[-1]["show_end"] = chunks[-1]["end"] + st["subtitle"].get("end_hold", 0.15)
        t = max(t, sc["start"] + sc.get("min_dur", 0))
        t += sc.get("hold", 0)
        sc["chunks"] = chunks
        scenes.append(sc)
    # 장면 끝 = 다음 장면 시작
    for a, b in zip(scenes, scenes[1:]):
        a["end"] = b["start"]
    scenes[-1]["end"] = t + scenes[-1].get("tail", 0.6)
    total = scenes[-1]["end"]

    # 외부 소재(clip): 장면 길이가 정해진 뒤 프레임으로 푼다
    from .media import prep_frames
    base = project.get("_dir", ".")
    for sc in scenes:
        if sc["type"] != "clip":
            continue
        md = sc.get("media") or {}
        if not md.get("path"):
            raise SystemExit(f"장면{sc['index']}: type: clip 인데 media.path 가 없음")
        src = os.path.join(base, md["path"]) if not os.path.isabs(md["path"]) else md["path"]
        if not os.path.exists(src):
            src = os.path.join(ROOT, md["path"])
        fdir = os.path.join(workdir, "media", f"s{sc['index']}")
        info = prep_frames(src, fdir, 1500, 690, sc["end"] - sc["start"], st["video"]["fps"], md.get("start", 0.0), md.get("loop", True))
        info["dir_abs"] = fdir
        sc["media_info"] = info
        if md.get("ai") and md.get("badge", True):
            sc["badge"] = md.get("badge_text") or f"AI 생성 · {md.get('tool', '')}".strip(" ·")
        if md.get("ai") and not sc.get("source"):
            sc["source"] = f"AI 생성 영상: {md.get('tool', '')} {md.get('model', '')}".strip()

    # 효과음 자동 배치(규칙집 §5)
    for sc in scenes:
        s0 = sc["start"]
        # 장면 전환 휙(whoosh)은 잦으면 안 된다 → 챕터 전환(chapter: true)과 3장면에 1번만
        if sc["index"] > 0 and (sc.get("chapter") or sc.get("whoosh") or sc["index"] % 3 == 0):
            sfx_events.append((max(0, s0 - 0.12), "whoosh", -3))
        if sc.get("big"):
            sfx_events.append((s0 + _chunk_off(sc, sc.get("big_at", 0)), "pop", 0))
        if sc["type"] == "number":
            ra = s0 + _chunk_off(sc, sc.get("reveal_at", 0))
            n = 4          # 숫자 굴림 tick 은 4개로(8개 연타는 '다닥다닥'이라는 피드백)
            for k in range(n):
                sfx_events.append((ra + 0.05 + sc.get("count_sec", 0.8) * (k / n) ** 0.6, "tick", -10))
            sfx_events.append((ra + 0.05 + sc.get("count_sec", 0.8), sc.get("hit_sfx", "boom"), -2))
        if sc["type"] == "headline" and sc.get("highlight"):
            sfx_events.append((s0 + _chunk_off(sc, sc.get("highlight_at", 1)), "swish", -4))
        if sc["type"] == "compare":
            sfx_events.append((s0 + _chunk_off(sc, sc["items"][-1].get("at", 0)), "pop", -6))   # 막대: 주인공(마지막 항목) 등장에만
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
            if p.get("sfx", False):      # 소품 pop 은 명시한 것만(모션이 뜰 때마다 넣지 않는다)
                sfx_events.append((s0 + _chunk_off(sc, p.get("at", 0)), "pop", -10))
        for e in sc.get("sfx", []):
            sfx_events.append((s0 + _chunk_off(sc, e.get("at", 0)) + e.get("offset", 0), e["name"], e.get("db", 0)))

    sfx_events = thin_sfx(sfx_events, st["rules"].get("sfx_min_gap_sec", 0.35))

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


SFX_PRIORITY = {"boom": 5, "tada": 5, "ding": 4, "click": 4, "whoosh": 3, "swish": 3, "pop": 2, "tick": 1}


def thin_sfx(events, min_gap):
    """같은 시각 중복 제거, 최소 간격(min_gap) 안에 겹치면 우선순위가 낮은 소리를 뺀다.
    tick 은 서로 간격이 좁은 게 정상(카운트업)이라 tick끼리는 예외."""
    ev = sorted(set((round(t, 2), n, db) for t, n, db in events))
    keep = []
    for t, n, db in ev:
        if keep:
            pt, pn, pdb = keep[-1]
            if t - pt < min_gap and not (n == "tick" and pn == "tick"):
                if SFX_PRIORITY.get(n, 0) > SFX_PRIORITY.get(pn, 0):
                    keep[-1] = (t, n, db)
                continue
        keep.append((t, n, db))
    return keep


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
        if c.get("show_start", c["start"]) <= t_global < c.get("show_end", c["end"]):
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


def rule_check(tl, st, fmt="longform"):
    """숫자로 쓴 규칙(style.yaml rules:) 위반을 찾는다. 위반 목록(문자열)을 돌려준다."""
    R, out = st.get("rules", {}), []
    total = tl["total"]
    # 효과음 밀도: 분당 개수 + 최소 간격
    ts = sorted(t for t, n in tl["sfx"] if n != "tick")
    per_min = (len(ts) + (1 if any(n == "tick" for _, n in tl["sfx"]) else 0)) / max(total, 1) * 60
    cap = R.get("sfx_max_per_min", 99)
    cap = cap.get(fmt, cap.get("longform", 99)) if isinstance(cap, dict) else cap
    if per_min > cap:
        out.append(f"효과음이 너무 많음: 분당 {per_min:.1f}개 (상한 {cap}, {fmt}). 장면 전환 whoosh·소품 pop 을 줄이세요")
    tight = [(a, b) for a, b in zip(ts, ts[1:]) if b - a < R.get("sfx_min_gap_sec", 0)]
    if tight:
        out.append(f"효과음이 다닥다닥: {len(tight)}곳이 {R['sfx_min_gap_sec']}초 이내 (예: {tight[0][0]:.2f}s~{tight[0][1]:.2f}s)")
    # 내레이션 속도(음절/초) — 말하는 구간만
    lo, hi = R.get("syllables_per_sec", [0, 99])
    syl = dur = 0.0
    for sc in tl["scenes"]:
        for c in sc["chunks"]:
            syl += len(re.findall("[가-힣]", to_speech(c["text"])))
            dur += c["end"] - c["start"]
    if dur:
        v = syl / dur
        if not lo <= v <= hi:
            out.append(f"내레이션 속도 {v:.1f}음절/초 (권장 {lo}~{hi}). voice.speed 를 {'올리' if v < lo else '내리'}세요")
    # 같은 구도 10초 초과
    for sc in tl["scenes"]:
        if sc["end"] - sc["start"] > R.get("same_layout_max_sec", 99):
            out.append(f"장면{sc['index']}({sc['type']}) 가 {sc['end'] - sc['start']:.1f}초: 같은 구도로 {R['same_layout_max_sec']}초 초과 — 장면을 나누세요")
    # 가짜 숫자 금지: 숫자를 보여주는 장면은 source 필요
    if R.get("no_fake_numbers"):
        for sc in tl["scenes"]:
            if sc["type"] in ("number", "compare") and not sc.get("source"):
                out.append(f"장면{sc['index']}: 숫자 장면인데 source(출처) 없음 — 꾸민 숫자 금지")
    # AI 소재(외부 사이트) 기록·약관·표시
    from .media import ai_issues
    out += ai_issues([(f"장면{sc['index']}", sc.get("media"), sc.get("media_info")) for sc in tl["scenes"] if sc["type"] == "clip"], st)
    # 첫 20초 안에 질문
    by = R.get("intro_question_by_sec")
    if by:
        head = " ".join(c["text"] for sc in tl["scenes"] for c in sc["chunks"] if c["start"] < by)
        if "?" not in head and "까요" not in head and "나요" not in head:
            out.append(f"첫 {by}초 안에 영상이 답할 질문이 없음")
    return out


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
        if sc.get("type") == "clip" and not (sc.get("media") or {}).get("path"):
            issues.append(f"장면{si} 외부 소재(clip)인데 media.path 없음")
        if sc.get("type") in ("headline", "image") and not sc.get("source"):
            issues.append(f"장면{si} 자료화면인데 출처(source) 없음")
    return issues
