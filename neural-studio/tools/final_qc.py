"""최종 납품 전 검수 (2026-11-18 현철님 지정 5항목) — make_editorial 빌드가 끝난 뒤 돌린다.
사용: python3 tools/final_qc.py projects/<slug>.yaml [--mp4 output/<slug>/final.mp4] [--thumbs a.png b.png]
결과: output/<slug>/final_qc.md (결과표) · final_qc.json (rerecord: 다시 녹음할 장면 목록과 캐시 파일)

1. 음성: 장면 녹음(_work/tts/<key>.wav — 영상에 들어간 그 소리)을 Whisper 로 받아쓰고 빌드 음성인식과 함께 대조(숫자 표기는 읽는 소리로 바꿔 비교).
   두 엔진 모두 CER 0.15 초과면 '다시 녹음', 두 엔진 모두 다르게 들은 낱말은 '의심 낱말(귀로 확인)'.
   완성 mp4 받아쓰기로 장면 소리가 실제로 들어갔는지 확인. 돈 단위 고유어 읽기 · 끊김(0.9초+ 쉼) · 겹침 · 장면 사이 잡음 · 녹음 끝 딸깍 · 클리핑 · 말 빠르기(중앙값 ±25%).
2. 자막: srt 형식(두 줄 초과·길이·겹침·이중 공백·숫자 쉼표) · 싱크(자막 시작 vs 실제 말소리 시작 0.3초; Whisper 낱말 시각을 쉼 뒤 말소리 시작으로 보정) ·
   화면 속 자막 OCR(어두운 자막 상자만 잘라 대조, 화면 밖 넘침).
3. 숫자: 대사·화면 그래픽·자막의 모든 숫자가 출처 facts(+numbers_ok)에 있는지 대조표.
4. 영상: 음량 LUFS(-14~-16) · 검은 화면 · 멈춘 화면(4초+, 끝 화면 제외) · 개인정보(빌드 QC 결과) · 썸네일 OCR.
5. 확인필요: 대본의 '확인필요/미확인/실적대기' 주석, verified 아닌 출처."""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from facetube.textnorm import cer, strip_markup, to_speech, lint_subtitle, SAY_AS  # noqa: E402
from facetube import qc as Q  # noqa: E402

NATIVE = "한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|스물|스무|서른|마흔|쉰|예순|일흔|여든|아흔"
UNITS = "달러|달라|엔|유로|위안|파운드|프랑|페소|리얄|루블|루피|센트|원|바트|레알|리라|랜드"
NATIVE_MONEY = re.compile(rf"(?<![가-힣])(?:{NATIVE})(?:\s?(?:{NATIVE}))*\s?(?:{UNITS})(?![가-힣]*(?:장|급))")
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


KO = lambda s: re.sub(r"[^가-힣a-zA-Z0-9]", "", s)
JOSA = ("은", "는", "이", "가", "을", "를", "의", "에", "에서", "까지", "로", "으로", "와", "과", "엔", "도", "만")


def norm_heard(h):
    """받아쓴 글의 숫자 표기를 읽는 소리로(4 ,968 .48 → 사천구백육십팔 점 사팔) 바꿔 대본 읽기 글과 비교한다."""
    h = re.sub(r"(\d)\s*([.,])\s*(\d)", r"\1\2\3", h)
    h = re.sub(r"(\d)\s*%", r"\1%", h)
    return to_speech(h)


def both_wrong(spoken, h1, h2, pronounce):
    """두 음성인식 모두 들은 말에 없는 낱말(소리 나는 대로 표기·조사 뗀 꼴도 인정)."""
    def forms(h):
        return [KO(h), KO(norm_heard(h)), KO(pronounce(norm_heard(h)))]
    H1, H2 = forms(h1), forms(h2)

    def ok(w, hs):
        c = KO(w)
        if len(c) < 2:
            return True
        f = {c, KO(pronounce(w))}
        for j in JOSA:
            if c.endswith(j) and len(c) - len(j) >= 2:
                f.add(c[:-len(j)])
        return any(x in h for x in f for h in hs)
    return [w for w in spoken.split() if not ok(w, H1) and not ok(w, H2)]


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + args, capture_output=True, text=True, errors="replace").stderr


def whisper_words(audio, model):
    segs, _ = model.transcribe(audio, language="ko", word_timestamps=True, vad_filter=True, beam_size=5,
                               condition_on_previous_text=False)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in (s.words or [])]


def sub_box_ocr(png):
    """아래 띠에서 자막의 어두운 상자만 잘라(오른쪽 아래 '자료:' 표기 제외) 반전해서 읽는다. (글, 화면 끝에 닿음 여부)"""
    from PIL import Image, ImageOps
    im = Image.open(png).convert("L")
    g = np.asarray(im, dtype="float32")
    dark = g < 70
    rows = np.where(dark.mean(axis=1) > 0.08)[0]
    if len(rows) == 0:
        return "", False
    y0, y1 = rows.min(), rows.max()
    cols = np.where(dark[y0:y1 + 1].mean(axis=0) > 0.5)[0]
    if len(cols) == 0:
        return "", False
    x0, x1 = cols.min(), cols.max()
    # 배경이 어두운 장면은 자막 상자와 배경이 구분되지 않아 띠 전체가 '상자'로 잡힌다 → 넘침 판정을 하지 않는다
    edge = (x0 < 8 or x1 > g.shape[1] - 8) and dark[y0:y1 + 1].mean() < 0.6
    box = ImageOps.invert(im.crop((x0, y0, x1 + 1, y1 + 1)))
    box = box.resize((box.width * 2, box.height * 2))
    tmp = png[:-4] + "_box.png"
    box.save(tmp)
    txt = subprocess.run(["tesseract", tmp, "-", "-l", "kor", "--psm", "6"], capture_output=True, text=True, errors="replace").stdout
    os.remove(tmp)
    return " ".join(txt.split()), bool(edge)


def srt_parse(path):
    out = []
    for blk in open(path, encoding="utf-8").read().strip().split("\n\n"):
        L = blk.strip().splitlines()
        if len(L) < 3:
            continue
        a, b = L[1].split(" --> ")
        sec = lambda x: int(x[:2]) * 3600 + int(x[3:5]) * 60 + float(x[6:].replace(",", "."))
        out.append({"i": int(L[0]), "t0": sec(a), "t1": sec(b), "lines": L[2:], "text": " ".join(L[2:])})
    return out


def num_norm(n):
    return n.replace(",", "").rstrip(".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--mp4")
    ap.add_argument("--thumbs", nargs="*", default=[])
    ap.add_argument("--model", default="small")
    a = ap.parse_args()
    proj = yaml.safe_load(open(a.project, encoding="utf-8"))
    SAY_AS.update(proj.get("say_as") or {})
    slug = proj.get("slug") or os.path.splitext(os.path.basename(a.project))[0]
    out = os.path.join(ROOT, "output", slug)
    work = os.path.join(out, "_work")
    mp4 = a.mp4 or os.path.join(out, "final.mp4")
    qcj = json.load(open(os.path.join(work, "qc.json"), encoding="utf-8"))
    R = {"slug": slug, "mp4": mp4}
    log = lambda m: print(m, flush=True)

    # ── 1. 음성 ───────────────────────────────────────────
    # (2026-11-17 첫 실전에서 고침) 완성본 받아쓰기는 배경음·숫자 때문에 오인식이 많고, 빌드 QC 의 문장 시각도 숫자 문장에서 어긋났다.
    # 그래서 ① 장면 녹음 파일(_work/tts/<key>.wav = 영상에 들어간 바로 그 소리)을 Whisper 로 받아쓰고, 빌드 음성인식(다른 엔진)과
    # 함께 본다. 두 엔진이 같은 낱말을 다르게 들으면 '의심 낱말', 둘 다 CER 이 높으면 '다시 녹음'.
    # ② 완성 mp4 받아쓰기는 장면마다 소리가 실제로 들어갔는지(빠짐·겹침)만 본다.
    from faster_whisper import WhisperModel
    import scipy.signal as S
    from facetube.captions import speech_regions, align_pieces
    import facetube.captions as CAP
    from facetube.g2p import pronounce
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    if a.model == "small":
        CAP._WM.append(model)                               # 자막 시각 맞춤(낱말 시각)도 같은 모델을 쓴다
    wav16 = os.path.join(work, "final16k.wav")
    ff(["-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav16])
    mix, sr = sf.read(wav16, dtype="float32")
    total = len(mix) / sr
    log("1. Whisper 받아쓰기(완성 mp4 + 장면 녹음)…")
    W = whisper_words(mix, model)
    json.dump(W, open(os.path.join(work, "whisper_words.json"), "w", encoding="utf-8"), ensure_ascii=False)
    vx, vsr = sf.read(os.path.join(work, "voice.wav"), dtype="float32")
    if vx.ndim > 1:
        vx = vx.mean(axis=1)
    VREG = speech_regions(vx, vsr)                         # 내레이션의 실제 말소리 구간(자막 싱크 기준)
    vt = json.load(open(os.path.join(work, "voice_timeline.json"), encoding="utf-8"))["tts"]
    sent = []
    for k, u in enumerate(vt):
        x, xsr = sf.read(os.path.join(work, "tts", u["key"] + ".wav"), dtype="float32")
        y = S.resample_poly(x, 16000, xsr).astype("float32")
        segs, _ = model.transcribe(y, language="ko", beam_size=5, vad_filter=False, condition_on_previous_text=False)
        heard = " ".join(s.text.strip() for s in segs)
        spoken = u["spoken"]
        cw = cer(KO(spoken), KO(norm_heard(heard)))
        cb = float(u.get("cer") or 0)
        sus = both_wrong(spoken, heard, u.get("asr") or "", pronounce)
        t0, t1 = u["start"], u["start"] + u["dur"]
        inmix = " ".join(w for s, e, w in W if e > t0 + 0.05 and s < t1 - 0.05)   # Whisper 낱말 시각은 1초 가까이 앞당겨지기도 해서 겹치기만 하면 넣는다
        cm = cer(KO(spoken), KO(norm_heard(inmix)))
        regs = speech_regions(x, xsr)
        voiced = sum(b - a_ for a_, b in regs)
        syl = len(re.sub(r"[^가-힣]", "", spoken))
        gaps_in = [round(regs[q + 1][0] - regs[q][1], 2) for q in range(len(regs) - 1) if regs[q + 1][0] - regs[q][1] >= 0.9]
        if gaps_in:
            # 문장 끝(. ? !)·쉼표 뒤 1.3초 이하의 쉼은 자연스러운 숨 → 끊김으로 세지 않는다(낱말 시각은 자막과 같은 방식으로 맞춤)
            wl = strip_markup(u["text"]).split()
            try:
                st_w = [a_ for a_, _ in align_pieces(x, xsr, wl)] if len(wl) > 1 else [0.0]
            except Exception:
                st_w = []
            keep = []
            for q in range(len(regs) - 1):
                g = regs[q + 1][0] - regs[q][1]
                if g < 0.9:
                    continue
                at = [k for k in range(1, len(st_w)) if abs(st_w[k] - regs[q + 1][0]) < 0.08]
                if g <= 1.3 and at and re.search(r"[.?!,…]$", wl[at[0] - 1]):
                    continue
                keep.append(round(g, 2))
            gaps_in = keep
        edge = max(float(np.sqrt(np.mean(x[:int(0.03 * xsr)] ** 2))), float(np.sqrt(np.mean(x[-int(0.03 * xsr):] ** 2))))
        r = {"scene": u["scene"], "t": round(t0, 2), "script": u["text"], "spoken": spoken, "heard": heard, "asr_b": u.get("asr"),
             "cer_w": round(cw, 3), "cer_b": round(cb, 3), "cer_mix": round(cm, 3), "suspect": sus, "key": u["key"],
             "rate": round(syl / voiced, 2) if voiced > 0.5 else None, "gaps_in": gaps_in, "edge_rms": round(edge, 4),
             "clip": int(np.sum(np.abs(x) > 0.999))}
        r["verdict"] = "다시 녹음" if (cw > 0.15 and cb > 0.15) else ("의심 낱말(귀로 확인)" if sus else "통과")
        if cm > 0.5 and cw <= 0.15:
            r["verdict"] = "완성본에서 소리 이상"
        if NATIVE_MONEY.search(spoken):
            r["verdict"] = "다시 녹음"
            r["money"] = "읽기 글에 고유어 돈 단위: " + NATIVE_MONEY.search(spoken).group(0)
        elif NATIVE_MONEY.search(heard.replace(" ", "")) and not NATIVE_MONEY.search(u["text"]):
            r["money_heard"] = "들린 말에 고유어 돈 단위 의심: " + NATIVE_MONEY.search(heard.replace(" ", "")).group(0)
        sent.append(r)
        log(f"   [{k + 1}/{len(vt)}] W {cw:.3f} · 빌드 {cb:.3f} · 완성본 {cm:.3f} {sus or ''}")
    rates = [s["rate"] for s in sent if s.get("rate")]
    med = float(np.median(rates)) if rates else 0
    for s in sent:
        if s.get("rate") and med and not (0.75 * med <= s["rate"] <= 1.25 * med):
            s["rate_flag"] = f"말 빠르기 {s['rate']}음절/초 (중앙값 {med:.2f})"
    # 장면 녹음끼리 겹침 · 장면 사이 잡음(내레이션 트랙은 장면 사이가 무음이어야 함)
    overlap, noise = [], []
    for k in range(len(vt) - 1):
        e0, s1 = vt[k]["start"] + vt[k]["dur"], vt[k + 1]["start"]
        if e0 > s1 + 0.01:
            overlap.append(round(s1, 2))
        if s1 - e0 > 0.2:
            seg = vx[int((e0 + 0.05) * vsr):int((s1 - 0.05) * vsr)]
            if len(seg) and float(np.sqrt(np.mean(seg ** 2))) > 0.003:
                noise.append(round(e0, 2))
    clip = int(np.sum(np.abs(mix) > 0.999))
    gaps = [{"t": s["t"], "text": s["script"][:40], "silence": g} for s in sent for g in s["gaps_in"]]
    R["voice"] = {"sentences": len(sent), "bad": [s for s in sent if s["verdict"] in ("다시 녹음", "완성본에서 소리 이상")],
                  "suspect": [s for s in sent if s["verdict"].startswith("의심")],
                  "money": [s for s in sent if s.get("money") or s.get("money_heard")],
                  "gaps": gaps, "noise": noise, "overlap": overlap, "clip_samples": clip, "rate_median": round(med, 2),
                  "rate_flags": [s for s in sent if s.get("rate_flag")], "rows": sent,
                  "edge_click": [s for s in sent if s["edge_rms"] > 0.02]}

    # ── 2. 자막 ───────────────────────────────────────────
    log("2. 자막 점검…")
    caps = srt_parse(os.path.join(out, "subtitles.srt"))
    sub = []
    for k, c in enumerate(caps):
        iss = []
        if len(c["lines"]) > 2:
            iss.append("두 줄 초과")
        if any(len(l) > 42 for l in c["lines"]):
            iss.append(f"한 줄 {max(len(l) for l in c['lines'])}자(42자 초과)")
        if k + 1 < len(caps) and c["t1"] > caps[k + 1]["t0"] + 0.01:
            iss.append("다음 자막과 겹침")
        if re.search(r"\s[,.?!]", c["text"]) or "  " in c["text"]:
            iss.append("띄어쓰기(문장부호 앞 공백·이중 공백)")
        if re.search(r"(?<![\d,.])\d{5,}(?![\d년])", c["text"]):
            iss.append("숫자 쉼표 빠짐")
        iss += lint_subtitle(c["text"])
        # 싱크: 자막 첫 낱말이 들린 시각
        first = re.sub(r"[^가-힣A-Za-z0-9]", "", c["text"].split()[0]) if c["text"].split() else ""
        cand = [(s, w) for s, e, w in W if abs(s - c["t0"]) < 1.5]
        best = None
        for s, w in cand:
            ww = re.sub(r"[^가-힣A-Za-z0-9]", "", w)
            if first and ww and (cer(first, ww) <= 0.25 or (len(first) >= 4 and ww[:2] == first[:2])):
                if best is None or abs(s - c["t0"]) < abs(best - c["t0"]):
                    best = s
        if best is not None:
            # Whisper 는 쉼 뒤 첫 낱말 시작을 쉼 앞쪽으로 당겨 적는다 → 그 시각이 말소리 밖(쉼)이면 다음 말소리 시작을 진짜 시각으로 본다
            inside = [(a0, b0) for a0, b0 in VREG if a0 - 0.05 <= best <= b0 + 0.05]
            nxt = [a0 for a0, _ in VREG if a0 > best]
            # 쉼 속이거나 앞 말소리 끝자락(0.25초 안)에 찍혔으면 다음 말소리 시작이 진짜 시각
            if nxt and nxt[0] - best < 1.6 and (not inside or (inside[0][1] - best < 0.35 and nxt[0] - inside[0][1] >= 0.22)):
                best = nxt[0]
            c["offset"] = round(c["t0"] - best, 2)
            if abs(c["offset"]) > 0.3:
                iss.append(f"싱크 {c['offset']:+.2f}초")
        if iss:
            sub.append({"i": c["i"], "t": round(c["t0"], 2), "text": c["text"], "issues": iss})
    offs = [c["offset"] for c in caps if "offset" in c]
    # 화면 속 자막(번인) OCR: 자막마다 가운데 시각 한 장, 아래쪽 띠
    ocrd = os.path.join(work, "capocr")
    os.makedirs(ocrd, exist_ok=True)
    burn = []
    for c in caps:
        tm = (c["t0"] + c["t1"]) / 2
        png = os.path.join(ocrd, f"c{c['i']:04d}.png")
        ff(["-y", "-ss", f"{tm:.2f}", "-i", mp4, "-frames:v", "1", "-vf", "crop=iw:ih*0.2:0:ih*0.8", png])
        txt, edge = sub_box_ocr(png)
        e = cer(KO(c["text"]), KO(txt))
        if e > 0.25 or edge:
            burn.append({"i": c["i"], "t": round(c["t0"], 2), "text": c["text"], "ocr": txt, "cer": round(e, 2), "edge": edge})
        os.remove(png)
    R["subs"] = {"count": len(caps), "issues": sub, "offset_median": round(float(np.median(offs)), 2) if offs else None,
                 "offset_checked": len(offs), "burn_suspect": burn}

    # ── 3. 숫자 ───────────────────────────────────────────
    log("3. 숫자 대조…")
    facts = set()
    for s in proj.get("sources", []):
        for f in s.get("facts", []):
            facts |= {num_norm(n) for n in NUM.findall(str(f))}
    allow = {num_norm(str(n)) for n in proj.get("numbers_ok", [])}

    def strings(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "from" and isinstance(v, (int, float)):
                    continue                      # 카운터 시작값(화면에 잠깐 지나가는 숫자)
                if k not in ("kind", "theme", "cam", "color", "fx", "photo", "photo_bg", "at", "beats", "sync", "hold", "instruct", "dir", "connector"):
                    yield from strings(v)
        elif isinstance(o, list):
            for v in o:
                yield from strings(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            yield str(o)
        elif isinstance(o, str):
            yield o
    nums, bad = [], []
    for i, sc in enumerate(proj["scenes"]):
        for where, txts in (("대사", [sc.get("say", "")]), ("화면", list(strings(sc.get("scene", {}))))):
            for t in txts:
                for n in NUM.findall(strip_markup(str(t))):
                    nn = num_norm(n)
                    ok = nn in facts or nn in allow
                    nums.append((i, where, n, ok))
                    if not ok:
                        bad.append({"scene": i, "where": where, "num": n, "text": strip_markup(str(t))[:60]})
    for c in caps:
        for n in NUM.findall(c["text"]):
            nn = num_norm(n)
            ok = nn in facts or nn in allow
            nums.append((-1, "자막", n, ok))
            if not ok:
                bad.append({"scene": "자막", "where": "자막", "num": n, "text": c["text"][:60]})
    # 장면 숫자에 출처 표기
    nosrc = [i for i, sc in enumerate(proj["scenes"]) if sc["scene"].get("kind") in ("bars", "waffle", "line", "gauge", "bignum", "stairs", "pie") and not sc.get("source")]
    R["numbers"] = {"total": len(nums), "unique": len({num_norm(n) for _, _, n, _ in nums}), "mismatch": bad,
                    "by_where": {w: sum(1 for x in nums if x[1] == w) for w in ("대사", "화면", "자막")}, "no_source_scene": nosrc}

    # ── 4. 영상 ───────────────────────────────────────────
    log("4. 음량·검은 화면·멈춤·썸네일…")
    au = Q.audio_stats(mp4)
    fr = [f for f in Q.detect_freeze(mp4, 4.0) if f[1] is None or True]
    ends = [i for i, sc in enumerate(proj["scenes"]) if sc["scene"].get("kind") == "end"]
    end_t = total - (proj["scenes"][ends[-1]].get("hold", 0) + 3) if ends else total
    fr = [f for f in fr if f[0] < end_t]
    th = []
    for p in a.thumbs:
        txt = subprocess.run(["tesseract", p, "-", "-l", "kor+eng", "--psm", "11"], capture_output=True, text=True, errors="replace").stdout
        th.append({"file": os.path.basename(p), "ocr": " ".join(txt.split())})
    R["video"] = {"lufs": au["lufs"], "peak_db": au["peak_db"], "lufs_ok": au["lufs"] is not None and -16 <= au["lufs"] <= -14,
                  "black": Q.detect_black(mp4), "freeze4": fr, "pii": qcj.get("pii", []), "thumbs": th,
                  "duration": round(total, 1)}

    # ── 5. 확인필요 ───────────────────────────────────────
    raw = open(a.project, encoding="utf-8").read().splitlines()
    todo = [l.strip() for l in raw if re.search(r"확인\s?필요|미확인|실적대기|TODO", l)]
    todo += [f"출처 미검증: {s.get('outlet')}" for s in proj.get("sources", []) if not s.get("verified")]
    R["todo"] = todo

    # ── 다시 녹음할 장면 → 캐시 파일 ────────────────────────
    rer = [{"scene": x["scene"], "script": x["script"], "cache": [os.path.join(work, "tts", x["key"] + ".json")]}
           for x in R["voice"]["bad"]]
    R["rerecord"] = rer
    json.dump(R, open(os.path.join(out, "final_qc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

    # ── 결과표 ────────────────────────────────────────────
    V, S, N, Vd = R["voice"], R["subs"], R["numbers"], R["video"]
    ok = lambda b: "✅ 통과" if b else "❌ 수정 필요"
    L = [f"# 최종 검수 결과표 — {proj.get('title')}", "", f"- 파일: `{os.path.relpath(mp4, ROOT)}` ({Vd['duration']}초)", "",
         "| 항목 | 점검 | 결과 |", "|---|---|---|",
         f"| 1 음성 | 장면 녹음 {V['sentences']}개를 Whisper+빌드 인식 두 엔진으로 대조 · 다시 녹음 {len(V['bad'])} · 의심 낱말(귀로 확인) {len(V['suspect'])} | {ok(not V['bad'])} |",
         f"| 1 음성 | 돈 단위 고유어 읽기 {len([m for m in V['money'] if m.get('money')])} · 들린 말 의심 {len([m for m in V['money'] if m.get('money_heard')])} | {ok(not [m for m in V['money'] if m.get('money')])} |",
         f"| 1 음성 | 끊김(0.9초+) {len(V['gaps'])} · 겹침 {len(V['overlap'])} · 장면 사이 잡음 {len(V['noise'])} · 녹음 끝 딸깍 {len(V['edge_click'])} · 클리핑 {V['clip_samples']}샘플 · 말 빠르기 튐(±25%) {len(V['rate_flags'])} (중앙값 {V['rate_median']}음절/초) | {ok(not V['gaps'] and not V['overlap'] and not V['noise'] and not V['edge_click'] and V['clip_samples'] == 0 and not V['rate_flags'])} |",
         f"| 2 자막 | srt {S['count']}개 · 문제 {len(S['issues'])} · 싱크 확인 {S['offset_checked']}개(중앙값 {S['offset_median']}초) | {ok(not S['issues'])} |",
         f"| 2 자막 | 화면 속 자막 OCR 의심 {len(S['burn_suspect'])} (넘침 {sum(1 for b in S['burn_suspect'] if b['edge'])}) | {ok(not S['burn_suspect'])} |",
         f"| 3 숫자 | 숫자 {N['total']}개(고유 {N['unique']}) · 대사 {N['by_where']['대사']}/화면 {N['by_where']['화면']}/자막 {N['by_where']['자막']} · 불일치 {len(N['mismatch'])} · 출처 없는 숫자 판 {len(N['no_source_scene'])} | {ok(not N['mismatch'] and not N['no_source_scene'])} |",
         f"| 4 영상 | 음량 {Vd['lufs']} LUFS (피크 {Vd['peak_db']} dB) | {ok(Vd['lufs_ok'])} |",
         f"| 4 영상 | 검은 화면 {len(Vd['black'])} · 4초+ 멈춤 {len(Vd['freeze4'])} · 개인정보 {len(Vd['pii'])} | {ok(not Vd['black'] and not Vd['pii'])} |",
         f"| 5 확인필요 | {len(R['todo'])}건 | {'목록 아래' if R['todo'] else '없음'} |", ""]
    if V["bad"]:
        L += ["## 다시 녹음 대상", "| 시각 | 대본 | Whisper | 빌드 인식 | 판정 |", "|---|---|---|---|---|"]
        L += [f"| {s['t']} | {s['script']} | {s['heard']} | {s['asr_b']} | {s['verdict']} {s.get('money', '')} |" for s in V["bad"]]
    if V["suspect"]:
        L += ["", "## 의심 낱말(두 엔진 모두 다르게 들음 — 귀로 확인)", "| 시각 | 낱말 | 대본 | Whisper | 빌드 인식 |", "|---|---|---|---|---|"]
        L += [f"| {s['t']} | {', '.join(s['suspect'])} | {s['script']} | {s['heard']} | {s['asr_b']} |" for s in V["suspect"]]
    for title, xs in (("돈 단위 의심", [f"- {s['t']}초 {s['script']} → {s.get('money') or s.get('money_heard')}" for s in V["money"]]),
                      ("끊김", [f"- {g['t']}초 {g['text']} (무음 {g['silence']}초)" for g in V["gaps"]]),
                      ("장면 사이 잡음", [f"- {t}초" for t in V["noise"]]),
                      ("겹침", [f"- {t}초" for t in V["overlap"]]),
                      ("녹음 끝 딸깍", [f"- {s['t']}초 {s['script'][:30]} (RMS {s['edge_rms']})" for s in V["edge_click"]]),
                      ("말 빠르기 튐", [f"- {s['t']}초 {s['script'][:40]} — {s['rate_flag']}" for s in V["rate_flags"]]),
                      ("자막 문제", [f"- #{x['i']} {x['t']}초 「{x['text']}」 {', '.join(x['issues'])}" for x in S["issues"]]),
                      ("화면 속 자막 OCR 의심(눈으로 확인)", [f"- #{b['i']} {b['t']}초 「{b['text']}」 OCR 「{b['ocr']}」 CER {b['cer']}{' 넘침' if b['edge'] else ''}" for b in S["burn_suspect"]]),
                      ("숫자 불일치", [f"- 장면 {m['scene']} {m['where']} {m['num']} — {m['text']}" for m in N["mismatch"]]),
                      ("4초 이상 멈춘 화면(정지 판 — 눈으로 확인)", [f"- {f[0]:.1f}~{f[1] if f[1] is None else round(f[1], 1)}초" for f in Vd["freeze4"]]),
                      ("썸네일 글자(OCR)", [f"- {t['file']}: {t['ocr']}" for t in Vd["thumbs"]]),
                      ("확인필요", [f"- {t}" for t in R["todo"]])):
        if xs:
            L += ["", f"## {title}"] + xs
    open(os.path.join(out, "final_qc.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:16]))


if __name__ == "__main__":
    main()
