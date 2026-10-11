"""업로드용 복붙 텍스트(upload.txt): 제목 / 설명 / 해시태그 3개 / 추천 예약 시간 / 수위."""
from __future__ import annotations

# 첫 운영 가설(KST). 2~3주 뒤 유튜브 스튜디오 '시청자가 YouTube를 이용하는 시간' 보고 조정.
SLOTS = {"short": ["12:30 (점심)", "19:30 (퇴근길)"], "long": ["21:00 (저녁 휴식)"]}


def write_copy(path, script, upload):
    fmt = script["format"]
    title = upload["title"]
    tags = upload.get("hashtags", [])[:3]
    desc = upload.get("description", "").strip()
    warn = []
    if len(title) > 60:
        warn.append(f"! 제목 {len(title)}자 — 60자 이내 권장")
    if len(tags) != 3:
        warn.append("! 해시태그는 3개로 맞출 것")
    safety = upload.get("safety", {})
    lines = [
        "=== 제목 ===", title, "",
        "=== 설명 ===", desc + ("\n\n" if desc else "") + " ".join(tags), "",
        "=== 해시태그 ===", " ".join(tags), "",
        "=== 추천 예약 시간 (KST) ===", " / ".join(SLOTS[fmt]),
        "",
        "=== 수위 ===", f"{safety.get('level', '안전')}" + ("" if safety.get("approved", True) else "  ← 업로드 전 확인 필요"),
    ]
    if fmt == "short":
        lines += ["", "※ 표지: 모바일 업로드 화면에서 '표지 수정' → 맨 앞(0초) 프레임 선택 = thumbnail.jpg"]
    else:
        lines += ["", "※ 썸네일: thumbnail.jpg 업로드"]
    path.write_text("\n".join(warn + ([""] if warn else []) + lines) + "\n", encoding="utf-8")
