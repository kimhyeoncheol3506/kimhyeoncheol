TITLE = "1989년 나타난 신라 화랑의 비밀 일기, 진짜인가 가짜인가"
END_PAD = 2.5
PCH = dict(torso="#4a4038", hair="#d0d0d0")   # 박창화(boss)
SEG = [
    (0, "village_road", "night", [P("m1", "boss", torso="#5a4a3a"), P("y1", "youth", scale=0.85)], {0: "1989 김해", 2: "화랑세기"}),
    (3, "study_room", "night", [P("sch", "scholar")], {4: "진짜라면?", 5: "가짜라면?"}),
    (6, "office", "interior", [P("pch", "boss", **PCH)], {6: "일본 궁내성"}),
    (8, "palace_hall", "interior", [P("king", "jking"), P("kdm", "official")], {11: ("kdm", "삼국사기"), 12: ("kdm", "김대문")}),
    (14, "study_room", "golden", [P("sch", "scholar")], {14: "인용 한 구절"}, {"calm": True}),
    (17, "village_road", "dusk" if False else "sunset", [P("sch", "scholar")], {17: "자취 감춤"}),
    (20, "office", "night", [P("pch", "boss", **PCH), P("st", "youth", scale=0.9)], {21: "박창화", 22: "1889~1962", 24: ("st", "제자의 집")}),
    (25, "study_room", "night", [P("sch", "scholar")], {25: "발췌본 32쪽", 26: "162쪽 모본"}),
    (28, "palace_hall", "night", [P("mis", "queen"), P("king", "jking"), P("hr", "general", torso="#7a3a5a")], {30: ("hr", "풍월주 32명"), 32: "미실"}),
    (38, "gate_court", "day", [P("pro", "scholar"), P("opp", "official_red")], {39: "진서설", 41: "향가"}),
    (45, "gate_court", "night", [P("opp", "official_red"), P("pro", "scholar")], {46: "위서설", 50: "한문 소설", 55: "공개 안 함"}),
    (56, "study_room", "golden", [P("sch", "scholar")], {57: "첫째 종이", 58: "궁내성 용지"}, {"calm": True}),
    (62, "study_room", "golden", [P("sch", "scholar")], {62: "둘째", 63: "백과사전", 64: "논란 계속"}),
    (65, "gate_court", "sunset", [P("pch", "boss", **PCH), P("sch", "scholar"), P("opp", "official_red")], {66: "기록?창작?", 67: "역사?소설?"}, {"holder": "sch"}),
    (69, "village_road", "dawn", [P("y1", "youth", scale=0.9)], {70: "새 나라 이름"}),
]
