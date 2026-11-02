#!/usr/bin/env python3
"""아나운서 운율(쉼·속도·억양) 측정과 비교. '여의도여자'가 기계처럼 들리는 이유를 숫자로 찾는다.

  python tools/prosody_ref.py measure voice_ref/ref_emily.mp3 voice_ref/calibration_ko.txt -o voice_ref/ref_emily.json
  python tools/prosody_ref.py compare voice_ref/ref_emily.json voice_ref/ours_yeouido_f.json      # 차이 보고
  python tools/prosody_ref.py profile voice_ref/ref_*.json -o voice_ref/announcer_profile.yaml    # 기준 묶음 → 적용 프로필
  python tools/prosody_ref.py ab voice_ref/calibration_ko.txt --ref voice_ref/ref_emily.json      # (현철님 PC) 여의도여자 전/후 비교

측정(같은 대본을 두 목소리로 읽혀서 비교한다)
  - 낱말 시각: 우리 음성인식(sherpa zipformer)으로 글자 시각 → 어절 시작 시각
  - 쉼: 어절 경계마다 무음 길이(쉼표·문장 끝·그 밖), 조사 뒤 쉼 확률
  - 속도: 문장별 음절/초(쉼 제외)
  - 억양: 기본주파수(F0, 자기상관) → 음역(반음), 문장 안 내림(declination), 문장 끝 3음절 내림/올림, 숫자 낱말의 음높이·세기 강조
발음 자체(소리 하나하나)는 이 측정으로 옮길 수 없다. 그건 대본 표기(발음 사전)와 모델 지시(instruct)로 조정한다.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from facetube.captions import align_pieces              # noqa: E402
from facetube.textnorm import to_speech                 # noqa: E402

SR = 16000
PARTICLE = re.compile(r"(은|는|이|가|을|를|의|에|에서|로|으로|와|과|도|만|까지|부터)[,.?!]?$")


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def f0_track(x, hop=0.01, win=0.04, lo=75, hi=450):
    """프레임마다 (시각, F0 Hz 또는 nan, 세기 dB)."""
    n, h = int(win * SR), int(hop * SR)
    out = []
    for s in range(0, len(x) - n, h):
        f = x[s:s + n] * np.hanning(n)
        e = 10 * np.log10(np.mean(f * f) + 1e-12)
        ac = np.correlate(f, f, "full")[n - 1:]
        ac /= ac[0] + 1e-12
        a, b = int(SR / hi), int(SR / lo)
        k = a + int(np.argmax(ac[a:b]))
        out.append((s / SR, SR / k if ac[k] > 0.45 else np.nan, e))
    return np.array(out)


def semis(hz, ref):
    return 12 * np.log2(hz / ref)


def measure(audio, text):
    x = load(audio)
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", " ".join(Path(text).read_text(encoding="utf-8").split())) if s.strip()]
    words = [w for s in sents for w in s.split()]
    starts = [a for a, _ in align_pieces(x, SR, words)]
    tr = f0_track(x)
    t, f0, en = tr[:, 0], tr[:, 1], tr[:, 2]
    floor = np.percentile(en, 95) - 32                     # 무음 기준: 큰 소리보다 32dB 아래(디지털 무음에 끌려가지 않게)
    voiced = f0[~np.isnan(f0) & (en >= floor)]
    med = float(np.median(voiced)) if len(voiced) else 200.0
    f0 = np.where((en >= floor) & (np.abs(12 * np.log2(np.nan_to_num(f0, nan=med) / med)) <= 9), f0, np.nan)   # 옥타브 오검출 제거
    dur = len(x) / SR
    ends = starts[1:] + [dur]
    sil = en < floor                                       # 무음 구간(80ms 이상)을 먼저 찾고, 가장 가까운 어절 경계에 붙인다
    runs, j = [], 0
    while j < len(sil):
        if sil[j]:
            k2 = j
            while k2 < len(sil) and sil[k2]:
                k2 += 1
            if (k2 - j) * 0.01 >= 0.08 and j > 0 and k2 < len(sil):
                runs.append((t[j], t[k2 - 1] + 0.01))
            j = k2
        else:
            j += 1
    used, pause, pstart = set(), [0.0] * len(words), [None] * len(words)
    for i in range(len(words) - 1):
        c = [(b - a, r) for r, (a, b) in enumerate(runs) if r not in used and b >= starts[i + 1] - 0.35 and a <= starts[i + 1] + 0.35]
        if c:
            d, r = max(c)
            used.add(r)
            pause[i], pstart[i] = d, runs[r][0]
    W = []
    for i, w in enumerate(words):
        m = (t >= starts[i]) & (t < ends[i])
        fv = f0[m & ~np.isnan(f0)]
        W.append({"w": w, "t0": round(starts[i], 3), "pause": round(pause[i], 3),
                  "f0": round(float(np.median(semis(fv, med))), 2) if len(fv) else None,
                  "db": round(float(np.max(en[m])) - floor, 1) if m.any() else None})
    S, k = [], 0
    for s in sents:
        ws = W[k:k + len(s.split())]
        k += len(s.split())
        li = k - 1                                         # 이 문장 마지막 어절의 번호
        a = ws[0]["t0"]
        end = pstart[li] if pstart[li] is not None else min(dur, ws[-1]["t0"] + 0.8)
        m = (t >= a) & (t <= end) & ~np.isnan(f0)
        tt, ff = t[m], semis(f0[m], med)
        slope = float(np.polyfit(tt - tt[0], ff, 1)[0]) if len(tt) > 10 else None
        e1, e0 = ff[tt >= end - 0.25], ff[(tt >= end - 0.8) & (tt < end - 0.25)]
        fin = float(np.median(e1) - np.median(e0)) if len(e1) >= 4 and len(e0) >= 4 else None
        syl = len(re.findall("[가-힣]", to_speech(s)))
        talk = (ws[-1]["t0"] - ws[0]["t0"]) - sum(w["pause"] for w in ws[:-1]) + 0.35
        S.append({"text": s, "q": s.endswith("?"), "syl_per_sec": round(syl / max(talk, .3), 2),
                  "range_st": round(float(np.percentile(ff, 90) - np.percentile(ff, 10)), 2) if len(ff) > 10 else None,
                  "declination_st_per_s": round(slope, 2) if slope is not None else None,
                  "final_move_st": round(fin, 2) if fin is not None else None})
    return {"audio": str(audio), "median_f0_hz": round(med, 1), "words": W, "sentences": S, **summarize(W, S)}


def summarize(W, S):
    inner = [w for w in W[:-1] if not re.search(r"[.?!]$", w["w"])]
    comma = [w["pause"] for w in inner if w["w"].endswith(",")]
    plain = [w["pause"] for w in inner if not w["w"].endswith(",")]
    part = [w for w in inner if not w["w"].endswith(",") and PARTICLE.search(w["w"])]
    sent_end = [w["pause"] for w in W[:-1] if re.search(r"[.?!]$", w["w"])]
    nums = [w for w in W if re.search(r"(퍼센트|명|년|점)", w["w"]) and w["f0"] is not None]
    rest = [w for w in W if w not in nums and w["f0"] is not None]
    st = lambda key, xs: round(float(np.mean([s[key] for s in xs if s[key] is not None])), 2) if any(s[key] is not None for s in xs) else None
    return {"summary": {
        "syl_per_sec": st("syl_per_sec", S),
        "range_st": st("range_st", S),
        "declination_st_per_s": st("declination_st_per_s", S),
        "final_move_statement_st": st("final_move_st", [s for s in S if not s["q"]]),
        "final_move_question_st": st("final_move_st", [s for s in S if s["q"]]),
        "pause_comma_s": round(float(np.median(comma)), 3) if comma else None,
        "pause_sentence_s": round(float(np.median(sent_end)), 3) if sent_end else None,
        "pause_inner_s": round(float(np.median(plain)), 3) if plain else None,
        "p_pause_after_particle": round(float(np.mean([w["pause"] >= 0.12 for w in part])), 2) if part else None,
        "number_emphasis_st": round(float(np.mean([w["f0"] for w in nums]) - np.mean([w["f0"] for w in rest])), 2) if nums and rest else None,
        "number_emphasis_db": round(float(np.mean([w["db"] for w in nums]) - np.mean([w["db"] for w in rest])), 2) if nums and rest else None,
    }}


NOTES = {
    "syl_per_sec": "말 속도(음절/초)", "range_st": "음역 폭(반음). 작으면 단조로움", "declination_st_per_s": "문장 안에서 음이 내려가는 정도",
    "final_move_statement_st": "평서문 끝 내림(음수=내림)", "final_move_question_st": "의문문 끝 움직임",
    "pause_comma_s": "쉼표 쉼(초)", "pause_sentence_s": "문장 사이 쉼(초)", "pause_inner_s": "쉼표 없는 어절 사이 쉼(초)",
    "p_pause_after_particle": "조사 뒤에서 끊어 읽는 비율", "number_emphasis_st": "숫자 낱말 음높이 강조(반음)", "number_emphasis_db": "숫자 낱말 세기 강조(dB)"}


def compare(ref, ours):
    a, b = json.load(open(ref))["summary"], json.load(open(ours))["summary"]
    L = ["| 항목 | 기준(아나운서) | 우리 | 차이 |", "|---|---|---|---|"]
    for k, note in NOTES.items():
        x, y = a.get(k), b.get(k)
        d = "" if x is None or y is None else f"{y - x:+.2f}"
        L.append(f"| {note} | {x} | {y} | {d} |")
    return "\n".join(L)


def profile(paths):
    """기준 음성 여러 개의 평균 → 여의도여자 생성·후처리에 쓰는 값."""
    sm = [json.load(open(p))["summary"] for p in paths]
    avg = {k: round(float(np.mean([s[k] for s in sm if s.get(k) is not None])), 3) for k in NOTES if any(s.get(k) is not None for s in sm)}
    return {"from": [str(p) for p in paths], "target": avg,
            "apply": {   # facetube/voice.py 의 voicebox 경로가 읽는다
                "pause_comma_s": avg.get("pause_comma_s"), "pause_sentence_s": avg.get("pause_sentence_s"),
                "comma_after_particle": (avg.get("p_pause_after_particle") or 0) >= 0.5}}


def ab(text, ref, voice="여의도여자", out=ROOT / "voice_ref"):
    """여의도여자로 같은 대본을 '그대로'와 '아나운서 운율 적용' 두 번 만들어 측정·비교한다(Voicebox 필요 → PC에서)."""
    import soundfile as sf
    from facetube import voice as V
    lines = [l for l in Path(text).read_text(encoding="utf-8").splitlines() if l.strip()]
    res = {}
    for tag, on in (("before", False), ("after", True)):
        V.PROSODY["breaks"] = on
        vc = V.Voice(backend="voicebox", voice=voice, instruct=None if on else "차분하고 또렷한 아나운서 톤, 신뢰감 있게, 보통 속도")
        parts = []
        for l in lines:
            x, _ = vc.say(l) if on else (V._trim(V._voicebox(to_speech(l), 1.0, voice, instruct="차분하고 또렷한 아나운서 톤, 신뢰감 있게, 보통 속도")), None)
            parts += [x, np.zeros(int((V.PROSODY["pause_sentence_s"] if on else 0.45) * V.SR), np.float32)]
        wav = Path(out) / f"ours_{tag}.wav"
        sf.write(wav, np.concatenate(parts), V.SR)
        r = measure(wav, text)
        (Path(out) / f"ours_{tag}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        res[tag] = Path(out) / f"ours_{tag}.json"
    md = ["# 여의도여자 운율 비교", "", "## 적용 전", compare(ref, res["before"]), "", "## 적용 후 (끊어 읽기 + 쉼 길이 + 지시문)", compare(ref, res["after"]),
          "", f"들어 보기: `{out}/ours_before.wav` / `{out}/ours_after.wav`"]
    (Path(out) / "ab_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("measure"); m.add_argument("audio"); m.add_argument("text"); m.add_argument("-o", required=True)
    c = sp.add_parser("compare"); c.add_argument("ref"); c.add_argument("ours")
    p = sp.add_parser("profile"); p.add_argument("refs", nargs="+"); p.add_argument("-o", required=True)
    b = sp.add_parser("ab"); b.add_argument("text"); b.add_argument("--ref", required=True); b.add_argument("--voice", default="여의도여자")
    a = ap.parse_args()
    if a.cmd == "measure":
        r = measure(a.audio, a.text)
        Path(a.o).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(r["summary"], ensure_ascii=False, indent=1))
    elif a.cmd == "compare":
        print(compare(a.ref, a.ours))
    elif a.cmd == "ab":
        ab(a.text, a.ref, a.voice)
    else:
        Path(a.o).write_text(yaml.safe_dump(profile(a.refs), allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(open(a.o, encoding="utf-8").read())


if __name__ == "__main__":
    main()
