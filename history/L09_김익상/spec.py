TITLE = "전기 수리공으로 위장해 총독부에 폭탄을 던진 청년"
END_PAD = 2.5
KIS = dict(torso="#4a5a6a")          # 김익상(worker)
TN = dict(torso="#5a5a3a", hair="#2a2a2a")   # 다나카(cop 계열 군복)
SEG = [
    (0, "sea_battle", "day", [P("tn", "cop", **TN), P("kis", "worker", **KIS)], {0: "1922.3", 2: "빗나감", 4: ("kis", "불발")}),
    (5, "office", "night", [P("kis", "worker", **KIS)], {5: "김익상", 6: "조선총독부"}),
    (9, "village_road", "day", [P("kis", "worker", **KIS)], {10: "1895 고양", 11: "숭실학교", 13: "비행사의 꿈"}),
    (15, "study_room", "night", [P("kis", "worker", **KIS), P("kwb", "official", torso="#2a2a2a")], {16: ("kwb", "의열단"), 17: ("kwb", "1919 지린")}),
    (19, "study_room", "night", [P("kwb", "official", torso="#2a2a2a"), P("kis", "worker", **KIS)], {22: "총독부", 23: "사이토 총독"}),
    (25, "office", "day", [P("kis", "worker", **KIS), P("gd", "cop", torso="#3a3a3a")], {26: "1921.9", 27: "전기 수리공", 30: "비서과·회계과"}),
    (32, "office", "night", [P("gd", "cop", torso="#3a3a3a"), P("of", "boss", torso="#2a2a2a")], {35: "범인 못 잡아"}),
    (36, "study_room", "night", [P("kwb", "official", torso="#2a2a2a"), P("kis", "worker", **KIS), P("osr", "worker", torso="#5a4a3a")], {38: ("kwb", "다나카"), 41: ("kwb", "세 겹 작전")}),
    (42, "sea_battle", "day", [P("osr", "worker", torso="#5a4a3a"), P("tn", "cop", **TN), P("kis", "worker", **KIS)], {42: "황포탄", 45: ("kis", "불발"), 48: ("tn", "살아남음")}),
    (49, "office", "interior", [P("kis", "worker", **KIS), P("jd", "boss", torso="#1a1a1a")], {51: "나가사키", 52: ("kis", "공훈록"), 55: ("kis", "동지 350명")}),
    (57, "office", "interior", [P("jd", "boss", torso="#1a1a1a"), P("kis", "worker", **KIS)], {57: "1심 무기", 58: ("jd", "2심 사형"), 59: "감형"}),
    (61, "village_road", "dawn", [P("kis", "worker", **KIS)], {62: "출옥", 64: "행적 끊김"}),
    (66, "study_room", "golden", [P("sch", "scholar")], {67: "첫째", 68: "1926 완공", 69: "남산 청사"}, {"calm": True}),
    (71, "office", "golden", [P("tn", "cop", **TN)], {71: "둘째", 72: "1927 총리", 73: "산둥 출병"}),
    (75, "gate_court", "sunset", [P("kis", "worker", **KIS), P("sch", "scholar"), P("tn", "cop", **TN)], {76: "김익상은?", 77: "다나카는?"}, {"holder": "sch"}),
    (79, "sea_battle", "dawn", [P("hy", "official"), P("kso", "official_red")], {79: "1590", 80: "두 사신"}),
]
