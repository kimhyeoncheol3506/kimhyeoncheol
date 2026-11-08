"""목소리가 틀리게 읽은 낱말을 모아 발음 사전에 스스로 넣는다(여의도남자·여의도여자 공통, 목소리별 기록).

흐름
  1) Voice.say 가 음성을 만들 때마다 ASR(받아쓰기)과 대본을 낱말 단위로 맞춰 본다(misread_words).
  2) 다르게 들린 낱말을 rules/pron_watch.jsonl 에 한 줄씩 남긴다(log_misreads).
  3) update() 가 기록을 모아, 서로 다른 문장에서 2번 이상 틀린 낱말을 rules/pron_learned.json 에 넣는다.
     넣는 발음은 표준발음 변환(g2p.pronounce + 된소리)으로 만든다. 철자와 소리가 같아 고칠 수 없는 낱말은
     'manual' 로 남겨 사람이 대본에 '원문{{발음}}' 으로 적도록 알린다.
  4) pron_dict.pron_hints 가 다음 생성부터 그 낱말을 소리 나는 대로 넣는다.
ASR 이 틀린 것일 수도 있어서 한 번 틀린 것은 넣지 않는다(2번 이상, 다른 문장).
"""
import datetime
import difflib
import json
import re

from .pron_dict import LEARNED_PATH, ROOT, load_learned

WATCH_PATH = ROOT / "rules" / "pron_watch.jsonl"
MIN_SENTENCES = 2
_PARTICLE = re.compile(r"(에서는|에서도|으로는|으로|에서|에게|까지|부터|보다|처럼|이라|이다|입니다|이고|하고|"
                       r"은|는|이|가|을|를|의|에|로|와|과|도|만|요)$")


def _core(word):
    w = re.sub(r"[^가-힣A-Za-z0-9]", "", word)
    c = _PARTICLE.sub("", w)
    return c if len(c) >= 2 else w


def misread_words(spoken, heard):
    """대본(읽는 말)과 ASR 결과를 맞춰, 다르게 들린 낱말 목록 [{'word','heard'}].
    ASR 이 표준발음대로 받아쓴 것(금리→금니, 갈등→갈뜽)은 맞게 읽은 것이므로 세지 않는다."""
    from .g2p import tense_hints
    from .pron_dict import pron_hints
    a = _diff_words(spoken, heard)
    alt = tense_hints(pron_hints(spoken))
    if alt != spoken and len(alt.split()) == len(spoken.split()):
        b = {it["i"] for it in _diff_words(alt, heard)}
        a = [it for it in a if it["i"] in b]
    return [{"word": it["word"], "heard": it["heard"]} for it in a]


def _diff_words(spoken, heard):
    from .textnorm import to_speech
    words = spoken.split()
    ref, owner = [], []
    for i, w in enumerate(words):
        for ch in re.sub(r"[^가-힣a-zA-Z]", "", w):
            ref.append(ch)
            owner.append(i)
    hyp = re.sub(r"[^가-힣a-zA-Z]", "", to_speech(heard or ""))
    if not ref:
        return []
    bad = {}
    sm = difflib.SequenceMatcher(None, ref, list(hyp), autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        idx = {owner[k] for k in range(i1, i2)} if i2 > i1 else {owner[min(i1, len(owner) - 1)]}
        for k in idx:
            bad.setdefault(k, "")
            bad[k] += hyp[j1:j2]
    out = []
    for k in sorted(bad):
        core = _core(words[k])
        if len(re.sub(r"[^가-힣]", "", core)) >= 2:          # 한 글자 조사·어미 흔들림은 무시
            out.append({"i": k, "word": core, "heard": bad[k]})
    return out


def log_misreads(items, voice, sentence):
    if not items:
        return
    WATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
    day = datetime.date.today().isoformat()
    with WATCH_PATH.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps({"date": day, "voice": voice, "word": it["word"], "heard": it["heard"],
                                "sentence": sentence}, ensure_ascii=False) + "\n")


def suggest(word):
    """표준발음 쪽으로 고쳐 적은 후보. 철자 그대로면 None(자동으로 못 고침)."""
    from .g2p import pronounce, tense_hints
    from .pron_dict import WORDS
    if word in WORDS:
        return WORDS[word]
    cand = tense_hints(word)
    if cand == word:
        cand = pronounce(word)
    return cand if cand != word else None


def collect():
    stats = {}
    if not WATCH_PATH.exists():
        return stats
    for line in WATCH_PATH.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s = stats.setdefault(r["word"], {"count": 0, "sentences": set(), "voices": set(), "heard": {}})
        s["count"] += 1
        s["sentences"].add(r.get("sentence", ""))
        s["voices"].add(r.get("voice", ""))
        h = r.get("heard", "")
        s["heard"][h] = s["heard"].get(h, 0) + 1
    return stats


def update(min_sentences=MIN_SENTENCES):
    """기록을 사전에 반영. 반환: (새로 넣은 낱말, 사람이 고쳐야 할 낱말)."""
    try:
        learned = json.loads(LEARNED_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        learned = {}
    added, manual = [], []
    for word, s in collect().items():
        if len(s["sentences"]) < min_sentences:
            continue
        prev = learned.get(word, {})
        if prev.get("locked"):                       # 사람이 확정한 항목은 건드리지 않음
            continue
        say = suggest(word)
        entry = {"say": say, "count": s["count"], "sentences": len(s["sentences"]),
                 "voices": sorted(v for v in s["voices"] if v), "heard": max(s["heard"], key=s["heard"].get),
                 "status": "auto" if say else "manual", "updated": datetime.date.today().isoformat()}
        if say and prev.get("say") != say:
            added.append(word)
        if not say:
            manual.append(word)
        learned[word] = entry
    LEARNED_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEARNED_PATH.write_text(json.dumps(learned, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    load_learned()
    return added, manual
