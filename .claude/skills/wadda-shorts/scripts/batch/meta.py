# 20편 업로드용 제목/설명/해시태그 TXT 생성 -> Downloads\어랏\이름N.TXT
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.expanduser("~"), "Downloads", "어랏")
T = json.load(open(os.path.join(B, "titles.json"), encoding="utf-8"))
SRC = json.load(open(os.path.join(B, "sources.json"), encoding="utf-8"))
S = json.load(open(os.path.join(B, "segments.json"), encoding="utf-8"))

INFO = {
    "김원훈": {"tags": ["김원훈", "숏박스", "김원훈레전드", "개그맨", "웃긴영상", "예능레전드", "빵터짐"],
            "intro": "숏박스 김원훈이 예능에만 나오면 왜 다들 빵 터질까ㅋㅋ"},
    "이수지": {"tags": ["이수지", "핫이슈지", "이수지레전드", "개그우먼", "웃긴영상", "라디오스타", "빵터짐"],
            "intro": "천의 얼굴 이수지가 나오면 스튜디오가 뒤집어지는 이유ㅋㅋ"},
    "장도연": {"tags": ["장도연", "장도연레전드", "라디오스타", "개그우먼", "웃긴영상", "예능레전드", "빵터짐"],
            "intro": "툭 던지는 한마디로 다 쓰러뜨리는 장도연ㅋㅋ"},
    "박영진": {"tags": ["박영진", "박영진레전드", "개그콘서트", "개그맨", "웃긴영상", "아는형님", "빵터짐"],
            "intro": "브레이크 없는 개그맨 박영진의 아무 말 대잔치ㅋㅋ"},
}
CH_KEYS = {}
for person in T:
    INFO.setdefault(person, {"tags": [person, person + "레전드", "개그맨", "웃긴영상", "예능레전드", "빵터짐"], "intro": "%s 나오면 다들 빵 터지는 이유ㅋㅋ" % person})
    start = T[person].get("start", 1)
    idxs = [i for i in range(len(S[person])) if str(i) in T[person]["ch"]]
    for v in range(5):
        p = os.path.join(B, "proj_%s_%d.json" % (person, v + 1))
        if not os.path.exists(p):
            continue
        proj = json.load(open(p, encoding="utf-8"))
        chs = proj["chapters"]
        title = T[person]["videos"][v]
        # 챕터 시작 시각
        t, lines, used = 0.0, [], []
        for ch in chs:
            lines.append("%d:%02d %s" % (t // 60, t % 60, ch["title"]))
            t += ch["out"] - ch["in"]
            sid = os.path.basename(ch["src"]).rsplit("_", 2)[0]
            if sid not in used:
                used.append(sid)
        credits = []
        for sid in used:
            s = next((x for x in SRC[person] if x["id"] == sid), None)
            if s:
                credits.append("- %s | %s\n  https://www.youtube.com/watch?v=%s" % (s.get("channel"), s.get("title"), sid))
        topics = [c["title"].lstrip(";") for c in chs]
        tags = ["#shorts", "#쇼츠"] + ["#" + x for x in INFO[person]["tags"]] + ["#" + topics[0].replace(" ", "")]
        hashtags = " ".join(dict.fromkeys(tags))
        desc = "\n".join([
            INFO[person]["intro"],
            "%s 편: %s" % (topics[0], ", ".join(topics[1:])) if len(topics) > 1 else topics[0],
            "",
            "▶ 순서",
            *lines,
            "",
            "▶ 원본 영상 (출처)",
            *credits,
            "",
            "※ 본 영상은 원작자의 영상을 짧게 인용·편집한 하이라이트입니다. 모든 권리는 각 방송사·채널에 있으며, 문제가 될 경우 삭제하겠습니다.",
            "구독과 좋아요는 큰 힘이 됩니다ㅋㅋ",
            "",
            hashtags,
        ])
        txt = "\n".join([
            "[제목]",
            "%s #shorts" % title,
            "",
            "[설명]",
            desc,
            "",
            "[해시태그]",
            hashtags,
            "",
            "[태그(쉼표 구분, 유튜브 태그 칸용)]",
            ", ".join([person] + INFO[person]["tags"][1:] + topics[:3] + ["쇼츠", "개그", "예능"]),
            "",
        ])
        fn = os.path.join(OUT, "%s%d.TXT" % (person, v + start))
        open(fn, "w", encoding="utf-8-sig").write(txt)
        print(os.path.basename(fn), len(title), "자 제목,", len(desc), "자 설명")
