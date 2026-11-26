TITLE = "한글이 일본 고대 문자를 베꼈다는 주장의 정체"
END_PAD = 2.5
BAN = dict(torso="#3a3a3a")
HIR = dict(torso="#6a2a2a")
SEG = [
    (0, "study_room", "night", [P("ban", "official", **BAN)], {0: "1850 에도", 3: "신대문자?"}),
    (6, "study_room", "night", [P("sch", "scholar")], {8: "한글=베낌?"}),
    (11, "palace_hall", "interior", [P("of", "official")], {13: "가나"}),
    (15, "study_room", "night", [P("hir", "official_red", **HIR)], {17: "신대문자"}),
    (19, "study_room", "night", [P("hir", "official_red", **HIR)], {20: "히라타", 23: "1824", 25: "히후미 문자"}),
    (26, "study_room", "golden", [P("sch", "scholar")], {26: "히후미", 31: "아비루 문자"}, {"calm": True}),
    (34, "palace_hall", "day", [P("sj", "jking")], {36: "1443.12", 37: "언문 28자", 38: "1446 반포"}),
    (41, "study_room", "golden", [P("sch", "scholar")], {42: "1940 안동", 43: "해례본", 47: "국보"}),
    (49, "study_room", "night", [P("ban", "official", **BAN), P("hir", "official_red", **HIR)], {52: "반 노부토모", 53: "1850 출간", 54: ("hir", "1843 별세")}),
    (58, "study_room", "golden", [P("sch", "scholar")], {59: "첫째", 60: "1443", 64: "둘째"}),
    (69, "gate_court", "sunset", [P("hir", "official_red", **HIR), P("sch", "scholar"), P("ban", "official", **BAN)], {70: "히라타는?", 71: "반은?"}, {"holder": "sch"}),
    (73, "fortress_wall", "night", [P("ygs", "general", torso="#3a3a5a")], {74: "642 평양", 76: "대신 100여 명"}),
]
