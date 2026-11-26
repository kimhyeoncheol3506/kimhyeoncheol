TITLE = "이틀 동안 21만 명이 몰린 시험, 합격자는 12명"
END_PAD = 2.5
JJ = dict(accent="#c8a020")
SEG = [
    (0, "gate_court", "day", [P("s1", "scholar"), P("s2", "scholar", torso="#d8d0b8"), P("y1", "youth", scale=0.85)], {0: "1800.3", 2: "11만 명", 3: "합격자는?"}),
    (4, "palace_hall", "interior", [P("jj", "jking", **JJ)], {4: "정조", 5: "석 달 뒤"}),
    (7, "study_room", "night", [P("sch", "scholar")], {7: "공정한 시험?"}),
    (10, "palace_hall", "day", [P("jj", "jking", **JJ), P("sch", "scholar")], {11: ("sch", "3년에 한 번"), 12: ("sch", "식년시")}),
    (15, "gate_court", "day", [P("s1", "scholar"), P("of", "official")], {15: "전시", 16: "33명", 17: ("of", "홍패")}),
    (19, "gate_court", "night", [P("s1", "scholar"), P("s2", "scholar", torso="#d8d0b8"), P("y1", "youth", scale=0.85)], {22: "1707 숙종", 24: ("y1", "선접꾼"), 26: "난장판"}),
    (27, "study_room", "night", [P("sch", "scholar"), P("s2", "scholar", torso="#d8d0b8")], {29: "대술", 31: ("s2", "협서")}),
    (33, "palace_hall", "interior", [P("of", "official")], {34: "이름 가림", 36: "1677"}),
    (37, "study_room", "night", [P("cc", "scholar", torso="#c8b890")], {38: "차천로", 39: "1586", 41: "유배"}),
    (43, "gate_court", "day", [P("s1", "scholar"), P("s2", "scholar", torso="#d8d0b8"), P("y1", "youth", scale=0.85)], {46: "11만 1838", 48: "3만 8614"}),
    (50, "gate_court", "day", [P("s1", "scholar"), P("s2", "scholar", torso="#d8d0b8")], {50: "10만 3579", 51: "3만 2884", 52: "합격 12명"}),
    (53, "palace_hall", "golden", [P("jj", "jking", **JJ)], {54: "규장각", 57: "1800.6"}),
    (58, "study_room", "golden", [P("sch", "scholar")], {59: "첫째", 62: "둘째"}, {"calm": True}),
    (66, "gate_court", "sunset", [P("jj", "jking", **JJ), P("sch", "scholar"), P("cc", "scholar", torso="#c8b890")], {67: "정조는?", 68: "차천로는?"}, {"holder": "sch"}),
    (70, "study_room", "dawn", [P("sch", "scholar")], {71: "1824 일본", 72: "신대문자"}),
]
