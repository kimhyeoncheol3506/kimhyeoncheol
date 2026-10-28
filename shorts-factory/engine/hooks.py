"""[1단계] 후킹 엔진: 5가지 공식 × 3문장 생성, 클릭률 점수 순위, 타이핑 타임라인."""
import re

HOOK_TYPES = [
    ("curiosity", "호기심 자극형"),
    ("problem", "문제 제시형"),
    ("price_shock", "가격 충격형"),
    ("rebuttal", "반박형"),
    ("number", "숫자 약속형"),
]
TYPE_KO = dict(HOOK_TYPES)


class _Missing(dict):
    def __missing__(self, key):
        raise KeyError(key)


def fmt_won(n):
    return f"{int(n):,}원"


def lexicon_entry(benefit, rules):
    lex = rules.get("benefit_lexicon", {})
    if benefit in lex:
        return dict(lex[benefit])
    return {  # 사전에 없는 혜택은 일반 표현으로
        "keyword": benefit, "pain": f"{benefit} 아쉬웠던 거", "old": f"{benefit} 별로인 거",
        "claim": f"{benefit}까지 완벽", "scene": f"써보면 {benefit} 바로 느낌",
        "short": benefit, "problem_q": f"{benefit} 아쉬웠죠?",
    }


def short_product(product):
    words = product.split()
    return words[-1] if len(product) > 6 and words else product


def short_target(target):
    m = re.match(r"(\d+대)", target)
    return m.group(1) if m else target.split()[0]


def build_context(product, target, benefits, rules, price=None, orig_price=None,
                  brand=None, short=None):
    benefits = (list(benefits) + ["가격", "편리함", "디자인"])[:3]
    lx = [lexicon_entry(b, rules) for b in benefits]
    ctx = {
        "product": product, "p": short or short_product(product),
        "target": target, "t": short_target(target),
        "brand": brand or product,
        "benefits": benefits, "lexicon": lx,
        "pain": lx[0]["pain"], "pain_q": lx[0]["problem_q"],
        "old": lx[0]["old"], "old2": lx[1]["old"],
    }
    for i, e in enumerate(lx, 1):
        ctx[f"kw{i}"] = e["keyword"]
        ctx[f"b{i}_claim"] = e["claim"]
        ctx[f"b{i}_scene"] = e["scene"]
        ctx[f"s{i}"] = e["short"]
    if price:
        ctx["price"] = fmt_won(price)
        ctx["price_value"] = int(price)
        man = int(price) // 10000
        ctx["price_short"] = (f"{man}만원대" if man > 1 else "만원대") if man else f"{int(price) // 1000}천원대"
    if orig_price:
        ctx["orig_price"] = fmt_won(orig_price)
    if price and orig_price and orig_price > price:
        ctx["discount"] = round((1 - price / orig_price) * 100)
    return ctx


def render_template(tpl, ctx):
    try:
        return tpl.format_map(_Missing(ctx)).strip()
    except KeyError:  # 가격 등 정보가 없으면 그 템플릿은 건너뜀
        return None


def score_hook(text, htype, ctx, h):
    """규칙 기반 클릭률 예측 점수(0~99). 근거도 함께 돌려준다."""
    sc = h["score"]
    reasons = []
    s = sc["base"] * h["type_weights"].get(htype, 1.0)
    n = len(text)
    if h["sweet_min"] <= n <= h["sweet_max"]:
        s += sc["sweet_len"]
        reasons.append(f"길이 {n}자(최적)")
    else:
        s += sc["sweet_len"] * 0.4
        reasons.append(f"길이 {n}자")
    if re.search(r"\d", text):
        s += sc["digit"]
        reasons.append("숫자")
    if "?" in text:
        s += sc["question"]
        reasons.append("질문형")
    pw = [w for w in h["power_words"] if w in text]
    if pw:
        bonus = min(len(pw) * sc["power_word"] * (1 + 0.25 * (h["intensity"] - 1)), sc["power_cap"])
        s += bonus
        reasons.append("파워워드:" + "/".join(pw))
        if any(text.startswith(w) for w in pw):
            s += sc["starts_power"]
            reasons.append("첫 단어 강타")
    if ctx["t"] in text:
        s += sc["target"]
        reasons.append("타겟 호명")
    if re.search(r"(세요|죠\?|요\?|님|당신)", text):
        s += sc["second_person"]
        reasons.append("말 걸기")
    if ctx["p"] in text:
        s += sc["product"]
        reasons.append("제품명")
    return min(99, round(s)), reasons


def _candidates(htype, ctx, h):
    tpls = list(h["templates"].get(htype, []))
    strong = list(h.get("strong_templates", {}).get(htype, []))
    if h["intensity"] >= 3:
        tpls = strong + tpls
    elif h["intensity"] >= 2:
        tpls = tpls + strong
    out = []
    for tpl in tpls:
        text = render_template(tpl, ctx)
        if not text:
            continue
        out.append(text)
        if len(text) > h["max_chars"]:  # 제품명을 '이거'로 줄여 재시도
            alt = text.replace(ctx["p"], "이거")
            if alt != text:
                out.append(alt)
    if h["intensity"] >= 2:  # 부스터 변형
        base = list(out)
        for text in base:
            for pre in h["boosters"]["prefix"]:
                if not text.startswith(pre):
                    out.append(f"{pre} {text}")
            for suf in h["boosters"]["suffix"]:
                stem = text.rstrip("?!. ")
                out.append(stem + suf)
    seen, uniq = set(), []
    for t in out:
        if t not in seen and len(t) <= h["max_chars"]:
            seen.add(t)
            uniq.append(t)
    return uniq


def generate_hooks(ctx, rules):
    """유형별 상위 per_type개 → 전체 순위. 결과: [{rank,type,type_ko,text,score,reasons}]"""
    h = rules["hooks"]
    result = []
    for htype, ko in HOOK_TYPES:
        scored = []
        for text in _candidates(htype, ctx, h):
            s, why = score_hook(text, htype, ctx, h)
            scored.append({"type": htype, "type_ko": ko, "text": text, "score": s, "reasons": why})
        scored.sort(key=lambda x: -x["score"])
        result.extend(scored[: h["per_type"]])
    result.sort(key=lambda x: -x["score"])
    for i, r in enumerate(result, 1):
        r["rank"] = i
    return result


def typing_timeline(text, rules):
    """단어가 0.5~1.0초 간격으로 하나씩 뜨는 타이핑 타임라인."""
    ty = rules["hooks"]["typing"]
    t0, win, hold = ty["start_sec"], ty["window_sec"], ty["hold_sec"]
    lo, hi = ty["min_word_sec"], ty["max_word_sec"]
    words = text.split()
    usable = win - hold - t0
    # 단어가 너무 많아 0.5초 간격이 안 나오면 짧은 단어끼리 묶는다
    while len(words) > 1 and usable / (len(words) - 1) < lo:
        i = min(range(len(words) - 1), key=lambda k: len(words[k]) + len(words[k + 1]))
        words[i:i + 2] = [words[i] + " " + words[i + 1]]
    step = hi if len(words) == 1 else max(lo, min(hi, usable / (len(words) - 1)))
    events = []
    for i, w in enumerate(words):
        start = round(t0 + i * step, 3)
        end = round(t0 + (i + 1) * step, 3) if i < len(words) - 1 else win
        events.append({"start": start, "end": end, "word": w,
                       "shown": " ".join(words[: i + 1])})
    return events
