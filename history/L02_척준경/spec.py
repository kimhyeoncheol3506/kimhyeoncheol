# L02 척준경 장면 spec (auto_storyboard.py)
TITLE = "혼자 성문을 열어젖힌 장군은 왜 반역자가 되었나"
END_PAD = 2.5
CJK = dict(torso="#5a3a3a")          # 척준경
YG = dict(torso="#2f4f86")           # 윤관
JJS = dict()                          # 정지상(official_red)
LJG = dict(accent="#c8a020")         # 이자겸(official_red)
SEG = [
    (0, "palace_hall", "night", [P("jjs", "official_red"), P("injong", "jking", scale=0.9)], {2: "만세의 죄"}),
    (5, "sea_battle", "dawn", [P("cjk", "general", **CJK)], {5: "암타도 유배"}),
    (6, "study_room", "night", [P("sch", "scholar")], {7: "소드마스터?", 10: "반역열전"}),
    (13, "mountain_pass", "day", [P("yg", "general", **YG), P("s1", "soldier")], {14: "여진 정벌", 16: "17만 명", 17: "별무반"}),
    (18, "fortress_wall", "night", [P("cjk", "general", **CJK), P("s1", "soldier")], {23: "추장 여러 명"}),
    (26, "fortress_wall", "dawn", [P("cjk", "general", **CJK), P("yg", "general", **YG)], {27: "동북 9성"}),
    (28, "mountain_pass", "night", [P("yg", "general", **YG), P("e1", "enemy"), P("cjk", "general", **CJK)], {30: "가한촌 포위"}),
    (35, "village_road", "sunset", [P("of", "official")], {35: "9성 반환"}),
    (37, "palace_hall", "interior", [P("ljg", "official_red", **LJG), P("injong", "jking", scale=0.9)], {38: "1126", 40: "이자겸"}),
    (43, "palace_hall", "night", [P("cjk", "general", **CJK), P("ljg", "official_red", **LJG)], {43: "척준경"}),
    (46, "palace_hall", "night", [P("cjk", "general", **CJK)], {47: "궁궐 화재"}),
    (49, "palace_hall", "night", [P("injong", "jking", scale=0.9), P("csj", "official")], {}),
    (53, "study_room", "night", [P("csj", "official"), P("cjk", "general", **CJK)], {54: "역적? 공신?"}),
    (56, "gate_court", "day", [P("cjk", "general", **CJK), P("ljg", "official_red", **LJG)], {56: "1126.5"}),
    (59, "palace_hall", "interior", [P("jjs", "official_red"), P("injong", "jking", scale=0.9)], {61: "1127.3", 62: "만세의 죄"}),
    (65, "sea_battle", "dawn", [P("cjk", "general", **CJK)], {65: "암타도→곡주"}),
    (68, "study_room", "golden", [P("sch", "scholar")], {69: "첫째", 70: "묘청의 난"}, {"calm": True}),
    (72, "palace_hall", "golden", [P("injong", "jking", scale=0.9), P("cjk", "general", **CJK)], {72: "둘째 1144"}),
    (75, "study_room", "golden", [P("sch", "scholar")], {75: "반역열전"}),
    (76, "gate_court", "sunset", [P("cjk", "general", **CJK), P("sch", "scholar"), P("injong", "jking", scale=0.9)], {77: "영웅?반역자?", 78: "은인? 법?"}, {"holder": "sch"}),
    (80, "study_room", "dawn", [P("sch", "scholar")], {81: "1989 김해"}),
]
