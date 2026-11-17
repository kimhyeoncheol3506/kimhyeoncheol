"""최종 납품 전 검수 (2026-11-18 현철님 지정 5항목) — make_editorial 빌드가 끝난 뒤 돌린다.
사용: python3 tools/final_qc.py projects/<slug>.yaml [--mp4 output/<slug>/final.mp4] [--thumbs a.png b.png]
결과: output/<slug>/final_qc.md (결과표) · final_qc.json (rerecord: 다시 녹음할 장면 목록과 캐시 파일)

1. 음성: 완성 mp4 를 Whisper(faster-whisper small)로 다시 받아써 문장마다 대본과 대조.
   어긋난 문장은 배경음 없는 내레이션(_work/voice.wav)으로 한 번 더 받아써서, 거기서도 틀리면 '다시 녹음'.
   돈 단위 고유어 읽기(여든 달러 등) · 끊김(문장 안 0.9초+ 무음) · 겹침 · 잡음(문장 사이 소음·클리핑) · 말 빠르기 튐(중앙값 ±30%).
2. 자막: srt 형식(두 줄 초과·길이·겹침·이중 공백·숫자 쉼표) · 싱크(자막 시작 vs Whisper 낱말 시작 0.3초) ·
   화면 속 자막 OCR(자막 띠 글자 대조, 화면 밖 넘침).
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


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + args, capture_output=True, text=True, errors="replace").stderr


def whisper_words(audio, model):
    segs, _ = model.transcribe(audio, language="ko", word_timestamps=True, vad_filter=True, beam_size=5,
                               condition_on_previous_text=False)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in (s.words or [])]


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
    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    wav16 = os.path.join(work, "final16k.wav")
    ff(["-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav16])
    mix, sr = sf.read(wav16, dtype="float32")
    log("1. Whisper 받아쓰기(완성 mp4)…")
    W = whisper_words(mix, model)
    json.dump(W, open(os.path.join(work, "whisper_words.json"), "w", encoding="utf-8"), ensure_ascii=False)
    vx, vsr = sf.read(os.path.join(work, "voice.wav"), dtype="float32")
    if vx.ndim > 1:
        vx = vx.mean(axis=1)
    rows = qcj["asr"]                      # 문장(대본 줄)마다 시작 시각
    total = len(mix) / sr
    sent = []
    for k, r in enumerate(rows):
        t0 = r["t"]
        t1 = rows[k + 1]["t"] if k + 1 < len(rows) else total
        heard = " ".join(w for s, e, w in W if t0 - 0.25 <= (s + e) / 2 < t1 - 0.1)
        c = cer(r["script"], heard)
        x = {"t": round(t0, 2), "script": r["script"], "spoken": r["spoken"], "heard": heard, "cer": round(c, 3), "verdict": "통과"}
        ws = [(s, e) for s, e, w in W if t0 - 0.25 <= (s + e) / 2 < t1 - 0.1]
        if ws:
            syl = len(re.sub(r"[^가-힣]", "", r["spoken"]))
            dur = ws[-1][1] - ws[0][0]
            x["rate"] = round(syl / dur, 2) if dur > 0.5 else None
        if c > 0.25:                          # 배경음 없는 내레이션으로 다시 확인
            seg = vx[int(max(0, t0 - 0.1) * vsr):int((t1 - 0.05) * vsr)]
            if vsr != 16000:
                import scipy.signal as S
                seg = S.resample_poly(seg, 16000, vsr).astype("float32")
            h2 = " ".join(w for _, _, w in whisper_words(seg, model))
            c2 = cer(r["script"], h2)
            x.update({"heard_clean": h2, "cer_clean": round(c2, 3)})
            x["verdict"] = "다시 녹음" if c2 > 0.2 else "통과(배경음 섞인 인식 오차, 깨끗한 음성 확인)"
        if NATIVE_MONEY.search(r["spoken"]):
            x["verdict"] = "다시 녹음"
            x["money"] = "읽기 글에 고유어 돈 단위: " + NATIVE_MONEY.search(r["spoken"]).group(0)
        elif NATIVE_MONEY.search(heard.replace(" ", "")) and not NATIVE_MONEY.search(r["script"]):
            x["money_heard"] = "들린 말에 고유어 돈 단위 의심: " + NATIVE_MONEY.search(heard.replace(" ", "")).group(0)
        sent.append(x)
    rates = [s["rate"] for s in sent if s.get("rate")]
    med = float(np.median(rates)) if rates else 0
    for s in sent:
        if s.get("rate") and med and not (0.7 * med <= s["rate"] <= 1.3 * med):
            s["rate_flag"] = f"말 빠르기 튐 {s['rate']}음절/초 (중앙값 {med:.2f})"
    # 끊김(빌드 QC: 문장 안 0.9초+ 무음) · 잡음(문장 사이 무음 구간 소음) · 클리핑
    gaps = qcj.get("gaps", [])
    noise = []
    for k in range(len(rows) - 1):
        a0 = int((rows[k + 1]["t"] - 0.12) * vsr)
        seg = vx[max(0, a0 - int(0.08 * vsr)):a0]
        if len(seg) and np.sqrt(np.mean(seg ** 2)) > 0.02:
            noise.append(round(rows[k + 1]["t"], 2))
    clip = int(np.sum(np.abs(mix) > 0.999))
    R["voice"] = {"sentences": len(sent), "bad": [s for s in sent if s["verdict"] == "다시 녹음"],
                  "asr_noise": sum(1 for s in sent if s["verdict"].startswith("통과(")),
                  "money": [s for s in sent if s.get("money") or s.get("money_heard")],
                  "gaps": gaps, "noise": noise, "clip_samples": clip, "rate_median": round(med, 2),
                  "rate_flags": [s for s in sent if s.get("rate_flag")], "rows": sent}

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
            if first and ww and (cer(first, ww) <= 0.34 or ww[:2] == first[:2]):
                if best is None or abs(s - c["t0"]) < abs(best - c["t0"]):
                    best = s
        if best is not None:
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
        tsv = subprocess.run(["tesseract", png, "-", "-l", "kor", "--psm", "6", "tsv"], capture_output=True, text=True, errors="replace").stdout
        ws = [r.split("\t") for r in tsv.splitlines()[1:] if r.count("\t") >= 11 and r.split("\t")[11].strip() and float(r.split("\t")[10]) > 30]
        txt = "".join(w[11] for w in ws)
        e = cer(c["text"], txt)
        edge = any(int(w[6]) < 8 or int(w[6]) + int(w[8]) > 1912 for w in ws)
        if e > 0.35 or edge:
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
    tts = []
    for j in glob.glob(os.path.join(work, "tts", "*.json")):
        try:
            tts.append((j, json.load(open(j, encoding="utf-8")).get("spoken", "")))
        except Exception:
            pass
    rer = []
    for s in R["voice"]["bad"]:
        for i, sc in enumerate(proj["scenes"]):
            if s["script"] in strip_markup(sc["say"]).replace("\n", " "):
                sp = to_speech(sc["say"].strip())
                hit = [j for j, spk in tts if spk and cer(sp, spk) < 0.1]
                rer.append({"scene": i, "script": s["script"], "cache": hit})
                break
    R["rerecord"] = rer
    json.dump(R, open(os.path.join(out, "final_qc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

    # ── 결과표 ────────────────────────────────────────────
    V, S, N, Vd = R["voice"], R["subs"], R["numbers"], R["video"]
    ok = lambda b: "✅ 통과" if b else "❌ 수정 필요"
    L = [f"# 최종 검수 결과표 — {proj.get('title')}", "", f"- 파일: `{os.path.relpath(mp4, ROOT)}` ({Vd['duration']}초)", "",
         "| 항목 | 점검 | 결과 |", "|---|---|---|",
         f"| 1 음성 | Whisper 대조 {V['sentences']}문장 · 다시 녹음 대상 {len(V['bad'])} · 배경음 인식오차(깨끗한 음성으로 통과) {V['asr_noise']} | {ok(not V['bad'])} |",
         f"| 1 음성 | 돈 단위 고유어 읽기 {len([m for m in V['money'] if m.get('money')])} · 들린 말 의심 {len([m for m in V['money'] if m.get('money_heard')])} | {ok(not [m for m in V['money'] if m.get('money')])} |",
         f"| 1 음성 | 끊김 {len(V['gaps'])} · 문장 사이 잡음 {len(V['noise'])} · 클리핑 {V['clip_samples']}샘플 · 말 빠르기 튐 {len(V['rate_flags'])} (중앙값 {V['rate_median']}음절/초) | {ok(not V['gaps'] and not V['noise'] and V['clip_samples'] == 0 and not V['rate_flags'])} |",
         f"| 2 자막 | srt {S['count']}개 · 문제 {len(S['issues'])} · 싱크 확인 {S['offset_checked']}개(중앙값 {S['offset_median']}초) | {ok(not S['issues'])} |",
         f"| 2 자막 | 화면 속 자막 OCR 의심 {len(S['burn_suspect'])} (넘침 {sum(1 for b in S['burn_suspect'] if b['edge'])}) | {ok(not S['burn_suspect'])} |",
         f"| 3 숫자 | 숫자 {N['total']}개(고유 {N['unique']}) · 대사 {N['by_where']['대사']}/화면 {N['by_where']['화면']}/자막 {N['by_where']['자막']} · 불일치 {len(N['mismatch'])} · 출처 없는 숫자 판 {len(N['no_source_scene'])} | {ok(not N['mismatch'] and not N['no_source_scene'])} |",
         f"| 4 영상 | 음량 {Vd['lufs']} LUFS (피크 {Vd['peak_db']} dB) | {ok(Vd['lufs_ok'])} |",
         f"| 4 영상 | 검은 화면 {len(Vd['black'])} · 4초+ 멈춤 {len(Vd['freeze4'])} · 개인정보 {len(Vd['pii'])} | {ok(not Vd['black'] and not Vd['pii'])} |",
         f"| 5 확인필요 | {len(R['todo'])}건 | {'목록 아래' if R['todo'] else '없음'} |", ""]
    if V["bad"]:
        L += ["## 다시 녹음 대상", "| 시각 | 대본 | 들린 말(완성본) | 들린 말(깨끗한 음성) |", "|---|---|---|---|"]
        L += [f"| {s['t']} | {s['script']} | {s['heard']} | {s.get('heard_clean', '')} {s.get('money', '')} |" for s in V["bad"]]
    for title, xs in (("돈 단위 의심", [f"- {s['t']}초 {s['script']} → {s.get('money') or s.get('money_heard')}" for s in V["money"]]),
                      ("끊김", [f"- {g['t']}초 {g['text']} (무음 {g['silence']}초)" for g in V["gaps"]]),
                      ("문장 사이 잡음", [f"- {t}초" for t in V["noise"]]),
                      ("말 빠르기 튐", [f"- {s['t']}초 {s['script']} — {s['rate_flag']}" for s in V["rate_flags"]]),
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
