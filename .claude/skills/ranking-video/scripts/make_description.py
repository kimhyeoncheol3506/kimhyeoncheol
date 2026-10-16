# -*- coding: utf-8 -*-
"""유튜브 업로드용 설명란 + 고정댓글 자동 생성 (ranking-video v2.0.0)

사용법: python3 -I make_description.py <대본데이터.json> <작업폴더>
입력: 대본데이터.json의 "upload" 블록(없으면 자동), <작업폴더>/08_완성영상/타임라인.json
출력: 05_메타데이터/설명란_업로드용.txt, 05_메타데이터/고정댓글.txt

"upload": {
  "hook": "첫 줄 한 문장",
  "summary": ["요약 1", "요약 2"],
  "hashtags": ["#태그1", "#태그2", "#태그3"],   # 정확히 3개 (유튜브는 앞 3개를 제목 위에 표시)
  "disclaimer": "사용자 지정 면책 문구"
}
"""
import json, os, re, sys


def mm(x):
    x = int(x); return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}" if x >= 3600 else f"{x // 60:02d}:{x % 60:02d}"


def auto_hashtags(D):
    words = re.findall(r"[가-힣A-Za-z0-9]+", D.get("title", ""))
    topic = next((w for w in words if w not in ("TOP10", "TOP", "특집", "맛집")), "랭킹")
    return [f"#{topic}맛집" if "맛집" in D.get("title", "") else f"#{topic}", f"#{topic}TOP10", "#맛집랭킹"]


def main(data_path, proj):
    D = json.load(open(data_path, encoding="utf-8"))
    T = json.load(open(os.path.join(proj, "08_완성영상", "타임라인.json"), encoding="utf-8"))
    U = D.get("upload", {})
    chapters = {c["name"]: c["card"] for c in T["chapters"]}
    secs = D["sections"]
    tags = (U.get("hashtags") or auto_hashtags(D))[:3]
    tags = [t if t.startswith("#") else "#" + t for t in tags]
    L = []
    if U.get("hook"): L.append(U["hook"])
    L += U.get("summary", [])
    L += ["", "⏱ 바로가기"]
    L.append(f"00:00 인트로")
    ranks = [s for s in secs if s.get("rank")]
    for s in secs[1:]:  # v2.3.0: 영상 순서대로, 순위 섹션과 정보 챕터(chapter) 모두
        if not (s.get("rank") or s.get("chapter")): continue
        nm = s.get("card_name") or (s["name"].split(" ", 1)[1] if " " in s["name"] else s["name"])
        tl = f" | {s['tagline']}" if s.get("tagline") else ""
        head = f"{s['rank']}위" if s.get("rank") else s["chapter"]
        L.append(f"{mm(chapters[s['name']])} {head} {nm}{tl}")
    out_sec = secs[-1]["name"]
    if out_sec in chapters and not secs[-1].get("rank"): L.append(f"{mm(chapters[out_sec])} 총정리")
    L += ["", "💬 여러분의 PICK은 몇 위인가요? 댓글로 알려주세요!", "🔔 구독·알림 설정하시면 다음 랭킹도 가장 먼저 받아보실 수 있어요.", ""]
    if U.get("disclaimer"): L.append(f"※ {U['disclaimer']}")
    L += ["※ 가격·영업 정보는 방문 전 매장에 확인해 주세요.",
          "※ 영상 속 사진은 실제 매장 사진이 아닌 자유 이용 이미지이며, 출처는 고정댓글에 있습니다. 내레이션은 AI 음성입니다.", "",
          " ".join(tags)]
    desc = "\n".join(L) + "\n"
    if len(desc) > 5000: raise SystemExit(f"설명란이 {len(desc)}자로 유튜브 한도 5,000자를 넘습니다")
    os.makedirs(os.path.join(proj, "05_메타데이터"), exist_ok=True)
    open(os.path.join(proj, "05_메타데이터", "설명란_업로드용.txt"), "w", encoding="utf-8").write(desc)
    # 고정댓글: 순위 목록 + 이미지 출처(짧은 버전)
    C = ["📍 오늘의 TOP" + str(len(ranks)), " | ".join(f"{s['rank']}위 {s['name'].split(' ', 1)[-1]}" for s in sorted(ranks, key=lambda s: s["rank"])), "",
         "👉 여러분의 PICK을 숫자로 남겨주세요!", ""]
    cred = os.path.join(proj, "08_완성영상", "이미지_출처_짧은버전.txt")
    if os.path.exists(cred): C.append(open(cred, encoding="utf-8").read().strip())
    open(os.path.join(proj, "05_메타데이터", "고정댓글.txt"), "w", encoding="utf-8").write("\n".join(C) + "\n")
    print(f"설명란 {len(desc)}자, 해시태그 {' '.join(tags)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
