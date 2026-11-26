TITLE = "일왕이 생일 기자회견에서 꺼낸 백제 이야기"
END_PAD = 2.5
EM = dict(torso="#1a1a1a", hair="#9a9a9a")
KM = dict(accent="#7a1f2b", torso="#5a2a6a")
SEG = [
    (0, "office", "night", [P("em", "boss", **EM), P("rp", "worker")], {0: "2001.12", 2: ("em", "무령왕 자손")}),
    (5, "study_room", "night", [P("sch", "scholar")], {6: "속일본기"}),
    (10, "office", "interior", [P("em", "boss", **EM), P("rp", "worker")], {11: ("rp", "월드컵 2002"), 15: ("em", "간무의 생모")}),
    (16, "palace_hall", "day", [P("km", "jking", **KM)], {16: "794 교토"}),
    (18, "palace_hall", "interior", [P("ng", "queen")], {19: "니이가사", 20: "백제 왕족"}),
    (21, "study_room", "golden", [P("sch", "scholar")], {21: "순타 태자", 23: "1971 공주", 24: "무령왕 지석"}, {"calm": True}),
    (28, "palace_hall", "night", [P("ng", "queen"), P("ym", "youth", scale=0.85)], {28: "황후 아님", 31: ("ym", "야마베")}),
    (32, "palace_hall", "interior", [P("in", "queen", torso="#b03030"), P("os", "youth", scale=0.85)], {33: ("os", "오사베")}),
    (37, "palace_hall", "night", [P("in", "queen", torso="#b03030"), P("of", "official")], {38: "772년", 39: "저주 사건"}),
    (42, "gate_court", "day", [P("km", "jking", **KM)], {42: "황태자", 44: "781 즉위", 46: "헤이안쿄"}),
    (48, "palace_hall", "golden", [P("km", "jking", **KM), P("ng", "queen")], {49: "황태부인", 50: "백제왕씨", 51: "789 별세"}),
    (53, "office", "night", [P("em", "boss", **EM), P("rp", "worker")], {53: "회견 그 후"}),
    (59, "study_room", "golden", [P("sch", "scholar")], {60: "첫째 797"}, {"calm": True}),
    (63, "study_room", "golden", [P("sch", "scholar")], {63: "둘째", 65: "속일본기"}),
    (69, "gate_court", "sunset", [P("km", "jking", **KM), P("sch", "scholar"), P("em", "boss", **EM)], {70: "간무는?", 71: "일왕의 말은?"}, {"holder": "sch"}),
    (73, "gate_court", "dawn", [P("sb", "scholar")], {74: "1800 춘당대"}),
]
