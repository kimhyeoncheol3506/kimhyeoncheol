# -*- coding: utf-8 -*-
"""L01 대마도 storyboard 생성기 (8분 롱폼). 3초 규칙을 자동 보충한다."""
import json, itertools

W = json.load(open("words.json", encoding="utf-8"))
T = lambda w: W[min(w, len(W) - 1)]["s"]


def C(id_, type_, x, y=1720, **k):
    d = {"id": id_, "type": type_, "x": x, "y": y, "z": 1.0, "scale": 1.0, "face": 0.0, "dir": 1, "pose": "stand", "expr": "neutral"}
    d.update(k); return d


def L(id_, x, y=1720, **k):
    k.setdefault("torso", "#2f4f86"); return C(id_, "general", x, y, **k)


def SG(x, y=1720, h=950):  # 팻말 보기 좋은 프레임 (오른손 쪽)
    return [x + 110, y - 420, h]


S = []


def sc(id_, w, set_, mood, cast, keys, acts=(), **k):
    d = {"id": id_, "start_word": w, "set": set_, "mood": mood, "cast": cast,
         "keys": [{"w": a, "frame": b} for a, b in keys], "acts": [dict(w=a[0], who=a[1], **a[2]) for a in acts]}
    d.update(k); S.append(d)


def a(w, who, **k): return (w, who, k)


RHEE = dict(type="boss", torso="#2b2f3a", accent="#7a1f2b", hair="#d8d8d8")
YOSHIDA = dict(type="boss", torso="#4a4a52", accent="#2c3e50", hair="#3a3a3a")

# ---------------- 프롤로그 1949 (L0-11)
sc("p1949", 0, "office", "night",
   [C("rhee", RHEE.pop("type"), 540, 1700, **RHEE), C("rep", "cop", 230, 1720, torso="#6b6b6b", face=0.4), C("rep2", "worker", 850, 1720, face=-0.4, dir=-1)],
   [(0, [540, 1250, 900]), (3, "all"), (8, SG(540, 1700)), (10, "rhee"), (13, "all")],
   [a(0, "rhee", pose="point", expr="angry", talk=True), a(3, "rep", expr="shocked"), a(5, "rep2", expr="shocked", pose="hold", hold="sign:1949.1", dir=1),
    a(8, "rhee", pose="hold", hold="sign:대마도 반환", dir=1, expr="angry", talk=False), a(10, "rhee", pose="stand", expr="smug")])
sc("yoshida", 19, "office", "interior",
   [C("yos", "boss", 360, 1720, torso="#4a4a52", hair="#3a3a3a", face=0.3), C("mac", "cop", 760, 1720, torso="#9a8a5a", face=-0.3, dir=-1, pose="arms_crossed")],
   [(19, "yos"), (23, "two"), (26, "mac")],
   [a(19, "yos", pose="walk", x=480, dur=1.5, expr="scared"), a(22, "yos", pose="point", talk=True), a(24, "mac", pose="hold", hold="sign:GHQ", dir=1, expr="deadpan")])
sc("now", 30, "village_road", "dawn",
   [C("y1", "youth", 480, 1780, scale=0.9, face=0.2)],
   [(30, "y1"), (32, SG(480, 1780)), (35, "y1:full")],
   [a(30, "y1", pose="think", expr="sly"), a(32, "y1", pose="hold", hold="sign:나가사키현", dir=1, expr="sad"), a(35, "y1", pose="shrug", expr="deadpan")])
sc("dist", 38, "village_road", "day",
   [C("p1", "peasant", 360, 1760, face=0.3), C("p2", "youth", 600, 1780, face=-0.3, dir=-1, scale=0.85)],
   [(38, "two"), (41, SG(360, 1760)), (46, "p2"), (50, "two"), (53, SG(360, 1760)), (58, "two")],
   [a(38, "p1", pose="point", expr="happy", talk=True), a(41, "p1", pose="hold", hold="sign:약 50km", dir=1), a(46, "p2", pose="point", expr="shocked"),
    a(50, "p1", expr="smug"), a(53, "p1", hold="sign:규슈 2배+"), a(58, "p2", pose="think", expr="sly")])
sc("q", 61, "study_room", "night",
   [C("sch", "scholar", 460, 1700, face=0.2)],
   [(61, "sch"), (65, SG(460, 1700)), (68, "sch:full"), (72, SG(460, 1700))],
   [a(61, "sch", pose="think", expr="sly"), a(65, "sch", pose="hold", hold="sign:누구의 땅?", dir=1), a(68, "sch", expr="neutral"), a(72, "sch", hold="sign:600년", expr="smug")])

# ---------------- 1장 쌀이 없는 섬 (L12-19)
sc("ch1", 80, "mountain_pass", "day",
   [C("p1", "peasant", 400, 1760, face=0.3, expr="sad"), C("p2", "peasant", 680, 1760, face=-0.3, dir=-1, expr="sad", torso="#8a6a4a")],
   [(80, [540, 1100, 1700]), (86, "two"), (88, SG(400, 1760)), (91, "p2"), (95, "two"), (100, "p1"), (103, "p2")],
   [a(86, "p1", pose="point", look=[0, -1]), a(88, "p1", pose="hold", hold="sign:온통 산", dir=1), a(91, "p2", pose="shrug", expr="sad"),
    a(95, "p1", pose="think"), a(100, "p1", pose="walk", x=300, dur=1.4, expr="happy"), a(103, "p2", pose="point", expr="angry")])
sc("waegu", 107, "sea_battle", "night",
   [C("w1", "enemy", 380, 1740, face=0.3, expr="angry"), C("w2", "enemy", 700, 1740, face=-0.3, dir=-1, expr="sly")],
   [(107, "two"), (110, "w1"), (114, "w2")],
   [a(107, "w1", pose="point", talk=True), a(110, "w2", pose="cheer", expr="laughing"), a(114, "w1", pose="run", x=900, dur=1.5)])
sc("parkwi", 118, "sea_battle", "day",
   [L("pw", 540, 1750, torso="#5a3a7a")],
   [(118, "pw"), (121, SG(540, 1750)), (124, "pw:full"), (129, "pw")],
   [a(118, "pw", pose="point", expr="angry", talk=True), a(121, "pw", pose="hold", hold="sign:1389 박위", dir=1), a(124, "pw", pose="cheer", expr="happy"),
    a(129, "pw", pose="stand", expr="sad"), a(131, "pw", pose="think", expr="deadpan")])

# ---------------- 2장 상왕의 분노 (L20-32)
sc("ch2", 133, "village_road", "night",
   [C("v1", "peasant", 360, 1760, face=0.3, expr="scared"), C("w1", "enemy", 640, 1760, face=-0.3, dir=-1, expr="angry")],
   [(133, [540, 1150, 1600]), (138, "two"), (141, SG(360, 1760)), (147, "w1"), (150, "v1")],
   [a(138, "w1", pose="run", x=520, dur=1.2), a(139, "v1", pose="run", x=200, dur=1.2, expr="scared"), a(141, "v1", pose="hold", hold="sign:1419 비인현", dir=1),
    a(147, "w1", pose="cheer", expr="laughing"), a(150, "v1", pose="hold", hold="sign:병선 7척 불", expr="sad")])
sc("taejong", 152, "palace_hall", "interior",
   [C("tj", "jking", 540, 1560, accent="#c8a020"), C("sj", "jking", 830, 1720, scale=0.9, face=-0.3, dir=-1, expr="neutral")],
   [(152, "sj"), (155, "tj"), (160, "two"), (163, "tj"), (168, "tj:full"), (171, SG(540, 1560))],
   [a(152, "sj", pose="shrug"), a(155, "tj", pose="arms_crossed", expr="deadpan"), a(160, "tj", pose="point", expr="angry", talk=True),
    a(163, "sj", expr="scared"), a(168, "tj", expr="angry"), a(171, "tj", pose="hold", hold="sign:대마도를 친다", dir=1, expr="angry")])
sc("fleet", 173, "sea_battle", "day",
   [L("lee", 420, 1750), C("s1", "soldier", 720, 1740, face=-0.3, dir=-1)],
   [(173, SG(420, 1750)), (176, SG(420, 1750)), (180, "two"), (184, SG(420, 1750)), (188, "lee"), (193, "all"), (197, "s1")],
   [a(173, "lee", pose="hold", hold="sign:병선 227척", dir=1), a(176, "lee", hold="sign:17,285명"), a(180, "s1", pose="cheer", expr="happy"),
    a(184, "lee", hold="sign:6월 19일"), a(188, "lee", pose="point", expr="angry", talk=True), a(193, "s1", pose="run", x=900, dur=1.5, expr="angry"),
    a(197, "lee", pose="cheer", expr="laughing")])
sc("edict", 202, "study_room", "golden",
   [C("of", "official", 460, 1700, face=0.2)],
   [(202, "of:full"), (205, SG(460, 1700)), (211, SG(460, 1700, 880)), (214, "of"), (218, SG(460, 1700))],
   [a(202, "of", pose="point", talk=True), a(205, "of", pose="hold", hold="sign:7월 17일", dir=1), a(211, "of", hold="sign:본래 우리 땅", expr="smug"),
    a(214, "of", pose="cheer", expr="happy"), a(218, "of", pose="hold", hold="sign:세종실록", expr="neutral")], calm=True)

# ---------------- 3장 도장을 달라던 섬 (L33-44)
sc("ch3", 227, "palace_hall", "interior",
   [C("env", "enemy", 300, 1720, face=0.4, torso="#6a4a3a"), C("of", "official", 780, 1720, face=-0.4, dir=-1)],
   [(227, [540, 900, 1500]), (233, "env"), (240, "two"), (244, SG(300, 1720)), (249, "env"), (254, "of"), (256, SG(780, 1720))],
   [a(233, "env", pose="walk", x=380, dur=1.4), a(240, "of", expr="shocked"), a(244, "env", pose="hold", hold="sign:도장을 주소서", dir=1, talk=True),
    a(249, "env", pose="cheer", expr="happy"), a(254, "of", pose="point", talk=True), a(256, "of", pose="hold", hold="sign:경상도 소속", dir=1, expr="smug")])
sc("happy", 260, "gate_court", "day",
   [C("of", "official", 540, 1760)],
   [(260, "of"), (263, "of:full")],
   [a(260, "of", pose="cheer", expr="laughing"), a(263, "of", pose="stand", expr="shocked")])
sc("kurian", 263, "palace_hall", "night",
   [C("kr", "enemy", 300, 1720, face=0.4, torso="#3a3a5a", expr="deadpan"), C("of", "official_red", 780, 1720, face=-0.4, dir=-1)],
   [(263, "kr"), (266, SG(300, 1720)), (269, "kr"), (277, SG(300, 1720, 880)), (281, "of"), (285, "two"), (290, "kr"), (295, "of"), (299, "two")],
   [a(266, "kr", pose="hold", hold="sign:1421.4", dir=1), a(269, "kr", pose="point", talk=True), a(277, "kr", pose="hold", hold="sign:근거 없다", expr="smug"),
    a(281, "of", expr="angry"), a(285, "kr", pose="arms_crossed", expr="sly"), a(290, "of", pose="point", expr="angry", talk=True),
    a(295, "kr", pose="walk", x=-200, dur=2.0, expr="sad"), a(299, "of", pose="arms_crossed", expr="angry")])

# ---------------- 4장 칼 대신 쌀 (L45-53)
sc("ch4", 302, "study_room", "golden",
   [C("of", "official", 460, 1700, face=0.2)],
   [(302, "of"), (308, "of:full"), (315, SG(460, 1700)), (316, SG(460, 1700))],
   [a(302, "of", pose="think", expr="deadpan"), a(308, "of", pose="shrug"), a(315, "of", pose="hold", hold="sign:쌀", dir=1, expr="smug"),
    a(316, "of", hold="sign:1443 계해약조")], calm=True)
sc("treaty", 318, "gate_court", "day",
   [C("of", "official", 300, 1760, face=0.4), C("dm", "enemy", 780, 1760, face=-0.4, dir=-1, torso="#6a4a3a")],
   [(318, SG(300, 1760)), (325, "dm"), (329, SG(300, 1760)), (335, "two"), (338, SG(780, 1760)), (345, "of"), (349, "two")],
   [a(318, "of", pose="hold", hold="sign:배 50척", dir=1), a(325, "dm", pose="cheer", expr="happy"), a(329, "of", hold="sign:쌀 200석"),
    a(335, "of", pose="point", talk=True), a(338, "dm", pose="hold", hold="sign:허가증", dir=1, expr="smug"), a(345, "of", pose="arms_crossed", expr="smug"),
    a(349, "dm", expr="neutral")])
sc("rope", 354, "sea_battle", "dawn",
   [C("dm", "enemy", 540, 1750, torso="#6a4a3a")],
   [(354, "dm"), (357, SG(540, 1750)), (362, "dm:full"), (365, "dm")],
   [a(354, "dm", pose="think", expr="sly"), a(357, "dm", pose="hold", hold="sign:조선 쌀", dir=1), a(362, "dm", hold="sign:일본 영주", expr="deadpan"), a(365, "dm", pose="shrug", expr="sly")])

# ---------------- 5장 길잡이가 된 섬 (L54-63)
sc("ch5", 368, "fortress_wall", "night",
   [C("yt", "enemy", 420, 1680, face=0.3, expr="angry"), C("w2", "enemy", 700, 1690, face=-0.2, dir=-1, expr="angry")],
   [(368, [560, 1150, 1500]), (374, "two"), (379, SG(420, 1680)), (380, "yt"), (385, SG(420, 1680)), (390, "two"), (394, "yt")],
   [a(374, "w2", pose="run", x=860, dur=1.4), a(379, "yt", pose="hold", hold="sign:1592", dir=1), a(380, "yt", pose="point", talk=True),
    a(385, "yt", pose="hold", hold="sign:소 요시토시"), a(390, "w2", pose="cheer", expr="laughing"), a(394, "yt", pose="point", expr="sly")])
sc("forge", 399, "study_room", "night",
   [C("dm", "enemy", 460, 1700, torso="#6a4a3a", face=0.2)],
   [(399, "dm"), (408, SG(460, 1700)), (413, "dm:full"), (419, SG(460, 1700)), (424, "dm"), (430, "dm:full")],
   [a(399, "dm", pose="point", talk=True), a(403, "dm", expr="happy"), a(408, "dm", pose="hold", hold="sign:1609 기유약조", dir=1),
    a(413, "dm", pose="stand", expr="scared"), a(419, "dm", pose="hold", hold="sign:국서 위조", expr="sly"), a(424, "dm", pose="think", expr="sly"),
    a(430, "dm", pose="shrug", expr="deadpan")])

# ---------------- 6장 1872 (L64-70)
sc("ch6", 438, "office", "interior",
   [C("mj", "boss", 540, 1700, torso="#1f2a44", hair="#1a1a1a")],
   [(438, [540, 1250, 1200]), (442, "mj"), (446, SG(540, 1700)), (452, "mj:full"), (456, SG(540, 1700))],
   [a(442, "mj", pose="point", expr="deadpan", talk=True), a(446, "mj", pose="hold", hold="sign:명령 한 장", dir=1), a(452, "mj", pose="arms_crossed", expr="smug"),
    a(456, "mj", pose="hold", hold="sign:폐번치현")])
sc("izuhara", 460, "office", "interior",
   [C("mj2", "boss", 420, 1700, torso="#1f2a44", hair="#1a1a1a", face=0.3), C("dm", "enemy", 780, 1700, torso="#6a4a3a", face=-0.3, dir=-1)],
   [(460, SG(420, 1700)), (464, "dm"), (466, "two")],
   [a(460, "mj2", pose="hold", hold="sign:외교권 회수", dir=1, expr="smug"), a(463, "dm", expr="shocked"), a(466, "dm", pose="shrug", expr="sad")])
sc("nagasaki", 468, "office", "interior",
   [C("mj", "boss", 400, 1700, torso="#1f2a44", hair="#1a1a1a", face=0.3), C("dm", "enemy", 760, 1700, torso="#6a4a3a", face=-0.3, dir=-1)],
   [(468, SG(400, 1700)), (472, "two"), (475, SG(400, 1700)), (479, "dm"), (482, "two"), (487, "dm")],
   [a(468, "mj", pose="hold", hold="sign:1872 나가사키", dir=1), a(472, "dm", expr="sad"), a(475, "mj", hold="sign:왜관 접수"),
    a(479, "dm", pose="shrug", expr="sad"), a(482, "mj", pose="point", talk=True), a(487, "dm", pose="walk", x=1150, dur=2.2, expr="sad")])

# ---------------- 7장 1949 (L71-75)
sc("ch7", 493, "office", "night",
   [C("rhee", "boss", 400, 1700, torso="#2b2f3a", accent="#7a1f2b", hair="#d8d8d8", face=0.3), C("mac", "cop", 760, 1720, torso="#9a8a5a", face=-0.3, dir=-1, pose="arms_crossed")],
   [(493, [560, 1250, 1300]), (498, "rhee"), (502, SG(400, 1700)), (507, "rhee"), (511, SG(400, 1700)), (517, "mac"), (520, SG(760, 1720))],
   [a(498, "rhee", pose="point", expr="angry", talk=True), a(502, "rhee", pose="hold", hold="sign:1948.8", dir=1), a(507, "rhee", hold="sign:1949.1"),
    a(511, "rhee", hold="sign:국회 건의"), a(517, "mac", pose="shrug", expr="deadpan"), a(520, "mac", pose="hold", hold="sign:거절", dir=1, expr="deadpan"),
    a(521, "rhee", pose="stand", expr="sad")])

# ---------------- 반전 (L76-82)
sc("twist", 524, "study_room", "golden",
   [C("sch", "scholar", 460, 1700, face=0.2)],
   [(524, "sch:full"), (528, SG(460, 1700)), (533, "sch"), (538, SG(460, 1700, 880)), (543, "sch:full"), (548, "sch")],
   [a(524, "sch", pose="point", expr="sly", talk=True), a(528, "sch", pose="hold", hold="sign:첫째", dir=1), a(533, "sch", hold="sign:세종실록"),
    a(538, "sch", hold="sign:반박도 실림", expr="shocked"), a(543, "sch", pose="think", expr="neutral"), a(548, "sch", pose="cheer", expr="happy")], calm=True)
sc("twist2", 557, "sea_battle", "golden",
   [C("of", "official", 380, 1750, face=0.3), C("dm", "enemy", 720, 1750, face=-0.3, dir=-1, torso="#6a4a3a")],
   [(557, SG(380, 1750)), (562, "two"), (566, SG(380, 1750)), (571, "dm"), (576, "two"), (582, SG(380, 1750)), (587, "two")],
   [a(557, "of", pose="hold", hold="sign:둘째", dir=1), a(562, "of", pose="shrug", expr="deadpan"), a(566, "of", pose="hold", hold="sign:땅 대신 쌀"),
    a(571, "dm", pose="cheer", expr="happy"), a(576, "of", pose="point", talk=True), a(582, "of", pose="hold", hold="sign:왜구 감소", expr="smug"),
    a(587, "dm", pose="arms_crossed", expr="sly")])

# ---------------- 판결 (L83-86)
sc("verdict", 590, "gate_court", "sunset",
   [C("tj", "jking", 300, 1760, face=0.3, accent="#c8a020"), C("sch", "scholar", 540, 1780, scale=0.95), C("dm", "enemy", 800, 1760, face=-0.3, dir=-1, torso="#6a4a3a")],
   [(590, [540, 1150, 1600]), (595, "tj"), (600, SG(300, 1760)), (603, "tj"), (608, "dm"), (611, SG(540, 1780)), (614, "dm"), (617, SG(540, 1780))],
   [a(595, "tj", pose="think", expr="deadpan"), a(600, "sch", pose="hold", hold="sign:실수?", dir=1), a(603, "sch", hold="sign:지혜?"), a(603, "tj", expr="sly"),
    a(608, "dm", pose="shrug", expr="sad"), a(611, "sch", hold="sign:배신자?"), a(614, "sch", hold="sign:생존자?"), a(614, "dm", expr="sly"),
    a(617, "sch", hold="sign:당신의 판결")])

# ---------------- 다음 편 (L87-89)
sc("next", 622, "fortress_wall", "dawn",
   [L("cjk", 540, 1700, torso="#5a3a3a", face=0.2)],
   [(622, [560, 1150, 1600]), (626, "cjk"), (631, "cjk:full"), (636, "cjk"), (641, [560, 1300, 1000]), (645, "cjk")],
   [a(626, "cjk", pose="hold", hold="sign:고려", dir=1, expr="neutral"), a(631, "cjk", pose="cheer", expr="angry"), a(636, "cjk", pose="point", expr="angry"),
    a(628, "cjk", expr="sly"), a(633, "cjk", expr="happy"), a(638, "cjk", pose="stand", expr="neutral"), a(641, "cjk", pose="stand", expr="sad"), a(643, "cjk", dir=-1), a(645, "cjk", pose="think", expr="deadpan", look=[0, 1]), a(647, "cjk", expr="angry", dir=1), a(648, "cjk", pose="arms_crossed", expr="sad")])

# ---------------- 3초 규칙 자동 보충
CYC_E = itertools.cycle(["shocked", "angry", "sad", "sly", "deadpan", "happy", "neutral"])
CYC_P = itertools.cycle(["think", "stand", "point", "arms_crossed", "shrug"])
for i, s in enumerate(S):
    if not s["cast"]:
        continue
    w_end = S[i + 1]["start_word"] if i + 1 < len(S) else len(W)
    t_end = T(w_end) if w_end < len(W) else W[-1]["e"] + 4
    holders = {x["who"] for x in s["acts"] if "hold" in x}
    for _ in range(40):
        ts = sorted({T(s["start_word"])} | {T(x["w"]) for x in s["acts"]})
        ts.append(t_end)
        gap = max(zip(ts, ts[1:]), key=lambda p: p[1] - p[0])
        if gap[1] - gap[0] <= 2.8:
            break
        mid = (gap[0] + gap[1]) / 2
        w = min(range(s["start_word"], w_end), key=lambda k: abs(T(k) - mid))
        if T(w) <= gap[0] + 0.3:
            w = next((k for k in range(s["start_word"], w_end) if T(k) > gap[0] + 0.5), None)
            if w is None:
                break
        who = next((c["id"] for c in s["cast"] if c["id"] not in holders), s["cast"][0]["id"])
        s["acts"].append({"w": w, "who": who, "expr": next(CYC_E)} if who in holders else {"w": w, "who": who, "expr": next(CYC_E), "pose": next(CYC_P)})
    s["acts"].sort(key=lambda x: x["w"])

sb = {"title": "부산에서 보이는 섬은 왜 일본 땅이 되었나", "fps": 30, "end_pad": 2.5, "lowercase": False, "scenes": S}
json.dump(sb, open("storyboard.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(S), "scenes")
