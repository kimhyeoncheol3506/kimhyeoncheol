"""쇼츠 자막: 13자 안팎 조각 나누기 + 음성인식 시각으로 조각별 시작·끝 맞추기.

- split_pieces: 어절 단위로 나눈다. 쉼표/문장 끝에서 끊는 것을 선호하고 [[강조]]는 쪼개지 않는다.
- align_pieces: 문장 음성을 음성인식해 글자별 시각을 얻고, 조각의 '읽는 소리' 음절 비율로 시작 시각을 정한다.
  (숫자는 화면 표기 405잔 ↔ 소리 사백오 잔 이 다르므로 소리 기준으로 센다)
"""
import re
import numpy as np
from .textnorm import strip_markup, to_speech

TOK = re.compile(r"\[\[.+?\]\]\S*|\S+")


def _plain_len(w):
    return len(strip_markup(w))


def split_pieces(text, max_chars=13, hard_max=15):
    words = TOK.findall(text.strip())
    n = len(words)
    if n == 0:
        return []
    INF = 1e9
    best = [INF] * (n + 1)
    prev = [0] * (n + 1)
    best[0] = 0
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            chunk = words[i:j]
            L = sum(_plain_len(w) for w in chunk) + (len(chunk) - 1)
            if L > hard_max and len(chunk) > 1:
                break
            cost = (max_chars - L) ** 2 if L <= max_chars else (L - max_chars) * 40
            last = strip_markup(chunk[-1])
            if re.search(r"[,.?!…]$", last):
                cost -= 6                       # 문장부호에서 끊기
            if j < n and L < 4:
                cost += 30                      # 너무 짧은 조각 금지
            if j == n and L < 4 and j - i == 1 and i > 0:
                cost += 30                      # 짧은 꼬리 금지
            if j < n and re.search(r"(은|는|이|가|을|를|의|에|에서|로|와|과)$", last) and L >= 6:
                cost -= 1                       # 조사 뒤 끊기 소폭 선호
            if best[i] + cost < best[j]:
                best[j] = best[i] + cost
                prev[j] = i
    out, j = [], n
    while j > 0:
        i = prev[j]
        out.append(" ".join(words[i:j]))
        j = i
    return out[::-1]


def char_times(samples, sr):
    """음성인식으로 글자별 시각(초) 목록과 전체 길이를 돌려준다."""
    from .voice import asr
    x = np.asarray(samples, dtype=np.float32)
    if sr != 16000:
        x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * 16000 / sr)), np.arange(len(x)), x).astype(np.float32)
    r = asr()
    s = r.create_stream()
    s.accept_waveform(16000, x)
    r.decode_stream(s)
    toks, ts = list(s.result.tokens), list(s.result.timestamps)
    dur = len(x) / 16000
    times = []
    for k, (tok, t) in enumerate(zip(toks, ts)):
        chars = re.sub(r"[^가-힣A-Za-z0-9]", "", tok)
        nxt = ts[k + 1] if k + 1 < len(ts) else min(dur, t + 0.3)
        span = max(0.0, min(nxt - t, 0.45))
        for q in range(len(chars)):
            times.append(t + span * q / max(1, len(chars)))
    return times, dur


def _syl(piece):
    return max(1, len(re.findall(r"[가-힣A-Za-z0-9]", to_speech(piece))))


def align_pieces(samples, sr, pieces):
    """조각별 (시작, 끝) 초를 돌려준다. 음성인식이 완전히 틀려도 비율 배분으로 안전하게 동작."""
    dur = len(samples) / sr
    sy = [_syl(p) for p in pieces]
    total = sum(sy)
    try:
        times, adur = char_times(samples, sr)
    except Exception:
        times = []
    starts, acc = [], 0
    for k in range(len(pieces)):
        frac = acc / total
        if times and len(times) >= 3:
            idx = min(len(times) - 1, int(round(frac * len(times))))
            t = times[idx] if k > 0 else 0.0
        else:
            t = dur * frac
        starts.append(max(0.0, min(dur, t)))
        acc += sy[k]
    for k in range(1, len(starts)):             # 단조 증가 보장
        starts[k] = max(starts[k], starts[k - 1] + 0.12)
    try:
        anchors = whisper_anchors(samples, sr, pieces)
    except Exception:
        anchors = {}
    starts = _snap_to_pauses(samples, sr, pieces, starts, sy, dur, anchors)
    ends = starts[1:] + [dur]
    return list(zip(starts, ends))


def speech_regions(samples, sr, min_sil=0.18):
    """쉼(min_sil초 이상 조용함)으로 나뉜 말소리 구간 [(시작, 끝)]."""
    h = max(1, int(0.02 * sr))
    n = len(samples) // h
    if n == 0:
        return []
    r = np.sqrt(np.mean(np.asarray(samples[:n * h], dtype="float32").reshape(n, h) ** 2, axis=1))
    thr = max(1e-4, 0.12 * float(np.percentile(r, 95)))
    v = r > thr
    regs, s, sil = [], None, 10 ** 6
    for i, b in enumerate(v):
        if b:
            if s is None or sil * 0.02 >= min_sil:
                if s is not None:
                    regs.append((s, last))
                s = i * 0.02
            sil, last = 0, (i + 1) * 0.02
        else:
            sil += 1
    if s is not None:
        regs.append((s, last))
    return [g for g in regs if g[1] - g[0] >= 0.1]


_WM = []


def _whisper():
    if not _WM:
        import os
        from faster_whisper import WhisperModel
        _WM.append(WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4))
    return _WM[0]


def _chars(t):
    return re.findall(r"[가-힣A-Za-z0-9]", t)


def whisper_anchors(samples, sr, pieces):
    """두 번째 의견: Whisper 낱말 시각으로 조각 첫 글자가 들린 시각을 찾는다 {조각 번호: 초}.
    음절 비율만으로는 '약 … 5개월.'처럼 천천히 끊어 읽은 곳에서 묶음을 한 칸 잘못 고르곤 했다(2026-11-18 코스피 편).
    Whisper 는 쉼 뒤 첫 낱말을 쉼 앞쪽으로 당겨 적으므로, 그 시각이 말소리 밖이거나 앞 말소리 끝자락이면 다음 말소리 시작으로 옮긴다."""
    import scipy.signal as S
    x = np.asarray(samples, dtype=np.float32)
    if sr != 16000:
        x = S.resample_poly(x, 16000, sr).astype(np.float32)
    segs, _ = _whisper().transcribe(x, language="ko", beam_size=5, vad_filter=False,
                                    condition_on_previous_text=False, word_timestamps=True)
    ws = [(w.start, w.end, w.word.strip()) for sg in segs for w in (sg.words or [])]
    merged = []                                   # "4" ",968" ".48" → 한 낱말(숫자 읽기가 맞게)
    for a, b, w in ws:
        if merged and re.match(r"^[,.%]?\d|^%", w) and re.search(r"\d[,.]?$", merged[-1][2]):
            merged[-1] = (merged[-1][0], b, merged[-1][2] + w)
        else:
            merged.append((a, b, w))
    hc, ht = [], []
    for a, b, w in merged:
        cs = _chars(to_speech(w))
        for q, ch in enumerate(cs):
            hc.append(ch)
            ht.append(a + (b - a) * q / max(1, len(cs)))
    sc, owner = [], []
    for k, p in enumerate(pieces):
        cs = _chars(to_speech(strip_markup(p)))
        sc += cs
        owner += [k] * len(cs)
    import difflib
    m = {}
    for blk in difflib.SequenceMatcher(None, sc, hc, autojunk=False).get_matching_blocks():
        for q in range(blk.size):
            m[blk.a + q] = blk.b + q
    regs = speech_regions(samples, sr)
    out, first = {}, {}
    for i, k in enumerate(owner):
        first.setdefault(k, i)
    for k, i0 in first.items():
        for i in (i0, i0 + 1):                    # 첫 글자(또는 둘째 글자)가 맞아떨어질 때만
            if i in m and owner[i] == k:
                t = ht[m[i]] - (0.06 if i > i0 else 0)
                inside = [(a, b) for a, b in regs if a - 0.05 <= t <= b + 0.05]
                nxt = [a for a, _ in regs if a > t]
                if nxt and nxt[0] - t < 1.6 and (not inside or (inside[0][1] - t < 0.35 and nxt[0] - inside[0][1] >= 0.22)):   # 0.22초 미만 틈은 낱말 속(받침·된소리) 끊김일 수 있어 옮기지 않는다
                    t = nxt[0]
                out[k] = t
                break
    return out


# 동적계획법 가중치: 묶음 안 쉼 벌점, 문장 끝·쉼표·그 밖에서 끊을 때 가감점(쉼 길이 g 곱)
SNAP_W = {"inner": 0.05, "sent": -0.05, "comma": -0.02, "none": 0.01, "anchor": 0.1}


def _snap_to_pauses(samples, sr, pieces, starts, sy, dur, anchors=None):
    """숫자가 많은 문장은 음성인식 글자 수와 실제 읽는 음절 수가 달라 자막 시각이 1초 넘게 앞서곤 했다(2026-11-17 코스피 편).
    실제 쉼으로 나뉜 말소리 구간들에 낱말 묶음을 나눠 맞춘다(동적계획법: 구간 길이 비율 ≈ 음절 수 비율, 문장부호에서 끊기면 가산점).
    한 묶음이 쉼 여러 개를 품을 수도 있다(긴 숫자 중간의 숨). 묶음 안에서는 말소리 시간에 음절 수 비율로 나눈다."""
    try:
        regs = speech_regions(samples, sr)
    except Exception:
        return starts
    N, R = len(pieces), len(regs)
    if R < 2 or N < 2 or R > 3 * N:
        return starts
    tot_s = float(sum(sy)) or 1.0
    span = regs[-1][1] - regs[0][0] or 1.0
    cs = [0]
    for v in sy:
        cs.append(cs[-1] + v)
    punct = [bool(re.search(r"[.,?!…:;]$", p)) for p in pieces]
    INF = float("inf")
    best = [[INF] * (N + 1) for _ in range(R + 1)]
    back = [[None] * (N + 1) for _ in range(R + 1)]
    best[0][0] = 0.0
    for r in range(R):
        for k in range(N):
            if best[r][k] == INF:
                continue
            for r2 in range(r + 1, R + 1):
                d = (regs[r2 - 1][1] - regs[r][0]) / span
                for k2 in range(k + 1, N + 1):
                    if (N - k2) < 0 or (R - r2) > 0 and k2 == N:
                        continue
                    sfrac = (cs[k2] - cs[k]) / tot_s
                    inner = sum(min(1.0, regs[q + 1][0] - regs[q][1]) for q in range(r, r2 - 1))
                    c = (d - sfrac) ** 2 + SNAP_W["inner"] * inner          # 묶음 안에 쉼을 품으면 벌점(쉼 길이만큼)
                    if k2 < N and r2 < R:
                        g = min(1.0, regs[r2][0] - regs[r2 - 1][1])
                        endp = pieces[k2 - 1][-1:]
                        c += SNAP_W["sent"] * g if endp in ".?!…" else (SNAP_W["comma"] * g if endp in ",:;" else SNAP_W["none"] * g)
                    if anchors and k in anchors and k > 0:   # 묶음 첫 조각이 Whisper 로 들린 시각과 멀면 벌점
                        c += SNAP_W["anchor"] * min(1.0, abs(regs[r][0] - anchors[k]))
                    v = best[r][k] + c
                    if v < best[r2][k2]:
                        best[r2][k2] = v
                        back[r2][k2] = (r, k)
    if best[R][N] == INF:
        return starts
    groups, r, k = [], R, N
    while (r, k) != (0, 0):
        pr, pk = back[r][k]
        groups.append((pr, r, pk, k))
        r, k = pr, pk
    groups.reverse()
    out = list(starts)
    for r0, r1, k0, k1 in groups:
        rs = regs[r0:r1]
        voiced = sum(b - a for a, b in rs) or 1.0
        tot = sum(sy[k0:k1]) or 1
        acc = 0
        for k in range(k0, k1):
            want = voiced * acc / tot                # 말소리 시간 기준 위치 → 실제 시각(쉼 건너뜀)
            t = rs[0][0]
            for a, b in rs:
                if want <= (b - a) + 1e-6:
                    t = a + want
                    break
                want -= (b - a)
                t = b
            if anchors and k in anchors and k > k0 and rs[0][0] <= anchors[k] <= rs[-1][1] and abs(anchors[k] - t) < 0.8:
                t = anchors[k]                       # 묶음 안 낱말도 Whisper 로 들린 시각이 있으면 그쪽(숫자 많은 문장에서 음절 비율이 어긋남)
            out[k] = t
            acc += sy[k]
    out[0] = max(0.0, out[0] - 0.02)
    for k in range(1, len(out)):
        out[k] = max(out[k], out[k - 1] + 0.12)
    return [max(0.0, min(dur, t)) for t in out]
