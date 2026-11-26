TITLE = "같은 배를 타고 온 두 사신은 왜 정반대로 보고했나"
END_PAD = 2.5
HYG = dict()                 # 황윤길(official)
KSI = dict()                 # 김성일(official_red)
SJ = dict(accent="#c8a020")  # 선조
HD = dict(torso="#6a5a2a")   # 히데요시(enemy)
SEG = [
    (0, "palace_hall", "interior", [P("hyg", "official"), P("sj", "jking", **SJ), P("ksi", "official_red")], {0: "1591 봄", 3: ("hyg", "반드시 병화"), 5: ("ksi", "보지 못했다")}),
    (6, "sea_battle", "night", [P("e1", "enemy"), P("e2", "enemy")], {7: "1592"}),
    (8, "study_room", "night", [P("sch", "scholar")], {9: "동인 vs 서인", 11: "선조수정실록"}),
    (12, "gate_court", "day", [P("ksi", "official_red"), P("dm", "enemy", torso="#6a4a3a"), P("hyg", "official")], {13: "1590.4", 15: ("dm", "가마 탄 채"), 16: ("ksi", "자리를 뜸")}),
    (19, "gate_court", "day", [P("dm", "enemy", torso="#6a4a3a"), P("ksi", "official_red")], {19: "부하 처형", 20: ("ksi", "존중")}),
    (21, "village_road", "day", [P("hyg", "official"), P("ksi", "official_red")], {24: "다섯 달"}),
    (25, "palace_hall", "night", [P("hd", "enemy", **HD), P("hyg", "official")], {26: "히데요시", 30: "떡 한 그릇"}),
    (31, "palace_hall", "night", [P("hd", "enemy", **HD), P("y1", "youth", scale=0.7)], {32: "아이가 오줌", 34: "방약무인"}),
    (35, "palace_hall", "night", [P("ksi", "official_red"), P("hyg", "official")], {36: "답서 없음", 38: ("ksi", "답서를 달라")}),
    (40, "study_room", "night", [P("ksi", "official_red"), P("gs", "official", torso="#3a3a3a")], {41: "곧장 명나라로", 42: "귀국이 앞장", 44: ("ksi", "고쳐라")}),
    (46, "palace_hall", "interior", [P("hyg", "official"), P("sj", "jking", **SJ), P("ksi", "official_red")], {48: ("hyg", "반드시 병화"), 50: ("ksi", "보지 못했다"), 54: ("hyg", "담력·지략"), 56: ("ksi", "쥐의 눈")}),
    (57, "study_room", "golden", [P("sch", "scholar")], {58: "체통을 잃음"}, {"calm": True}),
    (59, "palace_hall", "night", [P("ryu", "official", torso="#2f4f86"), P("ksi", "official_red")], {60: "조헌", 64: ("ryu", "만일…"), 66: ("ksi", "민심 동요")}),
    (67, "study_room", "golden", [P("sch", "scholar")], {68: "첫째", 69: "앞장서라", 71: "둘째 수정실록"}),
    (73, "mountain_pass", "dusk" if False else "night", [P("ksi", "official_red"), P("s1", "soldier")], {73: "1592.4", 75: "의병"}),
    (76, "gate_court", "sunset", [P("hyg", "official"), P("sch", "scholar"), P("ksi", "official_red")], {77: "황윤길은?", 78: "김성일은?"}, {"holder": "sch"}),
    (80, "sea_battle", "dawn", [P("e1", "enemy"), P("e2", "enemy")], {80: "1592", 81: "칠 년"}),
]
