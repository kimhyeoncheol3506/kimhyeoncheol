import json
LEE = {"type":"general","torso":"#2f4f86"}
def A(id_, base, **k):
    d = {"id": id_, **base}; d.update(k); return d
def C(id_, type_, **k):
    d = {"id": id_, "type": type_, "z":1.0, "scale":1.0, "face":0.0, "dir":1, "pose":"stand", "expr":"neutral"}; d.update(k); return d
def L(id_, **k): return C(id_, "general", torso="#2f4f86", **k)
S = []
def sc(id_, w, set_, mood, cast, keys, acts, **k):
    d = {"id": id_, "start_word": w, "set": set_, "mood": mood, "cast": cast,
         "keys": [{"w": a, "frame": b} for a, b in keys], "acts": acts}; d.update(k); S.append(d)
def act(w, who, **k): d = {"w": w, "who": who}; d.update(k); return d

# 0 hook: 군대가 칼끝을 돌려 수도로 (0-4.7s)
sc("hook", 0, "river_camp", "night",
   [L("lee", x=540, y=1760, scale=1.15, dir=-1, pose="point", expr="angry", face=0.2),
    C("s1","soldier", x=250, y=1690, scale=0.95, face=0.3, pose="hold", expr="shocked"),
    C("s2","soldier", x=840, y=1690, scale=0.95, face=-0.3, dir=-1, pose="hold", expr="angry")],
   [(0, [540, 1180, 820]), (3, "lee"), (5, "all"), (9, "lee:full")],
   [act(0, "lee", hold="sign:개경으로!", pose="hold", dir=1),
    act(5, "s2", pose="cheer"), act(5, "s1", expr="angry"),
    act(9, "lee", pose="point", dir=-1, expr="angry")])
# 1 지도: 위화도 (4.7-9.4)
sc("map_wihwa", 11, "map_table_late", "night",
   [], [(11, [430, 560, 800]), (13, [450, 600, 800]), (15, [440, 590, 800])], [])
# 2 갇힌 군대 + 보낸 사람 (9.4-16.9)
sc("trapped", 18, "river_camp", "night",
   [L("lee", x=540, y=1760, scale=1.1, face=0.0, pose="arms_crossed", expr="sad"),
    C("s1","soldier", x=240, y=1690, scale=0.95, face=0.3, pose="stand", expr="scared"),
    C("s2","soldier", x=840, y=1690, scale=0.95, face=-0.3, dir=-1, pose="stand", expr="sad")],
   [(18, "all"), (21, [540, 1000, 900]), (24, "s1"), (26, "lee"), (28, "lee:full")],
   [act(21, "s1", look=[0.5, -1]), act(26, "lee", pose="think", expr="deadpan"),
    act(32, "lee", pose="hold", hold="sign:우왕·최영", expr="neutral")])
# 3 재훅1: 시작부터 이상 / 반대한 신하가 죽었다 (16.9-22.8)
sc("strange", 34, "study_room", "night",
   [C("ja","official_red", x=470, y=1700, scale=1.05, face=0.2, pose="stand", expr="sad")],
   [(34, [600, 1150, 1400]), (37, "ja"), (39, "ja:full")],
   [act(37, "ja", pose="hold", hold="sign:태조실록", expr="neutral"),
    act(39, "ja", pose="stand", expr="scared", look=[0, -1])])
# 4 명의 통보, 정벌 결정 (22.8-29.8)
sc("ming", 42, "palace_hall", "interior",
   [C("king","jking", x=540, y=1560, face=0.0, pose="stand"),
    C("choe","general", x=270, y=1720, scale=1.05, face=0.4, pose="arms_crossed"),
    C("off","official", x=820, y=1720, scale=1.0, face=-0.4, dir=1, pose="hold", hold="sign:명 황제 통보")],
   [(42, "off"), (45, "king"), (48, "all"), (50, "choe"), (52, "two")],
   [act(45, "king", expr="shocked"), act(48, "king", pose="point", expr="angry", talk=True),
    act(50, "choe", pose="hold", hold="sign:요동 정벌", expr="angry"),
    act(52, "king", pose="cheer", expr="angry")])
# 5 이자송 (29.8-34.5)
sc("jason", 55, "study_room", "night",
   [C("ja","official_red", x=300, y=1700, scale=1.0, face=0.4, pose="stand"),
    C("choe","general", x=640, y=1700, scale=1.05, face=-0.4, dir=-1, pose="arms_crossed", expr="angry")],
   [(55, "ja"), (57, "two"), (59, "choe"), (61, "ja"), (63, "ja:full")],
   [act(55, "ja", pose="point", expr="angry", talk=True),
    act(59, "choe", pose="point", expr="angry", talk=True), act(59, "ja", pose="stand", expr="shocked"),
    act(61, "ja", pose="hold", hold="sign:곤장·유배", expr="sad"),
    act(63, "ja", pose="stand", expr="sad", look=[0, 1])])
# 6 4불가론 (34.5-46.5)
sc("four", 65, "palace_hall", "interior",
   [C("king","jking", x=540, y=1560, pose="arms_crossed", expr="deadpan"),
    L("lee", x=800, y=1720, scale=1.05, face=-0.4, dir=-1, pose="stand")],
   [(65, "lee"), (68, "lee:full"), (72, [900, 1300, 900]), (77, [900, 1300, 850]), (80, [900, 1300, 900]), (83, [900, 1300, 850]), (86, "lee:full"), (88, "king")],
   [act(65, "lee", pose="point", talk=True, expr="deadpan"),
    act(72, "lee", pose="hold", hold="sign:소국→대국", dir=1, talk=True),
    act(77, "lee", hold="sign:여름 출병", talk=True),
    act(80, "lee", hold="sign:왜구 침입", talk=True),
    act(83, "lee", hold="sign:장마·역병", talk=True),
    act(87, "lee", hold="sign:4불가론", talk=False, expr="neutral"),
    act(88, "king", pose="stand", expr="happy")])
# 7 그날 밤 최영 (46.5-52.1)
sc("night_choe", 91, "palace_hall", "night",
   [C("king","jking", x=620, y=1560, face=-0.2, dir=-1, pose="stand"),
    C("choe","general", x=300, y=1720, scale=1.05, face=0.4, pose="stand", expr="deadpan")],
   [(91, [540, 900, 1400]), (94, "choe"), (96, "two"), (98, "choe:full"), (100, "king")],
   [act(94, "choe", pose="walk", x=380, dur=1.2),
    act(98, "choe", pose="point", talk=True, expr="angry"),
    act(100, "king", expr="deadpan", look=[-1, 0])])
# 8 경고가 현실로: 익사, 도망, 베라 (52.1-64.7)
sc("flood", 102, "river_camp", "night",
   [L("lee", x=380, y=1760, scale=1.1, face=0.3, pose="arms_crossed", expr="sad"),
    C("s1","soldier", x=700, y=1700, scale=0.95, face=-0.3, dir=-1, pose="stand", expr="scared"),
    C("s2","soldier", x=880, y=1670, scale=0.9, face=-0.3, dir=-1, pose="stand", expr="sad"),
    C("msg","official", x=-200, y=1740, scale=1.0, face=0.3, pose="walk")],
   [(102, "all"), (105, "lee"), (108, [560, 1080, 760]), (111, [560, 1100, 1100]), (113, "s1"), (116, "two"), (119, "all"), (121, [760, 1330, 900])],
   [act(105, "lee", look=[1, -0.5]),
    act(111, "s1", pose="hold", hold="sign:익사 수백", expr="sad"),
    act(116, "s2", pose="run", x=1200, dur=1.6, expr="scared"),
    act(117, "s1", pose="run", x=1150, dur=2.0, expr="scared"),
    act(119, "msg", pose="walk", x=700, dur=1.5),
    act(121, "msg", pose="hold", hold="sign:왕명: 베어라", dir=1, expr="angry"),
    act(121, "lee", expr="shocked")])
# 9 회군 요청 → 김완 독촉 (64.7-72.0)
sc("kimwan", 125, "river_camp", "night",
   [L("lee", x=300, y=1760, scale=1.1, face=0.3, pose="hold", hold="sign:회군 요청", expr="sad"),
    C("kw","official", x=1250, y=1740, scale=1.0, face=-0.3, dir=-1, pose="walk")],
   [(125, "lee"), (128, "lee:full"), (132, [700, 1200, 1300]), (134, "kw"), (136, "two")],
   [act(131, "kw", x=780, dur=1.4, pose="walk"),
    act(134, "kw", pose="hold", hold="sign:진군하라!", expr="angry", talk=True, dir=1),
    act(136, "lee", pose="stand", expr="angry")])
# 10 재훅2 (72.0-75.7)
sc("rehook2", 139, "river_camp", "night",
   [L("lee", x=540, y=1760, scale=1.15, pose="think", expr="deadpan")],
   [(139, [540, 1300, 1300]), (141, "lee"), (144, [560, 1330, 900])],
   [act(144, "lee", expr="sly", look=[0.5, 0])])
# 11 회군 (75.7-86.7) golden
sc("turn", 147, "river_camp", "golden",
   [L("lee", x=540, y=1760, scale=1.15, pose="point", expr="angry", dir=-1),
    C("kw","official", x=860, y=1740, scale=1.0, face=-0.3, dir=-1, pose="stand", expr="scared"),
    C("s1","soldier", x=240, y=1690, scale=0.95, face=0.3, pose="hold", expr="shocked")],
   [(147, "all"), (148, "kw"), (151, "lee"), (154, "lee:full"), (155, [540, 1250, 1300]), (161, "s1"), (164, "all")],
   [act(148, "kw", pose="shrug", expr="scared"),
    act(151, "lee", pose="point", dir=-1, talk=True),
    act(154, "lee", pose="hold", hold="sign:회군!", dir=1, expr="angry", talk=False),
    act(154, "s1", pose="cheer", expr="happy"),
    act(155, "s1", pose="hold", hold="sign:태조실록", expr="neutral"),
    act(161, "lee", pose="stand", expr="neutral", look=[-1, 0])], calm=True)
# 12 개경 성문 (86.7-94.8) day
sc("gaegyeong", 167, "fortress_wall", "day",
   [L("lee", x=760, y=1700, scale=1.05, face=-0.3, dir=-1, pose="walk"),
    C("s1","soldier", x=940, y=1690, scale=0.95, face=-0.3, dir=-1, pose="walk"),
    C("s2","soldier", x=1100, y=1690, scale=0.95, face=-0.3, dir=-1, pose="walk")],
   [(167, [600, 1150, 1500]), (169, [640, 1300, 1300]), (173, [560, 1310, 900]), (175, [780, 1300, 900]), (180, [700, 1300, 1200]), (182, [560, 1310, 950])],
   [act(167, "lee", x=520, dur=2.5, pose="walk"), act(167, "s1", x=740, dur=2.5), act(167, "s2", x=900, dur=2.5),
    act(170, "lee", pose="stand"), act(170, "s1", pose="stand"), act(170, "s2", pose="stand"),
    act(173, "lee", pose="hold", hold="sign:6월 1일", expr="neutral", dir=1),
    act(175, "s1", pose="hold", hold="sign:베라던 왕?", expr="angry", dir=1),
    act(180, "s1", pose="cheer", expr="laughing"), act(180, "s2", pose="cheer", expr="happy"),
    act(182, "lee", pose="point", expr="smug")])
# 13 최영과 우왕의 작별, 최후 (94.8-106.8) palace night
sc("farewell", 185, "palace_hall", "night",
   [C("choe","general", x=300, y=1720, scale=1.05, face=0.4, pose="point", expr="angry"),
    C("king","jking", x=760, y=1600, face=-0.3, dir=-1, pose="stand", expr="scared")],
   [(185, "choe"), (187, "two"), (188, "king"), (190, "two"), (194, [340, 1290, 900]), (197, [340, 1290, 850]), (200, [560, 1200, 900]), (203, "two")],
   [act(187, "choe", pose="stand", expr="sad"),
    act(188, "king", pose="walk", x=520, dur=1.4, expr="sad"),
    act(191, "king", pose="stand", expr="sad"),
    act(194, "choe", pose="hold", hold="sign:고봉현 유배", expr="sad", dir=1),
    act(197, "choe", hold="sign:그해 겨울", expr="sad"),
    act(200, "king", pose="hold", hold="sign:강화도로", expr="sad", dir=1),
    act(203, "king", expr="scared", look=[0, 1])])
# 14 조선 (106.8-111.3) gate_court dawn
sc("joseon", 206, "gate_court", "dawn",
   [C("lee","jking", x=540, y=1720, scale=1.05, pose="stand", expr="smug"),
    C("o1","official", x=280, y=1790, scale=0.95, face=0.4, pose="stand"),
    C("o2","official_red", x=800, y=1790, scale=0.95, face=-0.4, dir=-1, pose="stand")],
   [(206, [540, 1150, 1600]), (208, "all"), (210, [580, 1300, 900]), (212, "lee:full")],
   [act(208, "o1", pose="cheer", expr="happy"), act(208, "o2", pose="cheer", expr="happy"),
    act(210, "lee", pose="hold", hold="sign:1392 조선", expr="smug")])
# 15 두 가지 반전 + 철령위 (111.3-120.2)
sc("twist", 214, "study_room", "golden",
   [C("sch","scholar", x=460, y=1700, scale=1.05, face=0.2, pose="hold", hold="sign:반전 두 개", expr="sly")],
   [(214, [520, 1250, 900]), (216, "sch:full"), (220, [520, 1250, 900])],
   [act(220, "sch", hold="sign:명사 지리지", expr="neutral"), act(222, "sch", pose="point", expr="shocked")])
sc("tieling", 223, "map_table_late", "golden",
   [], [(223, [380, 560, 800]), (225, [360, 540, 800]), (227, [420, 580, 800]), (229, [400, 560, 800])], [], calm=True)
# 16 기록은 조선이 썼다 (120.2-125.5)
sc("records", 232, "study_room", "golden",
   [C("sch","scholar", x=460, y=1700, scale=1.05, face=0.2, pose="stand", expr="neutral")],
   [(232, "sch:full"), (236, [520, 1250, 850]), (240, [520, 1250, 950])],
   [act(236, "sch", pose="hold", hold="sign:고려사 1451"),
    act(238, "sch", hold="sign:실록 1413"),
    act(240, "sch", hold="sign:조선 편찬", expr="sly")])
# 17 백성 환영 = 승자의 기록 (125.5-129.8)
sc("welcome", 243, "village_road", "golden",
   [C("p1","peasant", x=360, y=1760, scale=1.0, face=0.3, pose="cheer", expr="happy"),
    C("p2","peasant", x=620, y=1760, scale=1.0, face=-0.3, dir=-1, pose="cheer", expr="laughing")],
   [(243, "two"), (246, "p1"), (249, "p2")],
   [act(249, "p2", pose="hold", hold="sign:승자의 기록", expr="deadpan", dir=1),
    act(249, "p1", pose="stand", expr="deadpan")])
# 18 재판: 변호 (129.8-141.7)
sc("defense", 252, "gate_court", "sunset",
   [C("dfn","scholar", x=200, y=1760, scale=1.0, face=0.4, pose="stand"),
    L("lee", x=450, y=1730, scale=1.05, pose="stand", expr="deadpan"),
    C("pro","official_red", x=710, y=1760, scale=1.0, face=-0.4, dir=-1, pose="arms_crossed", expr="deadpan")],
   [(252, [540, 900, 1500]), (253, "all"), (255, "dfn"), (257, [300, 1320, 900]), (262, [300, 1320, 900]), (266, [340, 1300, 1100]), (270, "dfn")],
   [act(255, "dfn", pose="point", talk=True, expr="smug"),
    act(257, "dfn", pose="hold", hold="sign:4불가론", talk=True),
    act(262, "dfn", hold="sign:회군 요청 2번", talk=True),
    act(266, "dfn", hold="sign:병사 귀환", talk=True, expr="happy"),
    act(266, "lee", expr="neutral")])
# 19 재판: 검사 (141.7-152.7)
sc("prosecution", 274, "gate_court", "sunset",
   [C("dfn","scholar", x=200, y=1760, scale=1.0, face=0.4, pose="arms_crossed", expr="deadpan"),
    L("lee", x=450, y=1730, scale=1.05, pose="stand", expr="deadpan"),
    C("pro","official_red", x=710, y=1760, scale=1.0, face=-0.4, dir=-1, pose="stand")],
   [(274, "pro"), (276, [800, 1320, 1000]), (281, [800, 1320, 1000]), (284, "lee"), (286, [800, 1320, 1000]), (290, [520, 1300, 900]), (293, "lee")],
   [act(274, "pro", pose="point", talk=True, expr="angry"),
    act(276, "pro", pose="hold", hold="sign:왕명 거역", dir=1, talk=True),
    act(281, "pro", hold="sign:최영·우왕 죽음", talk=True),
    act(284, "lee", expr="sad", look=[0, 1]),
    act(286, "pro", hold="sign:1392 즉위", talk=True),
    act(290, "lee", pose="hold", hold="sign:왕좌", expr="sly")])
# 20 판결 (152.7-end) river_camp sunset
sc("verdict", 296, "river_camp", "sunset",
   [L("lee", x=360, y=1760, scale=1.1, face=0.3, pose="arms_crossed", expr="neutral"),
    C("s1","soldier", x=640, y=1720, scale=1.0, face=0.2, pose="hold", hold="sign:결단?", expr="neutral")],
   [(296, [560, 1300, 1150]), (300, [600, 1320, 1000]), (303, [540, 1290, 1250])],
   [act(300, "s1", hold="sign:쿠데타?", expr="angry"),
    act(300, "lee", expr="sly"),
    act(303, "s1", hold="sign:판결은?", expr="deadpan"),
    act(303, "lee", pose="point", expr="deadpan", look=[0, 0])], calm=True)

sb = {"title": "위화도 회군: 결단인가 쿠데타인가", "fps": 30, "end_pad": 2.0, "lowercase": False, "scenes": S}
json.dump(sb, open("storyboard.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(S), "scenes")
