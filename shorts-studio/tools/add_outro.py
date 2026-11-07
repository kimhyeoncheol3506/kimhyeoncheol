"""모든 쇼츠 마지막에 구독·좋아요 부탁 멘트(청유형) 장면을 붙인다 (현철님 요청, 2026-10-23).

  python tools/add_outro.py projects/<프로젝트>
- script.json 맨 끝에 장면 `outro`(여의도남자, CTA 화면)를 추가한다. 이미 있으면 그대로 둔다(여러 번 실행해도 안전).
- 쇼츠(card/kakao)만 대상. 롱폼(format != short)은 건드리지 않는다.
- 본편 마지막 장면 뒤에 1.5초 간격을 두고 멘트가 나온다(OUTRO_GAP).
- 멘트 문구는 아래 OUTRO 에서만 바꾼다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

OUTRO_GAP = 1.5  # 본편 끝 → 멘트 사이 간격(초)
OUTRO = {
    "id": "outro",
    "voice": "여의도남자",
    "say": "구독하시고 댓글 하나 남겨 주시면, 사주와 관상, 궁합까지 무료로 보는 방법을 알려 드릴게요.",
    "cap": ["구독하고 *댓글* 남기시면", "*사주·관상·궁합* 무료로"],
    "sfx": [["pop", 0.2]],
    "visual": {"mode": "cta"},
}


def ensure(proj: Path) -> bool:
    """붙였으면 True, 이미 있거나 대상이 아니면 False."""
    p = proj / "script.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    if s.get("format") != "short" or any(x.get("id") == "outro" for x in s["scenes"]):
        return False
    # 본편 마지막 음성과 너무 붙으면 어색해서 1.5초 쉬었다가 멘트 (현철님, 2026-10-23)
    last = s["scenes"][-1]
    last["pause_after"] = max(last.get("pause_after", 0), OUTRO_GAP)
    s["scenes"].append(json.loads(json.dumps(OUTRO, ensure_ascii=False)))
    p.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


if __name__ == "__main__":
    print("outro 추가" if ensure(Path(sys.argv[1])) else "outro 이미 있음/대상 아님")
