"""34편 연말정산 썸네일 후보 3개 (현철님 참고 썸네일 6장: 초록 배너 '연말정산' 큰 글씨, 흰·노랑 글자 검정 외곽, 큰 금액, 13월의 월급 vs 세금 폭탄 대비).
실존 인물 얼굴 대신 개미 마스코트 + 원천징수영수증·카드 실물 소품. 렌더는 33편 make_thumb_v2.render 재사용(/home/user/hf/thumb)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "20261106-econ2h"))
import make_thumb_v2 as M  # noqa: E402

T = M.T
STK = "drop-shadow(7px 0 0 #fff) drop-shadow(-7px 0 0 #fff) drop-shadow(0 7px 0 #fff) drop-shadow(0 -7px 0 #fff) drop-shadow(0 18px 24px rgba(0,0,0,.3))"


def ant(name, right, bottom, w, rot=0, flip=False):
    tf = f"rotate({rot}deg)" + (" scaleX(-1)" if flip else "")
    return (f'<div class="abs" style="right:{right}px;bottom:{bottom}px;width:{w}px;height:{int(w * 1.25)}px;transform:{tf}">'
            f'<img src="assets/mascot/{name}.png" style="width:100%;height:100%;object-fit:contain;filter:{STK}"></div>')


def receipt(x, y, w, rot, line, amount, col):
    """근로소득 원천징수영수증 모양 종이 (실물 증거 소품)"""
    rows = "".join(f'<div style="height:16px;margin:16px 0;border-radius:8px;background:#D9D4C7;width:{p}%"></div>' for p in (90, 70, 84, 60))
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;padding:34px 38px 40px;background:#FFFEF8;border-radius:10px;transform:rotate({rot}deg);'
            f'box-shadow:0 22px 40px rgba(0,0,0,.35);font-family:PB">'
            f'<div style="font-size:34px;color:#333;border-bottom:4px solid #333;padding-bottom:12px">근로소득 원천징수영수증</div>{rows}'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;font-size:36px;color:#333">{line}'
            f'<span style="font-family:BH;font-size:70px;color:{col}">{amount}</span></div></div>')


def card(x, y, w, rot, kind, label):
    """신용·체크카드 소품 (누끼 스티커처럼 흰 윤곽 + 그림자)"""
    bg = "linear-gradient(135deg,#2B2F3A,#11131A)" if kind == "credit" else "linear-gradient(135deg,#3FB57A,#1E7A4E)"
    h = int(w * 0.63)
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:{w // 14}px;background:{bg};transform:rotate({rot}deg);'
            f'border:8px solid #fff;box-shadow:0 22px 34px rgba(0,0,0,.45);font-family:BH;color:#fff">'
            f'<div style="position:absolute;left:{w // 11}px;top:{h // 3}px;width:{w // 6}px;height:{w // 8}px;border-radius:10px;background:linear-gradient(135deg,#F5D27A,#C89B3C)"></div>'
            f'<div style="position:absolute;left:{w // 11}px;top:{h // 9}px;font-size:{w // 9}px">{"신용카드" if kind == "credit" else "체크카드"}</div>'
            f'<div style="position:absolute;right:{w // 12}px;bottom:{h // 10}px;font-size:{w // 4}px;line-height:1;color:{"#9BB0FF" if kind == "credit" else "#FFE14D"}">{label}</div></div>')


def sticker_box(x, y, text, bg, col, size, rot=0):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;padding:8px 30px 14px;background:{bg};color:{col};font-family:BH;font-size:{size}px;line-height:1.1;'
            f'transform:rotate({rot}deg);border:6px solid #fff;box-shadow:0 12px 0 rgba(0,0,0,.35);white-space:nowrap">{text}</div>')


def design(v):
    """2026-11-11 현철님 지정 썸네일 원칙(비디클래스 '썸네일의 모든 것') 적용판:
    제목과 다른 각도의 문구 · 윗줄/아랫줄 무게 차이 · 오른쪽 아래(재생시간 자리) 비우기 · 누끼 콜라주(흰 윤곽+그림자) · 첫 10초와 일치"""
    if v == "D":  # 콜라주: 영수증 + 카드 2장 + 충격 개미, 왼쪽 위 2줄
        bg = "radial-gradient(circle at 75% 35%,#1F5A73 0%,#0B1E2B 75%)"
        body = ('<div class="abs" style="inset:0;background:radial-gradient(#ffffff10 3px,transparent 3px);background-size:40px 40px"></div>'
                + receipt(1060, 40, 700, 6, "추가 납부", "117만 원", "#E02A2A")
                + card(1000, 470, 470, -12, "credit", "15%")
                + card(1380, 520, 440, 9, "check", "30%")
                + sticker_box(60, 70, "377만 명이 더 냈다", "#E02A2A", "#fff", 92, -2)
                + T("연말정산", 50, 230, 300)
                + T('<span style="color:#FFE14D">세금 폭탄</span>', 50, 540, 260)
                + ant("충격", 820, -70, 340, 4)
                + T('카드 하나로 <span style="color:#FFE14D">갈린다</span>', 60, 850, 100))
    elif v == "E":  # 2분할 VS: 신용 15% vs 체크 30%, 위쪽 질문
        bg = "linear-gradient(90deg,#2A3FB8 0 50%,#16A05D 50% 100%)"
        body = ('<div class="abs" style="left:957px;top:0;width:6px;height:1080px;background:#fff"></div>'
                + card(150, 420, 640, -6, "credit", "15%")
                + card(1110, 420, 640, 6, "check", "30%")
                + '<div class="abs" style="left:860px;top:520px;width:200px;height:200px;border-radius:50%;background:#FFE14D;border:10px solid #111;font-family:BH;font-size:110px;color:#111;display:flex;align-items:center;justify-content:center;transform:rotate(-8deg)">VS</div>'
                + '<div class="abs" style="left:0;right:0;top:0;height:330px;background:rgba(0,0,0,.78)"></div>'
                + T('연말정산 카드', 0, 30, 120, align="center")
                + T('<span style="color:#FFE14D">언제</span> 바꿔야 할까?', 0, 160, 150, align="center")
                + ant("아이디어", 40, 520, 300, 4))
    else:  # F 중앙 큰 숫자 + 개미가 숫자를 가림
        bg = "radial-gradient(circle at 50% 55%,#FFF6D6 0%,#FFD84D 70%)"
        body = ('<div class="abs" style="inset:0;background:repeating-conic-gradient(from 0deg at 50% 60%,#ffffff40 0 6deg,transparent 6deg 18deg)"></div>'
                + T('연말정산 추가 납부 <span style="color:#FFE14D">1인당 평균</span>', 0, 60, 96, align="center")
                + '<div class="abs" style="left:0;right:0;top:260px;text-align:center;font-family:BH;font-size:380px;line-height:1;color:#E02A2A;letter-spacing:-10px;'
                  '-webkit-text-stroke:14px #111;paint-order:stroke fill;filter:drop-shadow(0 16px 0 #111)">117만 원</div>'
                + ant("충격", 1500, -60, 420, -6)
                + sticker_box(1380, 150, "역대 최대", "#111", "#FFE14D", 80, 10)
                + T('<span style="color:#fff">나는 피할 수 있을까?</span>', 470, 800, 120))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumbs")
    os.makedirs(out, exist_ok=True)
    for v in (sys.argv[1:] or ["D", "E", "F"]):
        print(M.render(v, os.path.join(out, f"thumbnail_{v}.png")))
