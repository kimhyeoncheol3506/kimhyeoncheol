#!/usr/bin/env python3
"""에디토리얼 롱폼: '종이 인포그래픽 + 차분한 해설' 가로 영상(참고: 미주일기, docs/참고분석_미주일기.md).

  python editorial/make_editorial.py projects/<이름>.yaml            # → output/<이름>/final.mp4
  python editorial/make_editorial.py projects/<이름>.yaml --stills   # 장면마다 마지막 그림만 빨리 찍어 보기

대본 YAML: scenes[] 마다 say(내레이션) + scene(kind 와 값) + sync.at(요소가 등장할 낱말) + source(화면 출처).
장면 종류는 editorial/scene.html 머리말. 자막은 문장 통째로 아래 가운데 어두운 띠에 뜨고,
요소는 sync.at 낱말을 말하는 순간 하나씩 쌓인다. 숫자 점검(출처 facts)·설명란·챕터 목록은 쇼츠 공장과 같은 원칙.
"""
import argparse, datetime, hashlib, json, math, os, re, shutil, subprocess, sys, time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "shorts"))
from facetube import audio as A, qc                       # noqa: E402
from facetube.build import load_style, thin_sfx           # noqa: E402
from facetube.captions import split_pieces, align_pieces  # noqa: E402
from facetube.textnorm import strip_markup, to_speech     # noqa: E402
from facetube.voice import Voice, PROSODY                 # noqa: E402
from make_short import autocorrect, sentences, _strings   # noqa: E402
from render_lib import render_scene                       # noqa: E402

HTML = Path(__file__).resolve().parent / "scene.html"
NUMERIC = {"bars", "waffle", "line", "gauge", "bignum", "stairs"}


def apply_style(st, proj):
    """대본의 style:(paper·neon …) 값을 editorial: 기본값 위에 덮어쓴다(docs/스타일_라이브러리.md)."""
    name = proj.get("style", "paper")
    ov = (st.get("styles") or {}).get(name)
    if ov is None:
        raise SystemExit(f"style '{name}' 이 style.yaml styles: 에 없음")
    E = dict(st["editorial"])
    for k, v in ov.items():
        E[k] = {**E[k], **v} if isinstance(v, dict) and isinstance(E.get(k), dict) else v
    st["editorial"] = E
    return E


def _resolve_at(spec, words, s0):
    """sync.at 의 낱말 → 그 낱말을 말하기 시작한 시각(장면 기준 초). 숫자는 그대로."""
    out, cursor = [], 0
    for v in spec:
        if isinstance(v, (int, float)):
            out.append(float(v))
            continue
        hit = next((k for k in range(cursor, len(words)) if v in words[k][1]), None)
        if hit is None:
            hit = next((k for k in range(len(words)) if v in words[k][1]), None)
        if hit is None:
            raise SystemExit(f"sync.at 낱말 '{v}' 이 대본에 없음")
        cursor = hit
        out.append(round(max(0.0, words[hit][0] - s0 - 0.05), 2))
    return out


def build_timeline(proj, st, work, voice, log):
    E = st["editorial"]
    fps = E["video"]["fps"]
    (work / "tts").mkdir(parents=True, exist_ok=True)
    t, scenes, vparts, tts = 0.0, [], [], []
    base_ins = voice.instruct
    for si, sc in enumerate(proj["scenes"]):
        s0 = t
        voice.instruct = sc.get("instruct") or base_ins        # 장면별 톤·강약(후킹은 힘주어, 정리는 차분하게)
        ik = f"|{voice.instruct}" if sc.get("instruct") else ""
        t += E["scene_lead"]
        rows, caps, words = [], [], []
        # Voicebox(여의도여자)는 장면 대사를 한 번에 읽혀 문장끼리 억양이 이어지게 한다(문장마다 끊어 만들면 매번 처음 톤으로 돌아가 기계처럼 들림)
        units = [sc["say"].strip()] if voice.backend == "voicebox" else sentences(sc["say"])
        for unit in units:
            pv = json.dumps(PROSODY, sort_keys=True) if voice.backend == "voicebox" else ""
            key = hashlib.md5(f"{voice.backend}|{voice.voice}|{voice.speed}|{pv}|{unit}|{to_speech(unit)}{ik}".encode()).hexdigest()[:16]   # 읽기 규칙이 바뀌면 다시 만든다
            wav, meta = work / "tts" / (key + ".wav"), work / "tts" / (key + ".json")
            if wav.exists() and meta.exists():
                x, _ = sf.read(wav, dtype="float32")
                info = json.load(open(meta, encoding="utf-8"))
            else:
                x, info = voice.say(unit)
                sf.write(wav, x, A.SR)
                json.dump(info, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
            dur = len(x) / A.SR
            ws = strip_markup(unit).split()
            spans = align_pieces(x, A.SR, ws)                     # 낱말마다 시작 시각(음성인식 기준)
            words += [(t + a, w) for w, (a, _) in zip(ws, spans)]
            k = 0
            sents = sentences(unit)
            for j, sent in enumerate(sents):                      # 문장마다 자막 조각·구간
                k0 = k
                for p in split_pieces(strip_markup(sent), E["caption_max_chars"], E["caption_hard_max"]):
                    caps.append({"t0": t + spans[k][0], "text": p})
                    k += len(p.split())
                a0 = spans[k0][0]
                a1 = spans[k][0] - 0.1 if j + 1 < len(sents) else dur
                rows.append({"text": sent, "start": t + a0, "end": t + max(a0 + 0.3, a1)})
            vparts.append((t, x))
            tts.append({"scene": si, "text": strip_markup(unit), **info, "start": round(t, 2), "dur": round(dur, 2)})
            log(f"  [{si}:{sc['scene']['kind']}] {strip_markup(unit)}  ({dur:.2f}s, CER {info.get('cer')})")
            t += dur + E["gap_sentence"]
        t = t - E["gap_sentence"] + E["scene_tail"]
        dur_s = math.ceil(max(E["scene_min_sec"], sc.get("hold", 0), t - s0) * fps) / fps     # hold: 끝 화면처럼 말 없이 길게 둘 때
        t = s0 + dur_s
        for k in range(len(caps)):                              # 자막은 다음 조각(또는 다음 문장 시작 전 말 끝 +0.2초)까지
            nxt = caps[k + 1]["t0"] if k + 1 < len(caps) else None
            end_row = next((r["end"] for r in rows if r["start"] <= caps[k]["t0"] < r["end"] + 0.01), t)
            hold = end_row + 0.2
            caps[k]["t1"] = (nxt if nxt - hold < 0.6 else hold) if nxt is not None else min(t, hold)   # 문장 사이 짧은 틈엔 자막을 이어 둔다(깜빡임 방지)
        d = dict(sc["scene"])
        if sc.get("sync", {}).get("at"):
            d["at"] = _resolve_at(sc["sync"]["at"], words, s0)
        if sc.get("sync", {}).get("beats"):                     # 강조 맥박: 새 요소 없이 긴 문장일 때 [[강조]] 글자가 이 낱말에 반짝
            d["beats"] = _resolve_at(sc["sync"]["beats"], words, s0)
        gap_max = proj.get("auto_beats")                         # 2026-11-04: 긴 영상용 — 새 요소도 맥박도 없는 틈이 이보다 길면 가운데 낱말에 맥박을 자동으로
        if gap_max:
            ws = [round(w0 - s0, 2) for w0, _ in words]
            dur_guess = (ws[-1] + 1.0) if ws else 0
            ev = sorted({0.0, *[float(x) for x in d.get("at", [])], *[float(x) for x in d.get("beats", [])], dur_guess})
            add = []
            for x0, x1 in zip(ev, ev[1:]):
                n = int((x1 - x0) // gap_max)
                for k in range(1, n + 1):
                    tgt = x0 + (x1 - x0) * k / (n + 1)
                    cand = [w for w in ws if x0 + 0.6 < w < x1 - 0.6]
                    if cand:
                        add.append(min(cand, key=lambda w: abs(w - tgt)))
            if add:
                d["beats"] = sorted(set(d.get("beats", []) + add))
        d["captions"] = [{"t0": round(c["t0"] - s0, 3), "t1": round(c["t1"] - s0, 3), "text": c["text"]} for c in caps]
        if sc.get("source"):
            d["source"] = sc["source"]
        if proj.get("brand"):
            d.setdefault("brand", proj["brand"])
        for k in ("photo", "photo_bg"):                          # 사진 경로 → 웹 루트(저장소) 기준 주소
            if d.get(k) and not str(d[k]).startswith(("http", "/")):
                p = (Path(proj["_dir"]) / d[k]).resolve()
                d[k] = "/" + p.relative_to(ROOT).as_posix()
        scenes.append({"index": si, "start": s0, "end": t, "dur": dur_s, "rows": rows, "caps": caps, "data": d, "src": sc.get("source"),
                       "chapter": sc.get("chapter"), "scene": sc["scene"]})
    total = t
    # 효과음: 종이가 놓일 때·형광펜·챕터만(분당 상한은 규칙에서 점검)
    ev = []
    for s in scenes if E.get("sfx_style") == "neon" else []:     # 네온: 전환 휙 · 등장 팝 · 숫자 딩 · 타자 틱
        d, a, s0, k = s["data"], s["data"].get("at") or [0], s["start"], s["data"].get("kind")
        if s["index"] and k not in ("hook", "title", "part"):           # 훅·제목은 자기 효과음(휙)이 있어 전환음을 겹치지 않는다
            ev.append((s0 + 0.02, "whoosh", -16))   # 첫 낱말을 덮지 않게(11-04 ego lite 검수: 장면 첫 낱말 재인식 실패)
        at = lambda i, dflt: s0 + (a[i] if len(a) > i else dflt)
        if k == "hook":                                          # 쾅은 첫 훅에만(같은 효과 반복 금지), 뒤의 훅은 가벼운 휙
            ev.append((at(1, .15), "boom" if s["index"] == 0 else "swish", -6))
        elif k == "title":
            ev.append((at(1, .3), "swish", -6))
        elif k == "number":
            ev.append((at(1, .4) + d.get("roll", 1), "ding", -6))
        elif k in ("icons", "flow"):                             # 첫 등장과 마지막 등장에만 팝(사이사이는 조용히)
            n = len(d.get("items") or d.get("nodes") or [])
            ev += [(at(i + 1, .3 + i * .5), "pop", -10) for i in sorted({0, n - 1}) if n]
        elif k == "terminal":
            ev += [(at(i + 1, .5 + i * 1.2) + j * .09, "tick", -18) for i, l in enumerate(d.get("lines") or []) if l.startswith("$ ") for j in range(6)]
        elif k == "warn":
            ev.append((at(0, 0) + .05, "boom", -10))
        elif k == "cta":
            ev.append((at(1, .5), "ding", -8))
        elif k == "part":
            ev.append((at(0, 0) + .05, "swish", -6))
        elif k == "bars":
            nb = len(d.get("bars") or [])
            ev.append((at(nb, .3 + (nb - 1) * .9) + .6, "ding", -6))
        elif k in ("recap", "agenda"):
            ev.append((at(1, .5), "pop", -10))
    for s in scenes if E.get("sfx_style") != "neon" else []:
        d, a, s0 = s["data"], s["data"].get("at") or [0], s["start"]
        k = d.get("kind")
        if s["chapter"] or k in ("chapter", "flip"):
            ev.append((s0 + 0.05, "softwhoosh", -6))
        elif k in ("doc", "person"):
            ev.append((s0 + a[0] + 0.05, "paper", -8))
        if k in ("doc", "person", "quote") and "[[" in json.dumps(d, ensure_ascii=False):
            ev.append((s0 + (a[1] if len(a) > 1 else a[0] + 1.1), "pen", -16))
    ev = thin_sfx(ev, st["rules"].get("sfx_min_gap_sec", 0.35))
    n = int(math.ceil(total * A.SR)) + A.SR
    v, sx = np.zeros(n, np.float32), np.zeros(n, np.float32)
    for s0, x in vparts:
        A.place(v, x, s0)
    for s0, name, db in ev:
        A.place(sx, A.sfx(name), s0, db)
    A.write(str(work / "voice.wav"), v)
    A.write(str(work / "sfx.wav"), sx)
    A.write(str(work / "bgm.wav"), A.make_bgm({"bgm_mood": E.get("bgm_mood", "calm"), **proj}, n / A.SR))
    return {"scenes": scenes, "total": total, "tts": tts, "sfx": [(round(a, 2), b) for a, b, _ in ev if b != "tick"]}


def _render(args):
    i, data, dur, out, fps, frames_dir, stills, html = args
    render_scene(ROOT / html, data, dur, None if stills else out, fps, empty_ratio=0, size=(1920, 1080), serve_root=ROOT,
                 frames_dir=frames_dir, frames_at=(max(0.0, dur - 0.6),) if stills else ())
    return i


def render(tl, st, work, out_mp4, procs, log, stills=False):
    E = st["editorial"]
    fps = E["video"]["fps"]
    jobs = [(s["index"], s["data"], s["dur"], str(work / f"seg_{s['index']:03d}.mp4"), 6 if stills else fps,
             str(work / "stills" / f"s{s['index']:03d}"), stills, E.get("html", "editorial/scene.html")) for s in tl["scenes"]]
    with Pool(procs) as pool:
        for k, _ in enumerate(pool.imap_unordered(_render, jobs)):
            log(f"  장면 렌더 {k + 1}/{len(jobs)}")
    if stills:
        return
    (work / "segs.txt").write_text("".join(f"file '{Path(j[3]).as_posix()}'\n" for j in jobs), encoding="utf-8")   # Windows: 역슬래시는 concat 이 이스케이프로 읽는다
    silent = work / "video_silent.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "segs.txt"), "-c", "copy", str(silent)], check=True)
    A.mix(str(work / "voice.wav"), str(work / "sfx.wav"), str(work / "bgm.wav"), str(work / "mix.wav"), {"audio": E["audio"]})
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(work / "mix.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{tl['total']:.3f}", "-movflags", "+faststart", str(out_mp4)], check=True)


def check_rules(proj, st, tl, voice=None):
    E, out = st["editorial"], []
    want = E["voice"]
    ok_names = want["name"] if isinstance(want["name"], list) else [want["name"]]
    got = voice.voice if voice and isinstance(voice.voice, list) else [voice.voice] if voice else []
    if voice and (voice.backend != want["backend"] or not set(got) <= set(ok_names)):
        out.append(f"목소리가 {voice.voice}({voice.backend}): 이 스타일은 {' / '.join(ok_names)}만 씀")
    kinds = [s["data"].get("kind") for s in tl["scenes"]]
    run = 1
    for a, b in zip(kinds, kinds[1:]):
        run = run + 1 if a == b else 1
        if run > E["same_kind_max_run"]:
            out.append(f"같은 장면 종류 '{b}' 가 {run}번 연속")
    for s in tl["scenes"]:
        ev = sorted({0.0, *[float(x) for x in (s["data"].get("at") or []) + (s["data"].get("beats") or [])], s["dur"]})
        still = max(b - a for a, b in zip(ev, ev[1:]))                  # 화면에 새 요소가 안 나오는 가장 긴 구간
        if E.get("max_still_sec") and still > E["max_still_sec"] and s["data"].get("kind") not in ("end", "cta"):
            out.append(f"장면{s['index']} {still:.1f}초 동안 화면 변화 없음 (상한 {E['max_still_sec']}초: sync.at 낱말을 더하거나 장면을 나누세요)")
        if s["dur"] > E["scene_max_sec"] and s["data"].get("cam") not in ("tilt", "pan") and s["data"].get("kind") != "end":   # CUT-1
            out.append(f"장면{s['index']} {s['dur']:.1f}초 (상한 {E['scene_max_sec']}초: 나누거나 요소를 더 쌓으세요)")
        if s["data"].get("kind") in NUMERIC and not s["src"]:
            out.append(f"장면{s['index']}: 숫자 장면에 화면 출처(source) 없음")
    first = " ".join(r["text"] for s in tl["scenes"] for r in s["rows"] if r["start"] < E["question_by_sec"])
    if "?" not in first:
        out.append(f"첫 {E['question_by_sec']}초 안에 질문(?)이 없음")
    srcs = proj.get("sources", [])
    facts = " ".join(f for s in srcs for f in s.get("facts", [])).replace(",", "")
    allow = {str(x) for x in proj.get("numbers_ok", [])}
    unk = set()
    for s in tl["scenes"]:
        for text in [*(r["text"] for r in s["rows"]), *([] if s["scene"].get("decor_numbers") else _strings(s["scene"]))]:   # decor_numbers: 화면 꾸밈 숫자(헥스 덤프 등)
            for n_ in re.findall(r"\d[\d,]*(?:\.\d+)?", strip_markup(str(text))):
                n_ = n_.replace(",", "")
                if n_ not in facts and n_ not in allow:
                    unk.add(n_)
    if unk:
        out.append(f"출처 facts 에 없는 숫자: {', '.join(sorted(unk, key=lambda x: float(x)))}")
    nv = [s.get("id", "?") for s in srcs if not s.get("verified")]
    if nv or not srcs:
        out.append(f"원문을 열어 확인하지 않은 출처: {', '.join(nv) if nv else '출처 없음'}")
    syl = sum(len(re.findall("[가-힣]", to_speech(r["text"]))) for s in tl["scenes"] for r in s["rows"])
    spk = sum(r["end"] - r["start"] for s in tl["scenes"] for r in s["rows"])
    v_ = syl / max(spk, 0.1)
    lo, hi = E["syllables_per_sec"]
    if not lo <= v_ <= hi:
        out.append(f"내레이션 속도 {v_:.1f}음절/초 (이 스타일 권장 {lo}~{hi})")
    per_min = len(tl["sfx"]) / tl["total"] * 60
    if per_min > E["sfx_max_per_min"]:
        out.append(f"효과음 분당 {per_min:.0f}개 (상한 {E['sfx_max_per_min']})")
    return out, v_


def write_outputs(proj, tl, out):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    rows, k = [], 1
    for s in tl["scenes"]:
        for c in s["caps"]:
            rows.append(f"{k}\n{ts(c['t0'])} --> {ts(c['t1'])}\n{c['text']}\n")
            k += 1
    (out / "subtitles.srt").write_text("\n".join(rows), encoding="utf-8")
    L = [f"# {proj['title']}", "", proj.get("summary", "").strip(), ""]
    ch = [(s["start"], s["chapter"] if isinstance(s["chapter"], str) else strip_markup(s["data"].get("title", "")).replace("\n", " "))
          for s in tl["scenes"] if s["chapter"]]
    if ch:                                                     # 유튜브 챕터(첫 줄은 00:00 이어야 함)
        if ch[0][0] > 0.5:
            ch.insert(0, (0.0, proj.get("intro_chapter", "들어가며")))
        L += ["챕터"] + [f"{int(a // 60):02d}:{int(a % 60):02d} {b}" for a, b in ch] + [""]
    L.append("주요 자료" if all(s.get("verified") for s in proj.get("sources", [])) else "주요 자료 (⚠ 원문 미확인 포함)")
    for s in proj.get("sources", []):
        L.append(f"- {s['outlet']}, {s['title']} ({s['date']}) · {s['url']}")
    if proj.get("photos"):
        L += ["", "사진 출처 및 이용 조건"] + [f"- {p['title']} · {p['author']} · {p['license']} · {p['url']}" for p in proj["photos"]]
        L.append("사진은 크기 조정·잘라내기·색 보정·합성으로 변경했습니다.")
    if proj.get("disclaimer"):
        L += ["", proj["disclaimer"].strip()]
    L += ["", " ".join(proj.get("tags", [])), "", f"(자동 생성: 확인일 {datetime.date.today()})"]
    (out / "description.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    from facetube import youtube_txt                          # 유튜브 올리기 세트(제목·설명란·해시태그·출처): 최종본마다 항상
    youtube_txt.write(out, proj, ch)
    from facetube import thumbnail                            # 썸네일도 같은 세트(PUB-02)
    thumbnail.make(proj, out, proj.get("_dir", "."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out")
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--stills", action="store_true", help="영상 대신 장면별 마지막 그림만(빠른 확인)")
    ap.add_argument("--no-qc", action="store_true")
    ap.add_argument("--note", help="버전기록.md 에 남길 바뀐 점 한 줄(PUB-03)")
    ap.add_argument("--stand-in-voice", action="store_true", help="검수 전용: Voicebox 없이 Edge 여성 목소리로 파이프라인만 점검(배포 금지, 보고서에 표시)")
    a = ap.parse_args()
    t0 = time.time()
    st = load_style()
    proj = yaml.safe_load(open(a.project, encoding="utf-8"))
    E = apply_style(st, proj)
    from facetube import textnorm
    textnorm.SAY_AS.update(proj.get("say_as") or {})              # 화면 표기 ↔ 읽는 소리(REA → 알이에이)
    log0 = f"스타일: {proj.get('style', 'paper')} ({E.get('html')})"
    proj["slug"] = proj.get("slug") or Path(a.project).stem
    proj["_dir"] = str(Path(a.project).resolve().parent)
    proj["beats"] = proj["scenes"]                            # autocorrect 는 beats[].say 를 고친다(같은 dict)
    out = Path(a.out) if a.out else ROOT / "output" / proj["slug"]
    work = out / "_work"
    work.mkdir(parents=True, exist_ok=True)
    log = lambda m: print(m, flush=True)
    log(log0)
    log("① 대본 사전검사")
    fixes = autocorrect(proj, log)
    vc = {**st["editorial"]["voice"], **proj.get("voice", {})}           # 기본은 여의도여자(style.yaml editorial.voice)
    if a.stand_in_voice:
        vc = {"backend": "edge", "name": "ko-KR-SunHiNeural" if any(k in str(vc.get("name")) for k in ("여자", "엠마")) else "ko-KR-HyunsuMultilingualNeural", "speed": 1.05}
    voice = Voice(backend=vc["backend"], voice=vc.get("name"), speed=vc.get("speed", 1.0), cer_retry=st["qc"]["asr_cer_retry"],
                  instruct=vc.get("instruct"))
    log(f"② 음성 더빙({voice.backend}, 속도 {voice.speed}) + 낱말 시각 맞추기")
    tl = build_timeline(proj, st, work, voice, log)
    log(f"   총 {tl['total']:.1f}초, 장면 {len(tl['scenes'])}개, 자막 {sum(len(s['caps']) for s in tl['scenes'])}개")
    if a.stills:
        log("③ 장면 정지 그림")
        render(tl, st, work, None, a.procs, log, stills=True)
        from PIL import Image
        shots = sorted((work / "stills").glob("s*/*.png"))
        W, H, cols = 640, 360, 3
        sheet = Image.new("RGB", (W * cols, H * math.ceil(len(shots) / cols)), "white")
        for i, p in enumerate(shots):
            sheet.paste(Image.open(p).resize((W, H)), ((i % cols) * W, (i // cols) * H))
        sheet.save(out / "stills.png")
        for v in check_rules(proj, st, tl, voice)[0]:            # 그림만 볼 때도 스타일 점검(정지 구간·숫자·연속 종류)은 돌린다
            log("  ⚠ " + v)
        log(f"완료: {out / 'stills.png'}")
        return
    log("③ 렌더링")
    mp4 = out / "final.mp4"
    render(tl, st, work, mp4, a.procs, log)
    violations, spd = check_rules(proj, st, tl, voice)
    for v in violations:
        log("  ⚠ " + v)
    if not a.no_qc:
        log("④ 품질검수")
        qtl = {"scenes": [{"index": s["index"], "type": s["data"].get("kind"), "start": s["start"], "end": s["end"], "source": s["src"],
                           "chunks": [{"text": r["text"], "start": r["start"], "end": r["end"]} for r in s["rows"]]} for s in tl["scenes"]],
               "total": tl["total"], "tts": tl["tts"], "sfx": tl["sfx"], "fps": st["editorial"]["video"]["fps"]}
        rep = qc.run_qc(str(mp4), qtl, st, str(work), None, log=log)
        md = qc.report_md(rep, qtl, st)
        if a.stand_in_voice:
            md = f"> ⚠️ **검수 전용 임시 목소리(Edge {voice.voice})로 만든 파일입니다. 배포 금지.** {st['editorial']['voice']['name']}(으)로 PC에서 다시 빌드해야 합니다.\n\n" + md
        md += "\n## 에디토리얼 스타일 점검\n" + ("\n".join(f"- ⚠️ {v}" for v in violations) if violations else "- ✅ 위반 없음") + "\n"
        md += f"\n- 내레이션 속도 {spd:.1f}음절/초, 효과음 {len(tl['sfx'])}개, 장면 {len(tl['scenes'])}개 (평균 {tl['total'] / len(tl['scenes']):.1f}초)\n"
        if fixes:
            md += "\n## 대본 자동 교정\n" + "\n".join(f"- {f}" for f in fixes) + "\n"
        (out / "qc_report.md").write_text(md, encoding="utf-8")
        if rep.get("sheet"):
            shutil.copy(rep["sheet"], out / "contact_sheet.png")
        print(md)
    write_outputs(proj, tl, out)
    from facetube import release                               # 주제 이름+버전으로 세트 내보내기(PUB-03)
    release.make(proj, out, note=a.note, stand_in=a.stand_in_voice, log=log)
    log(f"완료: {mp4} ({time.time() - t0:.0f}초 소요)")


if __name__ == "__main__":
    main()
