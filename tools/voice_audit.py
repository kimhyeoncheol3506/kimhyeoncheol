"""목소리 듣기 검수(매니저용, 2026-11-10 현철님: "이상하게 발음하거나 더듬는 말을 하면 최종 영상 전에 니가 알아서 수정").

장면별 TTS 원본(_work/tts/*.wav + *.json의 spoken)을 다시 받아 적어서 아래를 찾는다.
  1) 빠진 말·바뀐 말: 대본(읽을 소리)과 들린 말을 음절 단위로 맞춰 어긋난 낱말
  2) 더듬기: 들린 말에서 같은 음절·낱말이 바로 이어 반복되는데 대본에는 그렇게 없는 곳
  3) 문장 중간의 긴 멈춤(0.7초 넘게)
  4) 너무 빠르거나 느린 문장(초당 음절)
사용: python tools/voice_audit.py <tts_dir> [--out report.md]
결과 표의 '들린 말'은 음성 인식 결과라 인식기 실수도 섞인다 → 같은 곳을 앞뒤로 잘라 한 번 더 인식해 둘 다 어긋날 때만 '확실'로 표시한다.
"""
import argparse, difflib, glob, json, os, re, sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from facetube.voice import transcribe  # noqa: E402
from facetube.textnorm import cer, hangul_only, to_speech  # noqa: E402

IGNORE = {("에이아이", "ai"), ("에이피아이", "api")}   # 인식기가 영문으로 적는 흔한 경우


def _norm_vowel(ch):
    """인식기가 자주 헷갈리는 소리(ㅐ/ㅔ, ㅖ/ㅔ, ㅒ/ㅔ)를 같은 것으로 본다(발음상 같음)."""
    c = ord(ch) - 0xAC00
    if not 0 <= c < 11172:
        return ch
    L, V, T = c // 588, (c % 588) // 28, c % 28
    V = {1: 5, 3: 5, 7: 5}.get(V, V)          # ㅐ→ㅔ, ㅒ→ㅔ, ㅖ→ㅔ
    return chr(0xAC00 + L * 588 + V * 28 + T)


def _syl(s):
    return "".join(_norm_vowel(c) for c in hangul_only(s))


def _rep(text, spoken=""):
    """들린 말에서 2~6음절 덩어리가 바로 두 번 이어진 곳(대본에 없는 반복 = 더듬기)."""
    h, r = _syl(text), _syl(spoken)
    out = []
    for n in range(6, 1, -1):
        for i in range(0, len(h) - 2 * n + 1):
            a = h[i:i + n]
            if h[i + n:i + 2 * n] == a and a + a not in r and not any(a in o for o in out):
                out.append(a + "·" + a)
    return out


def _pauses(x, sr, thr=0.012, min_gap=1.0):
    env = np.abs(x)
    win = int(sr * 0.02)
    if len(env) < win * 3:
        return []
    e = np.convolve(env, np.ones(win) / win, mode="same") > thr
    idx = np.where(e)[0]
    if len(idx) == 0:
        return []
    a, b = idx[0], idx[-1]
    gaps, run = [], 0
    for i in range(a, b, win):
        if not e[i]:
            run += win
        else:
            if run / sr >= min_gap:
                gaps.append(round((i - run) / sr, 2))
            run = 0
    return gaps


def _diffs(ref, hyp):
    r, h = _syl(ref), _syl(hyp)
    sm = difflib.SequenceMatcher(None, r, h, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        a, b = r[max(0, i1 - 2):i2 + 2], h[max(0, j1 - 2):j2 + 2]
        if (r[i1:i2], h[j1:j2].lower()) in IGNORE:
            continue
        out.append((op, a, b, i2 - i1))
    return out


def _drops(spoken, hyp):
    """대본에는 있는데 들린 말에서 통째로 빠진 2음절 이상 덩어리(바뀐 말이 아니라 '없어진' 말)."""
    r, h = _syl(spoken), _syl(hyp)
    sm = difflib.SequenceMatcher(None, r, h, autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if (op == "delete" and i2 - i1 >= 2) or (op == "replace" and (i2 - i1) - (j2 - j1) >= 2):
            out.append((i1, i2, r[i1:i2]))
    return out, len(r)


def _confirm_drop(x, sr, i1, i2, n_syl, word):
    """빠진 말 근처(앞뒤 1.3초)만 잘라 다시 듣는다. 거기서도 안 들리면 진짜 빠짐."""
    dur = len(x) / sr
    t0 = max(0.0, (i1 / max(1, n_syl)) * dur - 1.3)
    t1 = min(dur, (i2 / max(1, n_syl)) * dur + 1.3)
    seg = _syl(to_speech(transcribe(x[int(t0 * sr):int(t1 * sr)], sr)))
    m = difflib.SequenceMatcher(None, word, seg, autojunk=False).find_longest_match(0, len(word), 0, len(seg))
    return m.size < max(2, int(len(word) * 0.6)), round(t0, 1)


def _current_spoken(project):
    """대본(yaml)의 지금 문장들(읽을 소리). 옛 빌드 캐시 파일은 검사에서 뺀다."""
    import yaml
    p = yaml.safe_load(open(project, encoding="utf-8"))
    out = set()
    for sc in p.get("scenes", []):
        for part in re.split(r"(?<=[.?!])\s+", sc.get("say", "")):
            if part.strip():
                out.add(_syl(to_speech(part)))
    return out


def audit(tts_dir, project=None):
    keep = _current_spoken(project) if project else None
    rows = []
    for jf in sorted(glob.glob(os.path.join(tts_dir, "*.json"))):
        d = json.load(open(jf, encoding="utf-8"))
        wav = jf[:-5] + ".wav"
        if not os.path.exists(wav) or not d.get("spoken"):
            continue
        x, sr = sf.read(wav)
        if x.ndim > 1:
            x = x.mean(1)
        spoken = d["spoken"]
        if keep is not None and not any(k and (k in _syl(spoken) or _syl(spoken) in k) for k in keep):
            continue
        hyp = to_speech(transcribe(x, sr))       # 인식기가 적은 숫자(49점)도 읽는 소리(사십구 점)로 맞춰 비교
        n = len(x)
        # 두 번째 듣기: 앞 0.15초를 빼고 다시(경계 효과를 줄여 인식기 실수와 진짜 실수를 가른다)
        hyp2 = to_speech(transcribe(x[int(0.15 * sr):], sr)) if n > sr else hyp
        c1, c2 = cer(spoken, hyp), cer(spoken, hyp2)
        sylps = len(_syl(spoken)) / max(0.1, n / sr)
        reps = _rep(hyp, spoken)
        reps2 = _rep(hyp2, spoken)
        stutter = sorted(set(reps) & set(reps2)) or sorted(set(reps + reps2)) if (reps or reps2) else []
        diffs = [df for df in _diffs(spoken, hyp) if df[3] >= 1]
        diffs2 = {(df[1]) for df in _diffs(spoken, hyp2)}
        sure = [df for df in diffs if df[1] in diffs2]          # 두 번 다 어긋난 곳
        drops = []
        d1, nsyl = _drops(spoken, hyp)
        d2, _ = _drops(spoken, hyp2)
        both = [d for d in d1 if any(abs(d[0] - e[0]) <= 2 for e in d2)]
        for i1, i2, w in both:
            gone, at = _confirm_drop(x, sr, i1, i2, nsyl, w)
            if gone:
                drops.append(f"{w}(~{at}초)")
        rows.append({
            "drops": drops,
            "file": os.path.basename(wav), "spoken": spoken, "heard": hyp, "cer": round(min(c1, c2), 3),
            "stutter": stutter, "sure": sure, "maybe": [df for df in diffs if df not in sure],
            "pauses": _pauses(x, sr, min_gap=1.0 + 0.0 * spoken.count(".")), "sylps": round(sylps, 1), "dur": round(n / sr, 2)})
    return rows


def score(r):
    s = 4 * len(r.get("drops", [])) + 3 * len(r["stutter"]) + 1.5 * len(r["pauses"]) + r["cer"] * 3
    if r["sylps"] > 8.5 or r["sylps"] < 3.0:
        s += 2
    return s


def report(rows, top=30):
    rows = sorted(rows, key=score, reverse=True)
    L = ["# 목소리 듣기 검수", "", f"- 장면 음성 {len(rows)}개를 두 번씩 다시 받아 적어 대본과 맞춤.",
         "- '확실' = 두 번 다 어긋난 곳(진짜 발음 문제일 가능성 높음). '더듬기' = 대본에 없는 반복.", "",
         "| 점수 | 파일 | 대본(읽을 소리) | 빠진 말(세 번 들어도 없음) | 더듬기 | 긴 멈춤(초) | 음절/초 | 참고: 두 번 다 다르게 들린 곳(이름 착각 포함) |", "|---|---|---|---|---|---|---|---|"]
    for r in rows[:top]:
        sc = score(r)
        if sc < 3.0:
            break
        sure = "; ".join(f"'{a}'→'{b}'" for _, a, b, _ in r["sure"][:4]) or "-"
        L.append(f"| {sc:.1f} | {r['file']} | {r['spoken'][:70]} | {', '.join(r.get('drops', [])) or '-'} | {', '.join(r['stutter']) or '-'} | "
                 f"{', '.join(map(str, r['pauses'])) or '-'} | {r['sylps']} | {sure} |")
    flagged = [r for r in rows if r["stutter"] or r.get("drops") or r["pauses"]]
    L += ["", f"고칠 후보 {len(flagged)}개 / 전체 {len(rows)}개"]
    return "\n".join(L), flagged


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tts_dir")
    ap.add_argument("--out")
    ap.add_argument("--json")
    ap.add_argument("--project", help="지금 대본 yaml — 주면 옛 빌드 캐시 파일은 빼고 검사")
    a = ap.parse_args()
    rows = audit(a.tts_dir, a.project)
    md, flagged = report(rows)
    print(md)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
