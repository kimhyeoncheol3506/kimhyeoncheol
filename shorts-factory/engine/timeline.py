"""[3단계] 편집 규칙(rules.yaml) → 타임라인 명세(JSON/TOML).
컷 / 자막 / 줌 / 효과음 / BGM / CTA / 아웃트로 위치를 전부 계산한다."""
import math
import re
from pathlib import Path

from .hooks import typing_timeline

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
VID_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}
PRICE_RE = re.compile(r"\d[\d,]*원")
NUM_RE = re.compile(r"\d[\d,.]*(?:%|초|가지|배|잔|개)?")


def split_lines(text, max_chars):
    """한 줄 max_chars 이내로 단어 단위 분할."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            while len(w) > max_chars:  # 한 단어가 너무 길면 강제로 자름
                lines.append(w[:max_chars])
                w = w[max_chars:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


def find_emphasis(text, rules):
    """숫자/가격/감탄사 위치 찾기 → (글자 위치, 종류, 줌배율)"""
    em = rules["editing"]["emphasis"]
    m = PRICE_RE.search(text)
    if m:
        return m.start(), "price", em["zoom_price"]
    m = NUM_RE.search(text)
    if m:
        return m.start(), "number", em["zoom_number"]
    for w in em["exclaims"]:
        i = text.find(w)
        if i >= 0:
            return i, "exclaim", em["zoom_exclaim"]
    return None


def highlight_terms(ctx, hook_text, rules):
    terms = [ctx[f"kw{i}"] for i in (1, 2, 3)] + [ctx["p"]]
    terms += [w for w in rules["hooks"]["power_words"] if w in hook_text]
    terms += [w for w in rules["editing"]["emphasis"]["exclaims"]]
    return sorted(set(t for t in terms if t), key=len, reverse=True)


def find_highlights(text, terms):
    found = [m.group(0) for m in PRICE_RE.finditer(text)]
    found += [m.group(0) for m in NUM_RE.finditer(text) if not any(m.group(0) in f for f in found)]
    found += [t for t in terms if t in text]
    return found


def collect_media(media_dir):
    """media 폴더의 사진/영상. 파일명이 hook_/intro_/feature_/price_/cta_ 로 시작하면 해당 구간에 우선 배치."""
    if not media_dir:
        return {}
    by = {"any": []}
    for f in sorted(Path(media_dir).iterdir()):
        ext = f.suffix.lower()
        if ext not in IMG_EXT | VID_EXT:
            continue
        kind = "image" if ext in IMG_EXT else "video"
        sec = f.name.split("_")[0].lower()
        key = sec if sec in ("hook", "intro", "feature", "price", "cta") else "any"
        by.setdefault(key, []).append({"kind": kind, "path": str(f.resolve())})
    return by


def build_timeline(ctx, hook, script, rules, media=None, voice=None):
    v, ed = rules["video"], rules["editing"]
    dur = float(v["duration"])
    max_chars = ed["subtitle"]["max_chars"]
    terms = highlight_terms(ctx, hook["text"], rules)
    subs, emph, typing_sfx = [], [], []

    # ── 1) 후킹 자막: 타이핑 효과 ─────────────────────────────
    typing = typing_timeline(hook["text"], rules)
    for ev in typing:
        hit = find_emphasis(ev["word"], rules)
        subs.append({"start": ev["start"], "end": ev["end"], "text": ev["shown"], "new_word": ev["word"],
                     "style": "hook", "kind": "typing", "highlights": find_highlights(ev["shown"], terms)})
        if hit:
            emph.append({"t": ev["start"], "kind": hit[1], "zoom": hit[2], "word": ev["word"]})
        else:
            typing_sfx.append(ev["start"])

    # ── 2) 본문 자막: 한 줄 15자 이내로 쪼개 시간 배분 ───────────
    phrases = [dict(p, section=s["id"]) for s in script["sections"] if s["id"] != "hook" for p in s["phrases"]]
    for p in phrases:
        lines = split_lines(p["text"], max_chars)
        total = sum(len(l) for l in lines)
        t = p["start"]
        for l in lines:
            d = (p["end"] - p["start"]) * len(l) / total
            subs.append({"start": round(t, 3), "end": round(t + d, 3), "text": l, "style": "main",
                         "kind": "line", "section": p["section"], "highlights": find_highlights(l, terms)})
            hit = find_emphasis(l, rules)
            if hit:
                emph.append({"t": round(t + d * hit[0] / max(1, len(l)), 3), "kind": hit[1],
                             "zoom": hit[2], "word": l})
            t += d

    # 혜택 정리 배지 (말하지 않고 화면에만)
    for s in script["sections"]:
        for b in s.get("badges", []):
            for l in split_lines(b, max_chars):
                subs.append({"start": s["start"], "end": s["end"], "text": l, "style": "badge",
                             "kind": "badge", "section": s["id"], "highlights": find_highlights(l, terms)})

    # ── 3) 컷: 말이 바뀌는 순간(공백 ≥ min_gap) + 구간 경계 + 아웃트로 ───
    cut_conf = ed["cut"]
    outro_start = round(dur - ed["outro"]["duration"], 3)
    bounds = {0.0, outro_start}
    bounds |= {float(s["start"]) for s in script["sections"]}
    bounds |= {float(e["start"]) for e in typing}  # 후킹: 단어가 뜰 때마다 컷
    for a, b in zip(phrases, phrases[1:]):
        if b["start"] - a["end"] >= cut_conf["min_gap_sec"] - 1e-6:
            bounds.add(b["start"])
    if voice:
        bounds |= {round(x, 3) for x in voice.get("gap_cuts", []) if 0 < x < outro_start}
    bounds = sorted(b for b in bounds if b < dur)
    # 0.4초보다 짧은 자투리 컷은 앞 컷에 합친 뒤, max_cut 을 넘는 컷은 앵글을 바꿔 분할
    merged = []
    for a, b in zip(bounds, bounds[1:] + [dur]):
        if merged and b - a < 0.4 and a < outro_start:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    segs = []
    for a, b in merged:
        if b - a > cut_conf["max_cut_sec"] and a < outro_start:
            n = math.ceil((b - a) / cut_conf["target_cut_sec"])
            segs += [(a + (b - a) * i / n, a + (b - a) * (i + 1) / n) for i in range(n)]
        else:
            segs.append((a, b))

    sec_of = lambda t: next(s for s in reversed(script["sections"]) if s["start"] <= t + 1e-6)
    media = media or {}
    used_any = 0
    played = {}  # 같은 영상을 여러 컷에 쓰면 이어서 재생
    cuts, sec_count = [], {}
    for i, (a, b) in enumerate(segs):
        a, b = round(a, 3), round(b, 3)
        if a >= outro_start:
            cuts.append({"id": i + 1, "start": a, "end": b, "section": "outro", "shot": "로고 + 구매 버튼",
                         "source": {"kind": "outro"}, "zoom": {"from": 1.0, "to": 1.0, "punches": []}})
            continue
        s = sec_of(a)
        k = sec_count.get(s["id"], 0)
        sec_count[s["id"]] = k + 1
        shot = s["shots"][k % len(s["shots"])] if s["shots"] else ""
        pool = media.get(s["id"]) or []
        if pool:
            src = pool[k % len(pool)]
        elif media.get("any"):
            src = media["any"][used_any % len(media["any"])]
            used_any += 1
        else:
            src = {"kind": "placeholder", "colors": ed["placeholder"]["colors"].get(s["id"], ["333333", "777777"])}
        if src["kind"] == "video":
            src = dict(src, offset=round(played.get(src["path"], 0.0), 3))
            played[src["path"]] = src["offset"] + (b - a)
        push = s.get("push_in") if (s.get("push_in") and k % 2 == 1) else 1.02
        punches = [{"t": round(e["t"] - a, 3), "scale": e["zoom"], "kind": e["kind"]}
                   for e in emph if a <= e["t"] < b]
        cuts.append({"id": i + 1, "start": a, "end": b, "section": s["id"], "shot": shot, "source": src,
                     "zoom": {"from": 1.0, "to": push, "punches": punches}})

    # ── 4) 효과음: 컷 "띵/띠용", 키워드 "팡", 후킹 타이핑 "탁" ─────────
    sx = ed["sfx"]
    cand = []
    for e in emph:
        cand.append({"t": e["t"], "type": "keyword", "anchor": f"강조:{e['word']}", "prio": 3})
    for t in typing_sfx:
        cand.append({"t": t, "type": "typing", "anchor": "후킹 타이핑", "prio": 2})
    hook_end = script["sections"][0]["end"]
    alt = 0
    for c in cuts[1:]:
        if c["start"] < hook_end and not sx["hook_cut_sfx"]:
            continue
        cand.append({"t": c["start"], "type": "cut" if alt % 2 == 0 else "cut_alt",
                     "anchor": f"컷{c['id']}", "prio": 1})
        alt += 1
    kept, dropped = [], []
    for c in sorted(cand, key=lambda x: -x["prio"]):
        if all(abs(c["t"] - k["t"]) >= sx["min_spacing_sec"] for k in kept):
            kept.append(c)
        else:
            dropped.append(c)
    sfx = sorted(({"t": round(c["t"], 3), "type": c["type"], "file": sx["files"][c["type"]],
                   "anchor": c["anchor"], "volume": sx["volume"]} for c in kept), key=lambda x: x["t"])

    # ── 5) CTA 버튼 / 아웃트로 ─────────────────────────────────
    cta = dict(ed["cta"], end=dur)
    outro = dict(ed["outro"], start=outro_start, end=dur, brand=ctx["brand"])
    bgm = dict(ed["bgm"], end=dur)

    return {
        "meta": {"product": ctx["product"], "target": ctx["target"], "benefits": ctx["benefits"],
                 "hook": hook["text"], "hook_type": hook["type_ko"], "rules_file": rules["_path"]},
        "video": {"width": v["width"], "height": v["height"], "fps": v["fps"], "duration": dur},
        "cuts": cuts,
        "subtitles": subs,
        "zoom_events": emph,
        "sfx": sfx,
        "sfx_dropped": [{"t": round(c["t"], 3), "type": c["type"], "reason": "다른 효과음과 너무 가까움"} for c in dropped],
        "bgm": bgm,
        "cta": cta,
        "outro": outro,
        "voice": voice,
    }


# ── TOML 저장 (외부 라이브러리 없이) ────────────────────────────────
def _tv(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, list):
        return "[" + ", ".join(_tv(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f'"{k}" = {_tv(x)}' for k, x in v.items() if x is not None) + " }"
    return '""'


def to_toml(tl):
    out = []
    for key, val in tl.items():
        if val is None:
            continue
        if isinstance(val, dict):
            out.append(f"[{key}]")
            out += [f'"{k}" = {_tv(x)}' for k, x in val.items() if x is not None]
            out.append("")
        elif isinstance(val, list) and val and isinstance(val[0], dict):
            for item in val:
                out.append(f"[[{key}]]")
                out += [f'"{k}" = {_tv(x)}' for k, x in item.items() if x is not None]
                out.append("")
        else:
            out.append(f'"{key}" = {_tv(val)}')
    return "\n".join(out) + "\n"
