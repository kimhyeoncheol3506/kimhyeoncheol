"""여의도 개미 표정·자세 48종 (v1.14.0). 이름은 대본에서 '이 문장엔 이 자세'를 고를 때 쓴다.
손 목표점은 가상 좌표(800x1000). 값의 뜻은 studio/mascot.py 위쪽 설명 참고."""
HL, HR = (266, 790), (534, 790)
BR = (-6, 6, 0)

POSES = {
    # ── 기본·기쁨 (8)
    "기본": dict(mouth="smile", hand_l=HL, hand_r=HR),
    "미소": dict(mouth="smile", brows=(3, -3, -4), hand_l=HL, hand_r=HR, fx=["blush"]),
    "환호": dict(mouth="grin", happy_eyes=True, hand_l=(205, 400), hand_r=(595, 400), antenna=14),
    "윙크": dict(mouth="smile", wink=True, hand_l=HL, hand_r=(610, 520)),
    "반짝": dict(mouth="grin", eyes="sparkle", hand_l=(300, 690), hand_r=(500, 690), front_l=True, front_r=True, fx=["sparkle"]),
    "으쓱": dict(mouth="smirk", brows=(4, -4, 0), hand_l=(205, 650), hand_r=(595, 650), bend_l=-1, bend_r=1),
    "자신감": dict(mouth="grin", brows=(4, -4, 0), hand_l=(262, 690), hand_r=(538, 690)),
    "승리": dict(mouth="grin", happy_eyes=True, hand_l=HL, hand_r=(585, 330), fx=["sparkle"]),
    # ── 놀람·불안 (8)
    "놀람": dict(mouth="o", eye_open=1.15, brows=(-8, 8, -14), hand_l=(205, 650), hand_r=(595, 650), bend_l=-1, bend_r=1, fx=["sweat"]),
    "충격": dict(mouth="wide", eye_open=1.2, brows=(-10, 10, -18), hand_l=(262, 380), hand_r=(538, 380), front_l=True, front_r=True, fx=["exclaim"]),
    "진땀": dict(mouth="wavy", brows=(-10, 10, -6), look=(1, 1), hand_l=(330, 700), hand_r=(470, 700), front_l=True, front_r=True, fx=["sweat"]),
    "걱정": dict(mouth="frown", brows=(-10, 10, -6), hand_l=(362, 650), hand_r=(438, 650), front_l=True, front_r=True, fx=["sweat"]),
    "당황": dict(mouth="small", eyes="dot", brows=(-6, 6, -8), hand_l=(230, 620), hand_r=(570, 620), bend_l=-1, bend_r=1, fx=["sweat", "question"]),
    "어지러움": dict(mouth="wavy", eyes="spiral", hand_l=HL, hand_r=HR, head_tilt=8),
    "뺨잡기": dict(mouth="wide", eye_open=1.1, brows=(-8, 8, -12), hand_l=(318, 430), hand_r=(482, 430), front_l=True, front_r=True),
    "머리감싸기": dict(mouth="grit", eyes="sad_closed", brows=(-12, 12, -4), hand_l=(270, 330), hand_r=(530, 330), front_l=True, front_r=True),
    # ── 슬픔·분노 (7)
    "슬픔": dict(mouth="frown", eye_open=0.7, brows=(-12, 12, -4), hand_l=(268, 792), hand_r=(532, 792), head_tilt=-6),
    "눈물": dict(mouth="frown", eyes="tear", brows=(-12, 12, -6), hand_l=HL, hand_r=HR),
    "포기": dict(mouth="flat", eyes="sad_closed", brows=(-8, 8, 2), hand_l=(270, 794), hand_r=(530, 794), head_tilt=-12),
    "화남": dict(mouth="flat", eye_open=0.75, brows=(14, -14, 4), hand_l=(262, 700), hand_r=(538, 700), fx=["vein"]),
    "버럭": dict(mouth="grit", eye_open=0.75, brows=(16, -16, 6), hand_l=(250, 640), hand_r=(550, 640), fx=["vein"]),
    "후회": dict(mouth="small", eyes="sad_closed", brows=(-10, 10, -2), hand_l=(300, 420), hand_r=(500, 420), front_l=True, front_r=True),
    # ── 생각·분석 (9)
    "고민": dict(mouth="flat", brows=BR, look=(1, -1), hand_l=(372, 515), hand_r=HR, arm_front=True),
    "갸웃": dict(mouth="small", brows=(-4, 6, -2), look=(1, -1), head_tilt=14, hand_l=(372, 515), hand_r=HR, arm_front=True, fx=["question"]),
    "의심": dict(mouth="flat", eye_open=0.8, brows=(8, -2, 0), look=(1, 0), hand_l=(250, 600), hand_r=HR, prop="magnifier"),
    "아이디어": dict(mouth="grin", eyes="sparkle", brows=(4, -4, -8), hand_l=HL, hand_r=(560, 560), fx=["bulb"]),
    "계산": dict(mouth="flat", look=(0, 1), brows=BR, hand_l=(344, 690), hand_r=HR, front_l=True, prop="calc", prop_hand="l"),
    "확인": dict(mouth="smile", look=(1, 0), hand_l=HL, hand_r=(570, 640), prop="chart"),
    "깨달음": dict(mouth="o", eyes="sparkle", brows=(-6, 6, -10), hand_l=HL, hand_r=(560, 560), fx=["bulb", "exclaim"]),
    # ── 설명·소통 (9)
    "설명": dict(mouth="smile", hand_l=HL, hand_r=(640, 570)),
    "가리킴": dict(mouth="smile", look=(1, 0), hand_l=HL, hand_r=(700, 640)),
    "위가리킴": dict(mouth="smile", look=(1, -1), hand_l=HL, hand_r=(600, 360)),
    "질문": dict(mouth="o", brows=(-4, 6, -6), hand_l=HL, hand_r=(580, 380), fx=["question"]),
    "인사": dict(mouth="smile", hand_l=HL, hand_r=(610, 470), antenna=10),
    "경고": dict(mouth="flat", brows=(6, -6, -4), hand_l=HL, hand_r=(610, 560), fx=["exclaim"]),
    "속삭임": dict(mouth="small", look=(-1, 0), hand_l=HL, hand_r=(452, 436), front_r=True),
    "박수": dict(mouth="grin", happy_eyes=True, hand_l=(382, 640), hand_r=(418, 640), front_l=True, front_r=True),
    "선언": dict(mouth="grin", brows=(6, -6, -2), hand_l=HL, hand_r=(560, 420)),
    # ── 경제 상황 (7)
    "상승": dict(mouth="grin", happy_eyes=True, hand_l=(205, 400), hand_r=(595, 400), fx=["up", "sparkle"]),
    "하락": dict(mouth="frown", eye_open=0.75, brows=(-12, 12, -6), hand_l=HL, hand_r=HR, head_tilt=-8, fx=["down"]),
    "탐욕": dict(mouth="grin", eyes="dollar", hand_l=(300, 690), hand_r=(500, 690), front_l=True, front_r=True),
    "수익": dict(mouth="smile", eyes="sparkle", hand_l=HL, hand_r=(590, 640), prop="stack"),
    "동전": dict(mouth="smile", hand_l=HL, hand_r=(585, 590), prop="coin"),
    "안전": dict(mouth="smile", brows=(3, -3, -4), hand_l=HL, hand_r=(560, 360), prop="umbrella"),
    "스마트폰": dict(mouth="small", look=(0, 1), brows=BR, hand_l=HL, hand_r=(552, 560), prop="phone"),
    # ── 일상·기다림 (3)
    "팔짱": dict(mouth="flat", brows=(5, -5, 0), hand_l=(452, 672), hand_r=(348, 672), front_l=True, front_r=True),
    "졸림": dict(mouth="small", eyes="sleep", hand_l=HL, hand_r=HR, head_tilt=-8, fx=["zzz"]),
    "출근": dict(mouth="smile", hand_l=HL, hand_r=(534, 760), prop="bag", prop_hand="r"),
}
