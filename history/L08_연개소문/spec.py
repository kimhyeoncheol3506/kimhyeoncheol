TITLE = "왕을 베고 당 태종을 막은 남자, 당신의 판결은?"
END_PAD = 2.5
YG = dict(torso="#3a3a5a")      # 연개소문
YR = dict(accent="#c8a020")     # 영류왕
TZ = dict()                     # 당 태종(tang)
SEG = [
    (0, "fortress_wall", "night", [P("ygs", "general", **YG), P("of", "official")], {0: "642 겨울", 2: ("ygs", "대신 100여 명")}),
    (3, "palace_hall", "night", [P("ygs", "general", **YG), P("yr", "jking", **YR)], {4: "삼국사기", 5: ("ygs", "여러 토막")}),
    (6, "study_room", "night", [P("sch", "scholar")], {6: "연개소문", 8: "독재자?영웅?"}),
    (10, "village_road", "day", [P("ygs", "general", **YG)], {12: "물에서 태어남"}),
    (14, "palace_hall", "interior", [P("ygs", "general", **YG), P("of", "official_red")], {16: ("of", "잔인·난폭"), 18: "맡겨 주시오"}),
    (21, "mountain_pass", "day", [P("ygs", "general", **YG), P("s1", "soldier")], {22: "642 봄", 23: "천리장성"}),
    (26, "palace_hall", "night", [P("yr", "jking", **YR), P("of", "official_red")], {27: ("of", "연개소문을…"), 28: "누설"}),
    (29, "fortress_wall", "night", [P("ygs", "general", **YG), P("s1", "soldier")], {31: "사열", 33: "백여 명"}),
    (34, "palace_hall", "night", [P("ygs", "general", **YG), P("bj", "jking", scale=0.85)], {35: "막리지", 36: "칼 다섯 자루", 39: "괴로워했다"}),
    (40, "palace_hall", "interior", [P("tz", "tang"), P("en", "official")], {41: ("tz", "당 태종"), 42: ("en", "신라 공격 말라")}),
    (43, "palace_hall", "night", [P("ygs", "general", **YG), P("en", "official")], {44: "수나라 때 땅", 47: "사신 투옥"}),
    (48, "fortress_wall", "day", [P("tz", "tang"), P("s1", "soldier")], {48: "645년", 50: "요동성", 52: "안시성"}),
    (53, "fortress_wall", "sunset", [P("gd", "general", torso="#2f4f86"), P("s1", "soldier")], {54: "석 달 가까이", 55: "9월 철군"}),
    (58, "study_room", "golden", [P("sch", "scholar")], {59: "첫째", 61: "641 진대덕"}, {"calm": True}),
    (65, "study_room", "golden", [P("sch", "scholar")], {65: "둘째", 67: "비상한 인물", 69: "김부식"}),
    (71, "palace_hall", "night", [P("ns", "general", torso="#5a3a3a"), P("nk", "general", torso="#3a5a3a")], {73: "남생", 74: "668 평양"}),
    (76, "gate_court", "sunset", [P("ygs", "general", **YG), P("sch", "scholar"), P("yr", "jking", **YR)], {77: "연개소문은?", 78: "영류왕은?"}, {"holder": "sch"}),
    (80, "office", "day", [P("kis", "worker", torso="#4a5a6a")], {81: "전기 수리공"}),
]
