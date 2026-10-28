#!/usr/bin/env python3
"""쇼츠 공장: "공장이 지키는 원칙" 6가지를 코드로 지키며 40~50초 세로 쇼츠를 만든다.

  python shorts/make_short.py projects/<이름>_short.yaml
원칙 → 구현
  01 소재는 오늘에서   topic.kind/published 점검(뉴스는 72시간 안). 소재 5개 고르는 절차는 스킬 문서
  02 40~50초, 줄마다 할 일  beats[].role = hook·twist·core·pov·todo·end, 길이·순서·core 연속 점검
  03 아래 18%는 비운다   장면을 찍을 때마다 내용을 숨긴 배경과 픽셀 비교(shorts/render_lib.py)
  04 자막은 목소리에 맞춰 문장별 음성인식 시각으로 조각을 맞추고 13자 안팎으로 나눔(facetube/captions.py)
  05 내 관점 한 줄은 꼭  role: pov 필수, 보고서에 '직접 손볼 것'으로 표시
  06 출처에 없는 숫자는 안 쓴다  sources[].facts 에 없는 숫자는 경고, verified: true(원문 확인)만 인정, 설명란 출처 자동 작성
"""
import argparse, datetime, hashlib, json, math, os, re, shutil, subprocess, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from facetube import audio as A, qc                       # noqa: E402
from facetube.build import load_style, thin_sfx           # noqa: E402
from facetube.captions import split_pieces, align_pieces  # noqa: E402
from facetube.media import prep_frames, ai_issues                  # noqa: E402
from facetube.textnorm import strip_markup, lint_subtitle, to_speech, COMMON_TYPOS  # noqa: E402
from facetube.voice import Voice                          # noqa: E402
from render_lib import render_scene                       # noqa: E402

FPS = 30
HTML = Path(__file__).resolve().parent / "scene.html"


# ----------------------------------------------------------------------------- 대본 사전 처리
def autocorrect(proj, log):
    fixes = []
    for b in proj["beats"]:
        o = b["say"]
        for bad, good in COMMON_TYPOS.items():
            if not good.endswith("확인") and bad in b["say"]:
                b["say"] = b["say"].replace(bad, good)
        if b["say"] != o:
            fixes.append(f"'{o}' → '{b['say']}'")
            log("  자동 교정: " + fixes[-1])
    return fixes


def sentences(text):
    return [x for x in re.split(r"(?<=[.?!])\s+", text.strip()) if x]


def resolve_at(spec, caps, bstart):
    """sync.at 의 문자열은 '그 말이 나오는 자막 조각의 시작 시각(장면 기준 초)'으로 바꾼다."""
    out = []
    for v in spec:
        if isinstance(v, (int, float)):
            out.append(float(v))
            continue
        hit = next((c for c in caps if v in c["html"]), None)
        out.append(round(max(0.0, hit["t0"] - bstart - 0.05), 2) if hit else 0.0)
    return out


# ----------------------------------------------------------------------------- 타임라인(음성·자막)
def build_timeline(proj, st, work, voice, log):
    S = st["shorts"]
    (work / "tts").mkdir(parents=True, exist_ok=True)
    t, beats, vparts, tts, sfx_ev = 0.0, [], [], [], []
    for bi, b in enumerate(proj["beats"]):
        bstart = t
        t += 0.15
        rows, caps = [], []
        for sent in sentences(b["say"]):
            key = hashlib.md5(f"{voice.backend}|{voice.voice}|{voice.speed}|{sent}".encode()).hexdigest()[:16]
            wav = work / "tts" / (key + ".wav")
            meta = Path(str(wav) + ".json")
            if wav.exists() and meta.exists():
                x, _ = sf.read(wav, dtype="float32")
                info = json.load(open(meta, encoding="utf-8"))
            else:
                x, info = voice.say(sent)
                sf.write(wav, x, A.SR)
                json.dump(info, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
            dur = len(x) / A.SR
            pieces = split_pieces(sent, S["caption_max_chars"], S["caption_hard_max"])
            span = align_pieces(x, A.SR, pieces)
            for p, (a, e) in zip(pieces, span):
                caps.append({"t0": t + a, "t1": t + e, "html": p})
            rows.append({"text": sent, "start": t, "end": t + dur})
            vparts.append((t, x))
            tts.append({"scene": bi, "text": strip_markup(sent), **info, "start": round(t, 2), "dur": round(dur, 2)})
            log(f"  [{bi}:{b['role']}] {strip_markup(sent)}  ({dur:.2f}s, CER {info.get('cer')}, 시도 {info.get('tries')})")
            t += dur + 0.2
        t = t - 0.2 + 0.4
        dur_b = max(2.6, t - bstart)
        dur_b = math.ceil(dur_b * FPS) / FPS                 # 프레임 단위로 맞춤
        t = bstart + dur_b
        for k in range(len(caps) - 1):                         # 자막은 다음 조각 시작까지 이어서
            caps[k]["t1"] = caps[k + 1]["t0"]
        caps[-1]["t1"] = bstart + dur_b
        beats.append({"index": bi, "role": b["role"], "start": bstart, "end": t, "dur": dur_b, "rows": rows,
                      "caps": caps, "scene": b["scene"], "source": b.get("source"), "sync": b.get("sync", {}),
                      "media": b.get("media")})
        t += 0.0
    total = t
    # 장면 데이터 + 효과음(종류별 최소한만)
    for b in beats:
        d = dict(b["scene"])
        spec = b["sync"].get("at")
        if spec:
            d["at"] = resolve_at(spec, b["caps"], b["start"])
        d["captions"] = [{"t0": round(c["t0"] - b["start"], 3), "t1": round(c["t1"] - b["start"], 3), "html": c["html"]} for c in b["caps"]]
        if b["source"]:
            d["source"] = b["source"]
        if d.get("kind") == "clip":                            # 외부에서 만든 영상·이미지 소재
            md = b["media"]
            if not md:
                raise SystemExit(f"장면{b['index']}: kind: clip 인데 media 가 없음")
            src = Path(md["path"])
            if not src.is_absolute():
                src = next((c for c in (Path(proj["_dir"]) / src, ROOT / src) if c.exists()), Path(proj["_dir"]) / src)
            fdir = Path(__file__).resolve().parent / "_media" / f"{proj['slug']}_b{b['index']}"
            m = prep_frames(src, fdir, 900, 1000, b["dur"], FPS, md.get("start", 0.0), md.get("loop", True))
            m["dir"] = f"_media/{proj['slug']}_b{b['index']}"
            d["media"] = m
            b["media_info"] = m
            if md.get("ai") and md.get("badge", True):
                d["badge"] = md.get("badge_text") or f"AI 생성 · {md.get('tool', '')}".strip(" ·")
            if md.get("ai") and not b["source"]:
                b["source"] = f"AI 생성 영상: {md.get('tool', '')} {md.get('model', '')}".strip()
                d["source"] = b["source"]
        b["data"] = d
        at = d.get("at") or []
        s0, kind = b["start"], d.get("kind")
        if kind == "hook":
            sfx_ev.append((s0 + 0.3, "pop", -4))
        if kind == "number":
            ra = s0 + (at[1] if len(at) > 1 else 0.5)
            for k in range(4):
                sfx_ev.append((ra + 0.05 + d.get("roll", 1.2) * (k / 4) ** 0.6, "tick", -10))
            sfx_ev.append((ra + 0.05 + d.get("roll", 1.2), "boom" if b["index"] == 0 else "ding", -3))
        if kind == "reveal":
            sfx_ev.append((s0 + (at[1] if len(at) > 1 else 0.4), "boom", -3))
        if kind == "list" and b["role"] not in ("end",):
            sfx_ev.append((s0 + (at[1] if len(at) > 1 else 0.6), "pop", -6))
        if b["role"] == "pov":
            sfx_ev.append((s0 + 0.1, "swish", -4))
        if b["role"] == "end":
            sfx_ev.append((s0 + 0.5, "ding", -6))
    sfx_ev = thin_sfx(sfx_ev, st["rules"].get("sfx_min_gap_sec", 0.35))
    # 오디오
    n = int(math.ceil(total * A.SR)) + A.SR
    v, sx = np.zeros(n, np.float32), np.zeros(n, np.float32)
    for s0, x in vparts:
        A.place(v, x, s0)
    for s0, name, db in sfx_ev:
        A.place(sx, A.sfx(name), s0, db)
    A.write(str(work / "voice.wav"), v)
    A.write(str(work / "sfx.wav"), sx)
    A.write(str(work / "bgm.wav"), A.make_bgm(proj, n / A.SR, 108))
    return {"beats": beats, "total": total, "tts": tts, "sfx": [(round(a, 2), b_) for a, b_, _ in sfx_ev]}


# ----------------------------------------------------------------------------- 렌더
def _render_beat(args):
    i, data, dur, out, empty = args
    return i, render_scene(HTML, data, dur, out, FPS, empty_ratio=empty)


def render(tl, st, work, out_mp4, procs, log):
    S = st["shorts"]
    jobs = [(b["index"], b["data"], b["dur"], str(work / f"seg_{b['index']:02d}.mp4"), S["bottom_empty_ratio"]) for b in tl["beats"]]
    viol = {}
    with Pool(procs) as pool:
        for k, (i, v) in enumerate(pool.imap_unordered(_render_beat, jobs)):
            viol[i] = v
            log(f"  장면 렌더 {k + 1}/{len(jobs)} (아래 18% {'✅' if not v else '⚠ ' + str(v[:2])})")
    lst = work / "segs.txt"
    lst.write_text("".join(f"file '{j[3]}'\n" for j in jobs))
    silent = work / "video_silent.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)], check=True)
    A.mix(str(work / "voice.wav"), str(work / "sfx.wav"), str(work / "bgm.wav"), str(work / "mix.wav"), st)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(work / "mix.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{tl['total']:.3f}", "-movflags", "+faststart", str(out_mp4)], check=True)
    return viol


# ----------------------------------------------------------------------------- 원칙 점검
def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in ("captions", "at", "kind"):
                continue
            yield from _strings(v)
            if k in ("to", "from") and isinstance(v, (int, float)):
                yield str(int(v)) if float(v).is_integer() else str(v)
    elif isinstance(o, list):
        for v in o:
            yield from _strings(v)


def check_rules(proj, st, tl, viol, fmt):
    S, R, out = st["shorts"], st["rules"], []
    # 01 소재
    tp = proj.get("topic", {})
    if tp.get("kind") == "news":
        try:
            age = (datetime.datetime.now() - datetime.datetime.fromisoformat(str(tp["published"]))).total_seconds() / 3600
            if age > S["topics"]["news_window_hours"]:
                out.append(f"[01] 뉴스 소재가 {age:.0f}시간 전 것 (기준 {S['topics']['news_window_hours']}시간 이내). 오래 가는 원리형(topic.kind: evergreen)으로 바꾸거나 최신 소재로")
        except Exception:
            out.append("[01] topic.published 날짜가 없거나 형식이 틀림(YYYY-MM-DD)")
    elif tp.get("kind") != "evergreen":
        out.append("[01] topic.kind 를 news 또는 evergreen 으로 적어 주세요")
    # 02 길이·역할
    lo, hi = S["concept_sec"] if fmt == "concept" else S["duration_sec"]
    if not lo <= tl["total"] <= hi:
        out.append(f"[02] 길이 {tl['total']:.1f}초 (기준 {lo}~{hi}초, {fmt})")
    roles = [b["role"] for b in tl["beats"]]
    order = S["roles"]
    if roles[0] != "hook" or roles[-1] != "end":
        out.append("[02] 첫 줄은 hook, 마지막 줄은 end 여야 함")
    firsts = [roles.index(r) for r in order if r in roles]
    if len(firsts) < len(order):
        out.append(f"[02] 빠진 역할: {', '.join(r for r in order if r not in roles)}")
    elif firsts != sorted(firsts):
        out.append("[02] 역할 순서가 hook→twist→core→pov→todo→end 가 아님")
    if S.get("no_adjacent_core") and any(a == b == "core" for a, b in zip(roles, roles[1:])):
        out.append("[02] 설명(core)만 두 줄 이어짐: 사이에 반전·화면 전환을 넣으세요")
    # 03 아래 18%
    bad = [(i, v) for i, v in viol.items() if v]
    for i, v in sorted(bad):
        out.append(f"[03] 장면{i} 아래 {int(S['bottom_empty_ratio'] * 100)}% 침범: {v[0][0]}초 등 {len(v)}곳")
    # 04 자막 길이
    lens = [len(strip_markup(c["html"])) for b in tl["beats"] for c in b["caps"]]
    over = [l for l in lens if l > S["caption_hard_max"]]
    if over:
        out.append(f"[04] 자막 {len(over)}개가 {S['caption_hard_max']}자 초과")
    med = float(np.median(lens)) if lens else 0
    if med > S["caption_max_chars"] + 1:
        out.append(f"[04] 자막 길이 중앙값 {med:.0f}자 (13자 안팎이어야 함)")
    # 05 내 관점
    pov = [b for b in tl["beats"] if b["role"] == "pov"]
    if S["require_pov"] and (not pov or len(strip_markup(" ".join(r["text"] for r in pov[0]["rows"]))) < 8):
        out.append("[05] 내 관점(pov) 줄이 없음")
    # 06 출처·숫자
    srcs = proj.get("sources", [])
    facts = " ".join(f for s in srcs for f in s.get("facts", [])).replace(",", "")
    allow = {str(x) for x in proj.get("numbers_ok", [])}
    unk = set()
    for b in tl["beats"]:
        for text in [strip_markup(b["data"].get("_say", "")), *(r["text"] for r in b["rows"]), *_strings(b["scene"])]:
            for n_ in re.findall(r"\d[\d,]*(?:\.\d+)?", strip_markup(text)):
                n_ = n_.replace(",", "")
                if n_ not in facts and n_ not in allow:
                    unk.add(n_)
    if unk:
        out.append(f"[06] 출처 facts 에 없는 숫자: {', '.join(sorted(unk))} (sources[].facts 에 근거를 적거나 numbers_ok 로 사유를 남기세요)")
    if S.get("sources_verified"):
        nv = [s.get("id", "?") for s in srcs if not s.get("verified")]
        if nv or not srcs:
            out.append(f"[06] 원문을 열어 확인하지 않은 출처: {', '.join(nv) if nv else '출처 없음'}")
    for b in tl["beats"]:
        if re.search(r"\d", " ".join(r["text"] for r in b["rows"])) and not b["source"] and b["data"].get("kind") in ("number", "list", "reveal"):
            out.append(f"[06] 장면{b['index']}: 숫자 장면에 화면 출처 표기(source) 없음")
    # AI 소재(외부 사이트): 기록, 약관 확인, 표시
    out += ai_issues([(f"장면{b['index']}", b.get("media"), b.get("media_info")) for b in tl["beats"]]
                     + ([("배경음", {**proj["bgm"], "ai": True}, None)] if (proj.get("bgm") or {}).get("path") else []), st)
    # 속도·효과음
    syl = sum(len(re.findall("[가-힣]", to_speech(r["text"]))) for b in tl["beats"] for r in b["rows"])   # 숫자도 소리 기준으로
    spk = sum(r["end"] - r["start"] for b in tl["beats"] for r in b["rows"])
    v_ = syl / max(spk, 0.1)
    lo_, hi_ = R["syllables_per_sec"]
    if not lo_ <= v_ <= hi_:
        out.append(f"내레이션 속도 {v_:.1f}음절/초 (권장 {lo_}~{hi_})")
    per_min = len([1 for _, n in tl["sfx"] if n != "tick"]) / tl["total"] * 60
    cap = R["sfx_max_per_min"]["short"]
    if per_min > cap:
        out.append(f"효과음 분당 {per_min:.0f}개 (상한 {cap})")
    return out, v_


def write_outputs(proj, tl, out_dir, rep, violations, pov_line, fixes, speed):
    # SRT(자막 조각 단위)
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    rows, k = [], 1
    for b in tl["beats"]:
        for c in b["caps"]:
            rows.append(f"{k}\n{ts(c['t0'])} --> {ts(c['t1'])}\n{strip_markup(c['html'])}\n")
            k += 1
    (out_dir / "subtitles.srt").write_text("\n".join(rows), encoding="utf-8")
    # 설명란(원칙 06: 출처를 남긴다)
    L = [f"# {proj['title']}", "", proj.get("summary", "").strip(), "", f"내 관점: {pov_line}", "", "▬ 출처 (원문을 열어 확인함)" if all(s.get("verified") for s in proj.get("sources", [])) else "▬ 출처 (⚠ 원문 미확인 포함)"]
    for s in proj.get("sources", []):
        L.append(f"· {s['outlet']} 「{s['title']}」 {s['date']} {s['url']}" + (f"  ※ {s['note']}" if s.get("note") else ""))
    ai = [(b["index"], b["media"]) for b in tl["beats"] if b.get("media") and b["media"].get("ai")]
    bg = proj.get("bgm") or {}
    if ai or bg.get("path"):
        L += ["", "▬ AI 생성 소재"] + [f"· 장면{i}: {m.get('tool')} ({m.get('model')}), {m.get('generated_on')}" for i, m in ai]
        if bg.get("path"):
            L.append(f"· 배경음악: {bg.get('tool')} ({bg.get('model')}), {bg.get('generated_on')}")
    L += ["", " ".join(proj.get("tags", [])), "", f"(자동 생성: 확인일 {datetime.date.today()})"]
    (out_dir / "description.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out")
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--no-qc", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    st = load_style()
    proj = yaml.safe_load(open(a.project, encoding="utf-8"))
    fmt = proj.get("format", "short")
    name = proj.get("slug") or Path(a.project).stem
    proj["slug"] = name
    proj["_dir"] = str(Path(a.project).resolve().parent)
    out = Path(a.out) if a.out else ROOT / "output" / name
    work = out / "_work"
    work.mkdir(parents=True, exist_ok=True)
    log = lambda m: print(m, flush=True)
    log("① 대본 사전검사")
    fixes = autocorrect(proj, log)
    vc = proj.get("voice", {})
    voice = Voice(backend=vc.get("backend", "auto"), voice=vc.get("name"), speed=vc.get("speed", 1.5), cer_retry=st["qc"]["asr_cer_retry"])
    log(f"② 음성 더빙({voice.backend}) + 음성인식 대조 + 자막 13자 조각·시각 맞추기")
    tl = build_timeline(proj, st, work, voice, log)
    log(f"   총 {tl['total']:.1f}초, 장면 {len(tl['beats'])}개, 자막 조각 {sum(len(b['caps']) for b in tl['beats'])}개")
    log("③ 렌더링 (장면마다 아래 18% 픽셀 검사)")
    mp4 = out / "final.mp4"
    viol = render(tl, st, work, mp4, a.procs, log)
    violations, spd = check_rules(proj, st, tl, viol, fmt)
    for v in violations:
        log("  ⚠ " + v)
    pov = next((b for b in tl["beats"] if b["role"] == "pov"), None)
    pov_line = " ".join(strip_markup(r["text"]) for r in pov["rows"]) if pov else ""
    rep = None
    if not a.no_qc:
        log("④ 품질검수")
        qtl = {"scenes": [{"index": b["index"], "type": b["scene"].get("kind"), "start": b["start"], "end": b["end"], "source": b["source"],
                           "chunks": [{"text": r["text"], "start": r["start"], "end": r["end"]} for r in b["rows"]]} for b in tl["beats"]],
               "total": tl["total"], "tts": tl["tts"], "sfx": tl["sfx"], "fps": FPS}
        rep = qc.run_qc(str(mp4), qtl, st, str(work), None, log=log)
        md = qc.report_md(rep, qtl, st)
        md += "\n## 쇼츠 공장 원칙 점검 (01~06)\n" + ("\n".join(f"- ⚠️ {v}" for v in violations) if violations else "- ✅ 위반 없음") + "\n"
        md += f"\n- 내레이션 속도 {spd:.1f}음절/초, 효과음 {len(tl['sfx'])}개\n"
        if any(b.get("media") and b["media"].get("ai") for b in tl["beats"]):
            md += "\n## AI 생성 소재 안내\n- 업로드할 때 YouTube Studio 에서 '변경되거나 합성된 콘텐츠' 표시를 확인하세요(현실처럼 보이는 AI 영상이면 공개해야 함).\n- 화면 배지는 영상에 포함되어 있습니다. 도구가 넣은 워터마크를 가리거나 지우지 마세요.\n"
        md += f"\n## 내 관점 줄 (원칙 05 — 현철님이 직접 손봐 주세요)\n> {pov_line}\n"
        if fixes:
            md += "\n## 대본 자동 교정\n" + "\n".join(f"- {f}" for f in fixes) + "\n"
        (out / "qc_report.md").write_text(md, encoding="utf-8")
        if rep.get("sheet"):
            shutil.copy(rep["sheet"], out / "contact_sheet.png")
        print(md)
    write_outputs(proj, tl, out, rep, violations, pov_line, fixes, vc.get("speed", 1.5))
    log(f"완료: {mp4} ({time.time() - t0:.0f}초 소요)")


if __name__ == "__main__":
    main()
