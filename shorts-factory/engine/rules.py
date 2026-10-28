"""rules.yaml 읽기/쓰기. 후킹 섹션만 골라서 다시 쓰는 기능 포함."""
import datetime
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = ROOT / "rules.yaml"
HOOKS_BEGIN = "# >>> HOOKS-BEGIN"
HOOKS_END = "# <<< HOOKS-END"


def load_rules(path=RULES_PATH):
    """편집 실행 때마다 호출된다 — 캐시하지 않는다."""
    path = Path(path)
    rules = yaml.safe_load(path.read_text(encoding="utf-8"))
    rules["_path"] = str(path)
    return rules


def save_hooks_section(hooks, path=RULES_PATH):
    """HOOKS-BEGIN ~ HOOKS-END 사이만 교체한다. 나머지 주석/설정은 그대로 둔다."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(HOOKS_BEGIN) + r".*?" + re.escape(HOOKS_END), re.S)
    if not pattern.search(text):
        raise RuntimeError("rules.yaml 에 HOOKS-BEGIN/END 표시가 없습니다.")
    body = yaml.safe_dump({"hooks": hooks}, allow_unicode=True, sort_keys=False,
                          width=1000, default_flow_style=None)
    block = f"{HOOKS_BEGIN}\n{body}{HOOKS_END}"
    path.write_text(pattern.sub(lambda m: block, text, count=1), encoding="utf-8")


def strengthen_hooks(rules, feedback_text, last_hook_type=None):
    """'후킹이 약해' 피드백 → 후킹 섹션을 강화 버전으로 바꾼다. 바뀐 내용 목록을 돌려준다."""
    h = rules["hooks"]
    changes = []

    old = h.get("intensity", 1)
    h["intensity"] = min(3, old + 1)
    if h["intensity"] != old:
        changes.append(f"강도 {old} → {h['intensity']} (strong 템플릿/부스터 활성화)")

    sc = h["score"]
    sc["power_word"] = sc.get("power_word", 5) + 2
    sc["power_cap"] = sc.get("power_cap", 15) + 5
    changes.append(f"파워워드 가점 → {sc['power_word']}점 (상한 {sc['power_cap']})")

    for t in ("price_shock", "rebuttal", "curiosity"):
        h["type_weights"][t] = round(h["type_weights"].get(t, 1.0) + 0.05, 3)
    if last_hook_type and last_hook_type in h["type_weights"]:
        h["type_weights"][last_hook_type] = round(h["type_weights"][last_hook_type] - 0.08, 3)
        changes.append(f"지난번 유형({last_hook_type}) 가중치 하향 → 다른 유형 시도")
    changes.append("가격충격/반박/호기심 유형 가중치 +0.05")

    if h["max_chars"] > 12:
        h["max_chars"] -= 1
        h["sweet_max"] = min(h["sweet_max"], h["max_chars"] - 1)
        changes.append(f"후킹 최대 글자 → {h['max_chars']}자 (더 짧고 세게)")

    ty = h["typing"]
    if ty["max_word_sec"] > 0.7:
        ty["max_word_sec"] = round(ty["max_word_sec"] - 0.1, 2)
        changes.append(f"타이핑 간격 상한 → {ty['max_word_sec']}초 (더 빠른 리듬)")

    for w in ("헐", "역대급", "충격"):
        if w not in h["power_words"]:
            h["power_words"].append(w)
            changes.append(f"파워워드 추가: {w}")
            break

    h.setdefault("history", []).append({
        "at": datetime.datetime.now().isoformat(timespec="seconds"),
        "feedback": feedback_text,
        "changes": changes,
    })
    return changes
