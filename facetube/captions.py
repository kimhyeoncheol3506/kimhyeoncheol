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
    ends = starts[1:] + [dur]
    return list(zip(starts, ends))
