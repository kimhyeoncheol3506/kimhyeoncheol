#!/usr/bin/env python3
"""월재스 영상 패턴 10종 (plans/영상패턴10.md) — 엔진 스타일 + 랜덤 선택.

  python3 patterns.py list                       # 10종 요약
  python3 patterns.py pick <에피소드폴더이름>       # 랜덤 1개 (직전 2편과 같은 패턴 금지, 경제2 비중) → research/pattern.json + 기록
  python3 patterns.py set <에피소드폴더이름> <번호>  # 직접 지정(기록에도 남김)
  python3 patterns.py show <번호>                  # 스타일 JSON

build.py project 가 에피소드의 research/pattern.json 을 읽어 project.json 의 "style"(neogul-edit)과
배경음악·효과음 프리셋·장면 기본값에 반영한다. 상시 원칙(월재스_제작원칙.md)은 모든 패턴에 그대로 적용.
"""
import json, os, random, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HISTORY = os.path.join(HERE, "pattern_history.json")

# 경제2(「쉽게 설명」) 비중: 2·3·8·9·10 높게. CEO 기업편 위주인 6은 낮게(경제1 몫).
WEIGHTS = {1: 1.0, 2: 2.0, 3: 2.0, 4: 1.0, 5: 1.2, 6: 0.5, 7: 0.8, 8: 2.0, 9: 2.0, 10: 2.0}


def _sub(text, box, alpha=0, align=2, mv=72, ml=40, bs=3, pad=9, size=50, bold=False, emph="#FFE14D", shadow=0):
    return {"font_size": size, "margin_v": mv, "margin_l": ml, "margin_r": ml, "align": align, "border_style": bs, "box_pad": pad,
            "bold": bold, "shadow": shadow,
            "normal": {"text": text, "box": box, "box_alpha": alpha},
            "emph": {"text": emph, "box": box, "box_alpha": alpha},
            "quote": {"text": "#111111", "box": "#FFE600", "box_alpha": 0}}


def _colors(bg, card, border, text, muted, accent, cream=None, cream_text="#161412", num_up=None, num_down=None, flash="#FFFFFF", mascot_cap=None, yellow=None):
    c = {"dark_bg": bg, "card_bg_dark": card, "card_border_dark": border, "text_dark_theme": text, "muted_dark": muted,
         "red": accent, "flash": flash}
    if cream:
        c.update({"cream_bg": cream, "text_cream_theme": cream_text})
    if num_up:
        c["red_num"] = num_up
    if num_down:
        c["blue_num"] = num_down
    if mascot_cap:
        c["mascot_caption"] = mascot_cap
    if yellow:
        c["yellow"] = yellow
    return c


PATTERNS = {
    1: {"name": "시사 썰 다큐", "ref": "슈카월드 'AI 데이터센터는 버블인가' (84만)", "minutes": "20~30",
        "flow": "이슈 → 역사 → 숫자 → 반론 → 앞으로", "visual": "지도·연표, 시네마 레터박스, 금색 포인트",
        "hook_mode": "title", "bgm": "bgm-cipher", "bgm_mode": "full", "bgm_volume": 0.045, "sfx": "basic",
        "grade_by_type": {"broll": ["cool", "vignette"], "pip": ["cool"]}, "mascot_mode": "text",
        "chrome": [{"kind": "tag", "text": "{series}", "x": 1824, "y": 980, "an": 9, "size": 24, "color": "#E3B341"}],
        "rules": {"colors": _colors("#0F1720", "#17212C", "#2A3645", "#F2F5F8", "#8FA0B3", "#E3B341", cream="#EEF1F4", num_up="#FF6B5A", num_down="#5FB4FF", flash="#0F1720", yellow="#E3B341"),
                  "subtitle": _sub("#FFFFFF", "#000000", alpha=0, bs=1, pad=3, shadow=2, size=48, bold=True),
                  "flash": {"after_broll": False}, "hook": {"kicker_color": "#E3B341"}}},
    2: {"name": "속보 반응", "ref": "너굴경제 '[속보] 젠슨황 복귀ㄷㄷ' (5분)", "minutes": "4~6",
        "flow": "무슨 일 → 왜 중요 → 내 계좌 영향 → 다음 체크", "visual": "하단 속보 바(LIVE), 뉴스 박스 제목, 빠른 컷",
        "hook_mode": "breaking", "bgm": "bgm-getting-it-done", "bgm_mode": "hook_outro", "bgm_volume": 0.07, "sfx": "tension",
        "grade": ["contrast"], "slide_defaults": {"title_style": "news"},
        "chrome": [{"kind": "bar", "pos": "bottom", "h": 64, "color": "#D7141A", "label": "속보", "label_bg": "#FFFFFF", "label_color": "#D7141A", "text": "{ticker}", "live": True}],
        "rules": {"colors": _colors("#111111", "#1D1D1D", "#333333", "#FFFFFF", "#A0A0A0", "#FF1F2D", cream="#F5F5F5", flash="#FFFFFF"),
                  "subtitle": _sub("#FFFFFF", "#000000", alpha=0, mv=96, size=50, bold=True),
                  "flash": {"duration": 0.25}, "hook": {"accent": "#D7141A"}}},
    3: {"name": "진짜 이유 파헤치기", "ref": "너굴경제 '엔비디아 이사회가 젠슨을 거부한 진짜 이유'", "minutes": "10~15",
        "flow": "발표 → 이상한 점 3개 → 숨은 이유", "visual": "사건 파일 오프닝, 증거 카드(종이색), 호박색 표시, 왼쪽 자막",
        "hook_mode": "case", "bgm": "bgm-investigations", "bgm_mode": "full", "bgm_volume": 0.05, "sfx": "tension",
        "grade_by_type": {"broll": ["vignette", "grain"], "pip": ["vignette"]},
        "chrome": [{"kind": "tag", "text": "EVIDENCE · {section}", "x": 1824, "y": 960, "an": 9, "size": 24, "color": "#12161C", "bg": "#F2A71B"}],
        "rules": {"colors": _colors("#12161C", "#1C222B", "#343C48", "#F4F1EA", "#9AA3AE", "#F2A71B", cream="#E9E1CF", cream_text="#1B1712", num_up="#FF5A4E", num_down="#6CB8FF", flash="#F2A71B", yellow="#F2A71B"),
                  "subtitle": _sub("#FFFFFF", "#0B0E12", alpha=40, align=1, ml=96, mv=70, size=48),
                  "hook": {"accent": "#C8102E"}}},
    4: {"name": "몰락의 전말", "ref": "경제꽈배기 'SM C&C 몰락의 전말'", "minutes": "15~20",
        "flow": "전성기 → 결정적 실수 → 숫자 붕괴 → 지금", "visual": "앞쪽 흑백·필름 그레인 → 뒤쪽 컬러, 진홍 박스",
        "hook_mode": "bw_title", "bgm": "bgm-decisions", "bgm_mode": "full", "bgm_volume": 0.05, "sfx": "tension",
        "grade_by_type": {"hook": ["bw", "grain"], "broll": ["grain"]}, "bw_until_section": 2, "mascot_mode": "text",
        "chrome": [{"kind": "letterbox", "h": 44}],
        "rules": {"colors": _colors("#0E0E0E", "#1A1A1A", "#333333", "#F2F2F2", "#9A9A9A", "#B3001B", cream="#EDEDED", num_up="#E0203A", num_down="#7A9CC6", flash="#000000"),
                  "subtitle": _sub("#FFFFFF", "#B3001B", alpha=0, mv=80, size=48, bold=True, emph="#FFFFFF"),
                  "flash": {"after_broll": False}, "hook": {"accent": "#B3001B"}}},
    5: {"name": "생활 속 돈벌이 비밀", "ref": "더시프트 '그 많던 터미널은 어디로 갔나'", "minutes": "15~20",
        "flow": "일상 의문 → 돈 흐름 추적 → 누가 버나 → 상장사 연결(사실만)", "visual": "밝은 크림 화면, 초록 포인트, 노란 자막 박스, 물음표 오프닝",
        "hook_mode": "question", "bgm": "bgm-easy-lemon", "bgm_mode": "full", "bgm_volume": 0.06, "sfx": "money",
        "chrome": [{"kind": "side_stripe", "w": 16, "color": "#19A974"}],
        "rules": {"colors": _colors("#FFF8EC", "#FFFFFF", "#E7DCC8", "#1F2A24", "#7A7468", "#19A974", cream="#EAF6EF", num_up="#E8453C", num_down="#1F7AE0", flash="#BFF0D4", yellow="#F5B700"),
                  "subtitle": _sub("#111111", "#FFE14D", alpha=0, mv=70, size=48, bold=True, emph="#C8102E"),
                  "mascot": {"bg": "#FFF8EC"}, "hook": {"accent": "#19A974", "card": "#FFF6D6"}}},
    6: {"name": "가문·인물 드라마", "ref": "더시프트 '구찌 가문 몰락의 전말'", "minutes": "15~20",
        "flow": "등장인물 → 갈등 → 결정적 장면 → 남은 것", "visual": "관계도, 드라마 자막(레터박스 안), 갈색·금색, 따뜻한 색보정",
        "hook_mode": "family", "bgm": "bgm-decisions", "bgm_mode": "full", "bgm_volume": 0.05, "sfx": "basic",
        "grade_by_type": {"broll": ["warm", "vignette"], "hook": ["warm"]}, "mascot_mode": "text",
        "chrome": [{"kind": "letterbox", "h": 80}],
        "rules": {"colors": _colors("#1A120D", "#2A1D15", "#4A3526", "#F3E7D3", "#B39B7E", "#C9A45C", cream="#F3E7D3", cream_text="#2A1D15", num_up="#E06A4E", num_down="#7FB0C9", flash="#1A120D", yellow="#C9A45C"),
                  "subtitle": _sub("#F3E7D3", "#000000", alpha=0, bs=1, pad=2, shadow=2, mv=100, size=50),
                  "flash": {"after_broll": False}, "hook": {"kicker_color": "#C9A45C"}}},
    7: {"name": "대역전·라이벌전", "ref": "경제꽈배기 '한화의 대우조선 대역전'", "minutes": "12~18",
        "flow": "두 선수 소개 → 1라운드(격차) → 반격 → 역전 스코어 → 지금", "visual": "VS 분할 화면, 상단 스코어보드, 파랑·빨강",
        "hook_mode": "vs", "bgm": "bgm-getting-it-done", "bgm_mode": "full", "bgm_volume": 0.055, "sfx": "tension",
        "grade": ["contrast"],
        "chrome": [{"kind": "score", "left": "{left}", "right": "{right}", "y": 18}],
        "rules": {"colors": _colors("#0B1530", "#13224A", "#22346A", "#FFFFFF", "#8EA3D1", "#FFD21F", cream="#EEF2FF", num_up="#FF3B3B", num_down="#2F7BFF", flash="#FFD21F", yellow="#FFD21F"),
                  "subtitle": _sub("#FFFFFF", "#000000", alpha=0, bs=1, pad=4, mv=64, size=52, bold=True),
                  "slide": {"title_y": 120, "section_y": 96},
                  "hook": {"left_color": "#1F5FBF", "right_color": "#C8102E"}}},
    8: {"name": "다음 주 시장 변수", "ref": "삼프로TV '다음 주 증시 핵심 변수'", "minutes": "8~12",
        "flow": "이번 주 정리 → 변수 3개(날짜) → 시나리오 2개(권유 없이)", "visual": "캘린더 오프닝, 오른쪽 위 날짜 카드, 체크리스트, 남색·하늘색",
        "hook_mode": "calendar", "bgm": "bgm-cipher", "bgm_mode": "hook_outro", "bgm_volume": 0.06, "sfx": "basic",
        "chrome": [{"kind": "calendar", "month": "{month}", "day": "{day}", "color": "#3DA9FC"}],
        "rules": {"colors": _colors("#0E1A2B", "#16263D", "#26405F", "#F2F7FC", "#8AA2BF", "#3DA9FC", cream="#EEF4FA", cream_text="#0E1A2B", num_up="#FF5D5D", num_down="#3DA9FC", flash="#BFE3FF", yellow="#3DA9FC"),
                  "subtitle": _sub("#FFFFFF", "#0E1A2B", alpha=30, mv=72, size=48),
                  "hook": {"accent": "#3DA9FC"}}},
    9: {"name": "수혜·피해 지도", "ref": "삼프로TV '…가장 먼저 오를 주식은?' 형식을 업종 지도·과거 사례로만", "minutes": "10~14",
        "flow": "사건 → 돈이 움직이는 길(업종 지도) → 과거 사례 숫자 → 체크할 변수 (종목 추천 금지)", "visual": "초록 격자 지도, 수혜(초록)·피해(빨강) 범례, 왼쪽 자막",
        "hook_mode": "map_money", "bgm": "bgm-local-forecast-elevator", "bgm_mode": "hook_outro", "bgm_volume": 0.06, "sfx": "money",
        "chrome": [{"kind": "grid", "step": 96, "color": "#22C55E", "alpha": 0.06}, {"kind": "tag", "text": "▲수혜  ▼피해  (업종·과거 사례)", "x": 1824, "y": 30, "an": 9, "size": 22, "color": "#9BE7A8", "bg": "#0F1A12"}],
        "rules": {"colors": _colors("#0F1A12", "#16261A", "#294330", "#F0F7F1", "#8FAF96", "#22C55E", cream="#EEF7EF", cream_text="#0F1A12", num_up="#22C55E", num_down="#EF4444", flash="#22C55E", yellow="#22C55E"),
                  "subtitle": _sub("#FFFFFF", "#123A1F", alpha=0, align=1, ml=96, mv=70, size=48),
                  "hook": {"accent": "#22C55E"}}},
    10: {"name": "나라·거시 위기 스토리", "ref": "너굴경제 '국가부채를 숨기다 걸려 파산위기' (30만) · '갚으려고 했는데 안 받아줘서 파산' (41만)", "minutes": "14~18",
         "flow": "그 나라에 무슨 일 → 빚이 쌓인 길 → 터진 날 → 지금과 우리", "visual": "세계지도 격자·깜빡이는 핀, 오른쪽 위 부채 시계, 남색·경고 빨강",
         "hook_mode": "map", "bgm": "bgm-investigations", "bgm_mode": "full", "bgm_volume": 0.045, "sfx": "tension",
         "grade_by_type": {"broll": ["cool", "vignette"]},
         "chrome": [{"kind": "grid", "step": 120, "color": "#7FB8FF", "alpha": 0.05}, {"kind": "clock", "label": "{clock_label}", "unit": "{clock_unit}", "per_sec": 1234.5}],
         "rules": {"colors": _colors("#06121F", "#0D2236", "#1D3A57", "#EAF2FA", "#86A0BA", "#FF5A4E", cream="#E8EEF4", cream_text="#06121F", num_up="#FF5A4E", num_down="#5FB4FF", flash="#FF5A4E", yellow="#FFB020"),
                   "subtitle": _sub("#FFFFFF", "#3A0D0D", alpha=60, mv=72, size=48, bold=True),
                   "hook": {"accent": "#FF5A4E"}}},
}

# 패턴별 기본 변수(에피소드 pattern.json 의 vars 로 덮어씀). 샘플·미입력 대비 값이며, 실제 편에서는 확인된 사실로 채운다.
DEFAULT_VARS = {
    1: {"series": "월재스 시사 썰", "kicker": "월재스 다큐"},
    2: {"ticker": "{section}", "flash_label": "속보"},
    3: {"case_no": "CASE FILE · 월재스", "stamp": "진짜 이유?"},
    4: {"kicker": "몰락의 전말"},
    5: {},
    6: {"kicker": "가문의 이야기"},
    7: {"left": "A", "right": "B", "kicker": "대역전"},
    8: {"month": "12월", "day": "8"},
    9: {"kicker": "수혜 · 피해 지도"},
    10: {"clock_label": "부채 시계(설명용)", "clock_unit": "", "clock_base": 38000000, "pin_x": 1300, "pin_y": 420},
}


def style_for(pid, vars_=None):
    p = PATTERNS[int(pid)]
    v = dict(DEFAULT_VARS.get(int(pid), {}))
    v.update(vars_ or {})
    st = {"pattern": int(pid), "name": p["name"], "hook_mode": p["hook_mode"], "rules": p["rules"], "chrome": p.get("chrome", []), "vars": v}
    for k in ("grade", "grade_by_type"):
        if p.get(k):
            st[k] = p[k]
    return st


def load_history():
    return json.load(open(HISTORY, encoding="utf-8")) if os.path.exists(HISTORY) else []


def save_history(h):
    json.dump(h, open(HISTORY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def pick(ep, seed=None):
    h = load_history()
    banned = {x["pattern"] for x in h[-2:]}
    pool = [k for k in PATTERNS if k not in banned]
    rnd = random.Random(seed)
    pid = rnd.choices(pool, weights=[WEIGHTS[k] for k in pool])[0]
    return set_pattern(ep, pid, h)


def set_pattern(ep, pid, h=None):
    h = load_history() if h is None else h
    ep_dir = os.path.join(ROOT, ep)
    os.makedirs(os.path.join(ep_dir, "research"), exist_ok=True)
    f = os.path.join(ep_dir, "research", "pattern.json")
    old = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
    d = {"pattern": int(pid), "name": PATTERNS[int(pid)]["name"], "vars": old.get("vars", {})}
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    h = [x for x in h if x["ep"] != ep] + [{"ep": ep, "pattern": int(pid), "date": datetime.date.today().isoformat()}]
    save_history(h)
    print("[pattern] %s → %d %s (%s분, %s)" % (ep, pid, PATTERNS[pid]["name"], PATTERNS[pid]["minutes"], PATTERNS[pid]["flow"]))
    return int(pid)


def episode_pattern(ep_dir):
    """build.py용: (pattern 정의, style) 또는 (None, None)."""
    pid = os.environ.get("PATTERN")
    vars_ = {}
    f = os.path.join(ep_dir, "research", "pattern.json")
    if os.path.exists(f):
        d = json.load(open(f, encoding="utf-8"))
        pid = pid or d.get("pattern")
        vars_ = d.get("vars", {})
    if not pid:
        return None, None
    return PATTERNS[int(pid)], style_for(pid, vars_)


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "list"
    if c == "list":
        for k, p in PATTERNS.items():
            print("%2d %-12s %6s분  오프닝=%-9s BGM=%-28s %s" % (k, p["name"], p["minutes"], p["hook_mode"], p["bgm"] + "/" + p["bgm_mode"], p["flow"]))
    elif c == "pick":
        pick(sys.argv[2])
    elif c == "set":
        set_pattern(sys.argv[2], int(sys.argv[3]))
    elif c == "show":
        print(json.dumps(style_for(int(sys.argv[2])), ensure_ascii=False, indent=1))
