#!/usr/bin/env python3
"""영상 패턴 10종 샘플: 패턴마다 10초짜리 mp4(오프닝 3.4초 + 본문 슬라이드 2장, 패턴 배경음악 포함)를 렌더하고
오프닝·본문 스틸을 한 장(그리드)으로 모은다.

  python3 pattern_samples.py <출력폴더> <이미지폴더(에피소드 작업폴더들의 상위, wolje)> [번호,번호...]

샘플 문구는 이미 출처를 확인한 월재스 편의 숫자만 쓴다(01·06·07·10·13편 facts.md).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
NEOGUL = os.path.join(REPO, ".claude", "skills", "neogul-edit", "scripts", "neogul_edit.py")
sys.path.insert(0, HERE)
import patterns  # noqa: E402

FONT = os.path.join(REPO, ".claude", "skills", "neogul-edit", "scripts", "fonts", "Pretendard-ExtraBold.otf")

# 패턴별 샘플: (이미지 에피소드, 이미지 파일, 헤드라인 2줄, vars, 본문 장면 2개, 자막 3줄)
S = {
    1: ("07_반도체와구글", "hook.png", ["AI 반도체, 버블일까?", "수출의 절반이 한 품목"], {},
        [{"section": "3. 숫자로 보면", "title": "전체 수출 중 반도체 비중", "subtitle": "2026년 9월, 한국 수출", "source": "자료: 산업통상부(2026-10-01)",
          "bignum": {"value": "49.9", "unit": "%", "caption": "2025년 한국 반도체 수출 1,734억 달러", "color": "yellow"}},
         {"section": "4. 반론", "title": "그때와 지금, 무엇이 다른가", "bullets": ["2000년 닷컴버블 — 이익 없는 기대", "2026년 — 실제 수출 숫자가 있다", "하지만 한 품목 쏠림은 그대로"], "build_step": 0.5}],
        ["AI 데이터센터, 정말 버블일까요?", "수출의 절반이 반도체 한 품목입니다.", "그때와 지금은 무엇이 다를까요?"]),
    2: ("04_환율IMF수준", "hook.png", ["한국은행, 기준금리 인상", "3.25% · 2026년 11월 26일"], {"ticker": "한국은행 기준금리 3.25%로 인상 (11/26)"},
        [{"section": "1. 무슨 일", "title": "한은 금리 인상, 내 대출은?", "source": "자료: 한국은행·뉴스1(2026-11-26)",
          "cards": [{"label": "기준금리", "value": "3.25", "unit": "%", "color": "red", "caption": "11월 26일 인상"}, {"label": "원·달러", "value": "1,342.7", "unit": "원", "color": "blue", "caption": "11월 25일 종가"}, {"label": "다음 FOMC", "value": "12/8~9", "color": "yellow", "caption": "미국 금리 결정"}],
          "highlights": [{"target": "card:0", "at": 1.0}]},
         {"section": "3. 다음 체크", "title": "다음에 볼 것", "bullets": ["12월 8~9일 미국 FOMC", "내 대출 금리 변경 주기", "원·달러 환율 방향"], "build_step": 0.4}],
        ["방금 한국은행이 금리를 올렸습니다.", "내 대출에는 언제 반영될까요?", "다음에 볼 날짜는 12월 8일입니다."]),
    3: ("12_레버리지ETF", "hook.png", ["블로그 글 하나에", "왜 6% 넘게 빠졌을까?"], {"stamp": "진짜 이유?"},
        [{"section": "2. 이상한 점", "title": "이상한 점 3가지", "theme": "cream", "bullets": ["① 상품이 아니라 논문 단계의 연구", "② 그런데 이틀 뒤 SK하이닉스 -6.23%", "③ 석 달 뒤엔 87만 3천 원"], "build_step": 0.5,
          "highlights": [{"target": "bullet:1", "at": 1.6}]},
         {"section": "3. 숨은 이유", "title": "발표 이틀 뒤, 서울", "source": "자료: 한국거래소 종가(2026-03-26)",
          "bars": [{"label": "삼성전자", "value": 4.71, "text": "-4.71%", "color": "blue_num"}, {"label": "SK하이닉스", "value": 6.23, "text": "-6.23%", "color": "red_num", "strong": True}]}],
        ["실적도 그대로인데 왜 6% 넘게 빠졌을까요?", "이상한 점이 세 가지 있습니다.", "두 번째가 핵심이에요."]),
    4: ("06_테마주폭락", "hook.png", ["원전 대표주, 고점 대비", "-91%의 전말"], {"kicker": "몰락의 전말"},
        [{"section": "1. 전성기", "title": "사상 최고가", "source": "자료: 모틀리풀·24/7 Wall St.(2026-11-25)",
          "bignum": {"value": "193.84", "unit": "달러", "caption": "2025년 10월 사상 최고가", "color": "yellow"}},
         {"section": "3. 숫자 붕괴", "title": "그리고 지금", "source": "자료: 모틀리풀·24/7 Wall St.(2026-11-25)",
          "bignum": {"value": "-91", "unit": "%", "caption": "193.84 → 17.60달러", "color": "red_num"}}],
        ["한때 가장 뜨거웠던 원전주였습니다.", "결정적 실수는 무엇이었을까요?", "고점 대비 91%가 사라졌습니다."]),
    5: ("05_초대형IPO", "hook.png", ["공모주 청약,", "증권사는 뭘로 벌까?"], {},
        [{"section": "1. 일상 의문", "title": "청약 버튼 뒤의 돈 흐름", "cards": [{"text": "청약\n증거금"}, {"text": "인수\n수수료"}, {"text": "상장사\n자금 조달", "fill": "yellow"}], "card_height": 220},
         {"section": "3. 누가 버나", "title": "스페이스X 공모 규모", "source": "자료: 위키피디아·Massive",
          "bignum": {"value": "750", "unit": "억 달러", "caption": "역대 최대 IPO (기본 물량)", "color": "red_num"}}],
        ["공모주 청약, 다들 해 보셨죠?", "그 버튼 뒤에서 누가 돈을 벌까요?", "돈이 흐르는 길을 따라가 볼게요."]),
    6: ("10_버핏투자법", "hook.png", ["버크셔의 다음 주인", "버핏 이후 60년"], {"kicker": "가문의 이야기"},
        [{"section": "1. 등장인물", "title": "버크셔의 세대교체", "theme": "cream", "source": "자료: 버크셔 해서웨이",
          "bullets": ["2025년 5월 3일 — 주총에서 연말 CEO 퇴임 발표", "2026년 1월 1일 — 그레그 에이블 CEO 취임", "버핏은 회장으로 남음"], "build_step": 0.5},
         {"section": "3. 결정적 장면", "title": "60년 성적표", "source": "자료: 버크셔 2025년 주주서한",
          "bignum": {"value": "19.7", "unit": "%", "caption": "1965~2025 연평균 (S&P500 10.5%)", "color": "yellow"}}],
        ["버핏 다음은 누가 이끌까요?", "2026년 1월, 새 CEO가 취임했습니다.", "60년 기록이 남긴 것은 무엇일까요?"]),
    7: ("07_반도체와구글", "hook.png", ["삼성전자", "SK하이닉스"], {"left": "삼성전자", "right": "SK하이닉스", "kicker": "메모리 왕좌의 역전"},
        [{"section": "2. 1라운드", "title": "같은 날, 다른 낙폭", "source": "자료: 한국거래소 종가(2026-03-26)",
          "bars": [{"label": "삼성전자", "value": 4.71, "text": "-4.71%", "color": "blue_num"}, {"label": "SK하이닉스", "value": 6.23, "text": "-6.23%", "color": "red_num", "strong": True}]},
         {"section": "3. 반격", "title": "석 달 뒤 SK하이닉스", "source": "자료: 한국거래소(2026-06-30)",
          "bignum": {"value": "87만 3천", "unit": "원", "caption": "2026년 6월 30일 종가", "color": "red_num"}}],
        ["메모리 왕좌를 두고 붙은 두 회사.", "같은 날 누가 더 크게 흔들렸을까요?", "석 달 뒤 스코어는 달라졌습니다."]),
    8: ("13_연준의장교체", "hook.png", ["다음 주 핵심 변수", "FOMC · 환율 · 대출금리"], {"month": "12월", "day": "8~9"},
        [{"section": "2. 변수 3개", "title": "체크리스트", "theme": "cream", "bullets": ["☐ 12월 8~9일 미국 FOMC", "☐ 원·달러 1,342.7원(11/25)에서 어디로", "☐ 한국 기준금리 3.25% 반영 시점"], "build_step": 0.5},
         {"section": "3. 시나리오", "title": "두 가지 경우", "cards": [{"text": "동결\n→ 환율 안정 쪽"}, {"text": "추가 인상\n→ 대출금리 부담", "fill": "yellow"}], "card_height": 220}],
        ["다음 주 시장, 무엇을 봐야 할까요?", "날짜가 정해진 변수가 세 개 있습니다.", "어느 쪽이든 미리 계산해 둘 수 있어요."]),
    9: ("08_호르무즈와기름값", "hook.png", ["유가가 오르면", "누가 웃고 누가 울까?"], {"kicker": "수혜 · 피해 지도"},
        [{"section": "2. 돈이 움직이는 길", "title": "업종 지도 (2026년 3월 사례)", "source": "자료: CNBC(2026-03) — 업종 예시, 종목 추천 아님",
          "cards": [{"label": "▲ 수혜 쪽", "value": "정유·해운", "color": "red", "caption": "판매가·운임 상승"}, {"label": "▼ 피해 쪽", "value": "항공·화학", "color": "blue", "caption": "연료·원료비 상승"}]},
         {"section": "3. 과거 사례", "title": "2026년 3월 브렌트유", "source": "자료: CNBC — 2월 27일 약 72달러 → 3월 9일",
          "bignum": {"value": "120", "unit": "달러", "caption": "배럴당, 3월 9일 120달러 가까이", "color": "red_num"}}],
        ["유가가 오르면 누가 웃고 누가 울까요?", "업종 지도로 먼저 보겠습니다.", "과거 사례 숫자도 함께요."]),
    10: ("01_아이슬란드", "hook_is.png", ["아이슬란드,", "나라가 파산할 뻔한 날"], {"clock_label": "부채 시계(설명용 예시)", "pin_x": 820, "pin_y": 300},
         [{"section": "2. 빚이 쌓인 길", "title": "지금 아이슬란드 기준금리", "source": "자료: 아이슬란드 중앙은행(2026-11-18 적용)",
           "bignum": {"value": "8.00", "unit": "%", "caption": "다음 결정 2027년 2월 3일", "color": "red_num"}},
          {"section": "4. 지금과 우리", "title": "체크할 숫자", "bullets": ["기준금리 8.00%", "다음 결정 2027-02-03", "2026년 2분기 GDP -1.1%(전년 대비)"], "build_step": 0.4}],
         ["작은 섬나라가 나라째 파산할 뻔했습니다.", "빚은 어떻게 그렇게 커졌을까요?", "지금 숫자로 다시 보겠습니다."]),
}


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def main():
    out_root, img_root = sys.argv[1], sys.argv[2]
    only = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else list(S)
    import build  # noqa: E402
    os.makedirs(out_root, exist_ok=True)
    tiles = []
    for pid in only:
        ep, img, heads, vars_, bodies, subs = S[pid]
        d = os.path.join(out_root, "p%02d" % pid); os.makedirs(d, exist_ok=True)
        ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "10", os.path.join(d, "voice.wav")])
        ts = [(0.2, 3.3), (3.5, 6.7), (6.9, 9.8)]
        with open(os.path.join(d, "voice.srt"), "w", encoding="utf-8") as f:
            for k, ((a, b), t) in enumerate(zip(ts, subs)):
                f.write("%d\n00:00:%s --> 00:00:%s\n%s\n\n" % (k + 1, ("%06.3f" % a).replace(".", ","), ("%06.3f" % b).replace(".", ","), t))
        media = os.path.join(img_root, ep, "assets", img)
        scenes = [{"type": "hook", "media": media, "headline": heads, "start": 0, "section": "오프닝"}]
        for k, b in enumerate(bodies):
            sc = dict(type="slide", start=[3.4, 6.8][k]); sc.update(b); scenes.append(sc)
        proj = {"title": "pattern %d" % pid, "voice": "voice.wav", "srt": "voice.srt", "tighten": False, "output": "sample.mp4", "tail": 0.0, "scenes": scenes}
        os.environ["PATTERN"] = str(pid); os.environ["EP_DIR"] = d
        pat = build.apply_pattern(proj)
        proj["style"]["vars"].update(vars_)
        build.add_sound(d, proj, pat)
        if pat.get("bgm_mode") != "full":
            proj["bgm_mode"] = "full"   # 10초 샘플에서도 BGM 톤이 들리도록
        json.dump(proj, open(os.path.join(d, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        r = subprocess.run([sys.executable, NEOGUL, "render", os.path.join(d, "project.json"), "--out", os.path.join(d, "sample_%02d.mp4" % pid)], capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit("패턴 %d 렌더 실패" % pid)
        v = os.path.join(d, "sample_%02d.mp4" % pid)
        for nm, t in (("a", 2.4), ("b", 5.6)):
            ff(["-ss", str(t), "-i", v, "-frames:v", "1", "-vf", "scale=800:450", os.path.join(d, nm + ".png")])
        p = patterns.PATTERNS[pid]
        label = "%d  %s   |  오프닝 %s · BGM %s · %s분" % (pid, p["name"], p["hook_mode"], p["bgm"].replace("bgm-", ""), p["minutes"])
        lab = label.replace(":", "\\:").replace("'", "")
        ff(["-i", os.path.join(d, "a.png"), "-i", os.path.join(d, "b.png"), "-filter_complex",
            "[0][1]hstack=2,pad=iw+12:ih+70:6:64:color=0x202020,drawtext=fontfile=%s:text='%s':x=18:y=16:fontsize=34:fontcolor=white" % (FONT, lab),
            os.path.join(d, "tile.png")])
        tiles.append(os.path.join(d, "tile.png"))
        print("[sample] 패턴 %d %s 완료" % (pid, p["name"]), flush=True)
    if len(tiles) == 10:
        args = []
        for t in tiles:
            args += ["-i", t]
        ff(args + ["-filter_complex", "xstack=inputs=10:layout=0_0|w0_0|0_h0|w0_h0|0_h0+h1|w0_h0+h1|0_h0+h1+h2|w0_h0+h1+h2|0_h0+h1+h2+h3|w0_h0+h1+h2+h3",
                   os.path.join(out_root, "패턴10_샘플.png")])
        ff(["-i", os.path.join(out_root, "패턴10_샘플.png"), "-q:v", "3", os.path.join(out_root, "패턴10_샘플.jpg")])
        print("[grid]", os.path.join(out_root, "패턴10_샘플.jpg"))


if __name__ == "__main__":
    main()
