TITLE = "망한 나라의 이름을 다시 쓰자고 한 사람들"
END_PAD = 2.5
SSW = dict()                       # 신석우(official)
YWH = dict(torso="#3a4a5a")        # 여운형(official_red 대신 boss 정장? → official_red 유지)
SEG = [
    (0, "office", "night", [P("ssw", "official"), P("ywh", "official_red")], {0: "상하이 1919", 4: ("ssw", "대한민국"), 6: ("ywh", "망한 나라")}),
    (8, "village_road", "day", [P("y1", "youth", scale=0.9)], {8: "대한민국"}),
    (12, "gate_court", "day", [P("gj", "jking"), P("of", "official")], {13: "1897.10", 14: "환구단", 17: "조선→대한"}),
    (18, "study_room", "golden", [P("sch", "scholar")], {19: "마한·진한·변한", 21: "대한제국"}, {"calm": True}),
    (23, "palace_hall", "night", [P("gj", "jking"), P("jp", "boss", torso="#2a2a2a")], {25: ("jp", "을사늑약"), 26: "헤이그 특사", 28: ("jp", "1910.8.29")}),
    (32, "village_road", "day", [P("p1", "peasant"), P("p2", "youth", scale=0.85)], {33: "1919.3.1"}),
    (35, "office", "night", [P("ssw", "official"), P("ywh", "official_red")], {36: "4월 10일", 39: ("ssw", "대한으로 흥하자"), 40: "대한민국"}),
    (41, "study_room", "golden", [P("sch", "scholar")], {43: "대한민국", 44: "제국→민국", 46: "민주공화제"}, {"calm": True}),
    (50, "office", "day", [P("m1", "official"), P("m2", "boss", torso="#2b2f3a"), P("m3", "official_red")], {52: "1948.5.31", 57: "헌법기초위", 58: "17 : 7", 60: "7·17 제헌절"}),
    (62, "study_room", "golden", [P("sch", "scholar")], {63: "첫째", 64: "30명 중 17", 66: "고려공화국?"}),
    (67, "study_room", "golden", [P("sch", "scholar")], {67: "둘째 전문", 69: "삼일운동"}),
    (72, "gate_court", "sunset", [P("ssw", "official"), P("sch", "scholar"), P("ywh", "official_red")], {73: ("sch", "신석우는?"), 74: ("sch", "여운형은?")}, {"holder": "sch"}),
    (76, "office", "interior", [P("em", "boss", torso="#1a1a1a", hair="#9a9a9a")], {77: "2001.12", 78: "백제"}),
]
