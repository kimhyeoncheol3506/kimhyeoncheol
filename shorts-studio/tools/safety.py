"""노란딱지(광고 제한) 위험 사전 점검.

유튜브 '광고주 친화 가이드' 기준으로 대본·자막·원문을 훑어 위험도를 매긴다.
  안전 → 바로 제작/업로드
  주의 → 제작은 하되 현철님께 "수위가 이 정도인데 올려도 될까요?" 먼저 확인
  위험 → 제작 전 확인 (대부분 노란딱지 확실)
script.json 의 "safety": {"level", "reasons", "approved"} 로 기록한다. approved=true 가 되어야 업로드 대상.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# (패턴, 위험도, 이유)
RULES = [
    (r"섹스|성관계|ㅅㅅ|ㅅㅅ한|야동|자위|모텔에서|떡\b|떡치|원나잇|19금|가슴|엉덩이|노출|알몸|벗[고은]", "주의", "성적 암시/표현"),
    (r"섹파|속궁합|조루|음담패설|성욕|잠자리|관계를 안했|자면 떠나|ㅅㅍ", "주의", "성적 암시(자막·화면 노출)"),
    (r"고추|섹스하는|섹스를|섹스 로망|성기|삽입|오르가", "위험", "노골적 성 묘사(커뮤니티 가이드 위반 가능)"),
    (r"강간|성폭행|성추행|몰카|불법촬영|미성년|고딩|중딩", "위험", "성범죄·미성년 관련"),
    (r"자살|자해|극단적 선택", "위험", "자해·자살"),
    (r"마약|대마|필로폰", "위험", "약물"),
    (r"살인|폭행|칼부림|피범벅", "주의", "폭력"),
    (r"학대|가정폭력|가폭|때렸|맞고 자랐", "주의", "학대·가정폭력 언급(광고 제한 가능)"),
    (r"시발|씨발|ㅅㅂ|좆|개새|병신|존나|ㅈㄴ", "주의", "욕설(자막·음성 노출)"),
    (r"바람|불륜|외도|상간", "주의", "불륜(맥락에 따라 제한)"),
    (r"도박|토토|카지노|코인 리딩", "주의", "도박·투기 조장"),
    (r"극우|극좌|정치색|좌파|우파|빨갱이|일베|음모론|역사왜곡", "주의", "정치 논쟁(댓글 싸움·광고주 기피 가능, 한쪽 편들기 금지)"),
]
ORDER = {"안전": 0, "주의": 1, "위험": 2}


def scan(script: dict, project: Path | None = None):
    texts = [("원문", script.get("source", {}).get("post", ""))]
    card = project / "card.json" if project else None
    if card and card.exists():  # 화면에 그대로 보이는 사연 본문도 검사
        c = json.loads(card.read_text(encoding="utf-8"))
        blurred = {int(k[4:]) - 1 for k in script.get("blur_lines", []) if k.startswith("body")}
        body = [t for i, t in enumerate(c.get("body", [])) if i not in blurred]  # 흐리게 가린 줄은 제외
        texts.append(("화면 카드", " ".join(c.get("title", []) + body)))
    texts += [("후크", " ".join(script.get("hook", [])))]
    for s in script.get("scenes", []):
        texts.append((f"{s['id']} 음성", s.get("say", "")))
        texts.append((f"{s['id']} 자막", " ".join(s.get("cap", []))))
    level, reasons = "안전", []
    for where, t in texts:
        for pat, lv, why in RULES:
            m = re.search(pat, t)
            if m:
                reasons.append(f"{why}: '{m.group()}' ({where})")
                if ORDER[lv] > ORDER[level]:
                    level = lv
    return level, sorted(set(reasons))


def main():
    p = Path(sys.argv[1]) / "script.json"
    script = json.loads(p.read_text(encoding="utf-8"))
    level, reasons = scan(script, Path(sys.argv[1]))
    prev = script.get("safety", {})
    # 사람이 직접 올린 등급(예: 원문 이미지에 보이는 수위)은 낮추지 않는다
    if ORDER.get(prev.get("level", "안전"), 0) > ORDER[level]:
        level = prev["level"]
    reasons = sorted(set(reasons) | set(prev.get("reasons", [])))
    script["safety"] = {"level": level, "reasons": reasons,
                        "approved": prev.get("approved", level == "안전")}
    p.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[수위] {level}", *("  - " + r for r in reasons), sep="\n")
    if not script["safety"]["approved"]:
        print("→ 현철님 확인 필요: 승인 전에는 업로드 대상이 아닙니다.")


if __name__ == "__main__":
    main()
