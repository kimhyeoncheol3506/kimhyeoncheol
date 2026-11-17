"""layout: whiteboard (2026-11-17 미팅 일꾼, '클로드 미팅·시트·화이트보드 사용법' 썸네일)
따뜻한 호박색 바탕 + 살짝 기운 흰 화이트보드(은색 틀, 마커 받침) 위에 검정 마커 글씨 제목(둘째 줄 형광펜 밑줄, [[주황 강조]])
+ 오른쪽에 붙인 포스트잇 3장(손그림 기호: 화상회의·표·포스트잇) + 화이트보드 위 모서리에 '화상회의 칸' 하나(얼굴 대신 빛나는 점 = AI 참가자).
실제 로고·인물 없음, 그림 생성 없음(크레딧 0).
기존 모양(default·tiles·versus·badge·phone·calendar·film·ticket·orbit·shield·board·oa_viewfinder·donut·podium·omr)과 겹치지 않게: 화이트보드 + 포스트잇 + 호박색.
대본:
  thumbnail:
    layout: whiteboard
    badge: "작은 꼬리표"            # 마커 받침 위 꼬리표
    line1: "첫 줄"
    line2: "[[강조]] 둘째 줄"        # 형광펜 밑줄
    line3: "셋째 줄(작게)"
    notes: [{icon: call, text: "미팅"}, {icon: grid, text: "시트"}, {icon: board, text: "화이트보드"}]
    tile: "AI 참가자"               # 선택(화상회의 칸 이름표)
    stamp: "베타"                   # 선택(둥근 도장)
    color: "#FFB020"                # 선택(바탕 호박) · color2: "#FF6A1A"(주황 강조)
"""
import html as _h
import re

ICONS = {
    "call": '<svg viewBox="0 0 100 100"><rect x="8" y="26" width="58" height="48" rx="10" fill="none" stroke="#1A1410" stroke-width="9"/>'
            '<path d="M66 44 L92 30 L92 70 L66 56 Z" fill="#1A1410"/><circle cx="37" cy="50" r="8" fill="#1A1410"/></svg>',
    "grid": '<svg viewBox="0 0 100 100"><rect x="10" y="14" width="80" height="72" rx="8" fill="none" stroke="#1A1410" stroke-width="9"/>'
            '<path d="M10 38 H90 M10 62 H90 M38 14 V86" stroke="#1A1410" stroke-width="7"/></svg>',
    "board": '<svg viewBox="0 0 100 100"><rect x="12" y="12" width="34" height="34" rx="4" fill="#1A1410"/><rect x="54" y="12" width="34" height="34" rx="4" fill="none" stroke="#1A1410" stroke-width="8"/>'
             '<rect x="12" y="54" width="34" height="34" rx="4" fill="none" stroke="#1A1410" stroke-width="8"/><path d="M58 70 L84 70 M74 60 L84 70 L74 80" stroke="#1A1410" stroke-width="8" fill="none" stroke-linecap="round"/></svg>',
    "note": '<svg viewBox="0 0 100 100"><path d="M14 10 H86 V64 L64 90 H14 Z" fill="none" stroke="#1A1410" stroke-width="9" stroke-linejoin="round"/>'
            '<path d="M28 34 H72 M28 52 H60" stroke="#1A1410" stroke-width="8" stroke-linecap="round"/></svg>',
}
NOTE_COLORS = ["#FFE066", "#FFC48A", "#FFF3D6"]


def _mk(s, acc):
    s = _h.escape(s or "")
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{acc}">\1</span>', s)


def page(t, fonts_uri, W, H):
    esc = _h.escape
    bg = t.get("color", "#FFB020")
    acc = t.get("color2", "#FF6A1A")
    notes = (t.get("notes") or [{"icon": "call", "text": "미팅"}, {"icon": "grid", "text": "시트"}, {"icon": "board", "text": "보드"}])[:3]
    rot = [-6, 4, -3]
    nhtml = []
    for i, n in enumerate(notes):
        svg = ICONS.get(n.get("icon", "note"), ICONS["note"])
        nhtml.append(
            f'<div class="nt" style="top:{170 + i * 270}px;left:{1490 + (i % 2) * 70}px;background:{NOTE_COLORS[i % 3]};transform:rotate({rot[i]}deg)">'
            f'<i class="pin"></i><div class="ni">{svg}</div><b>{esc(n.get("text", ""))}</b></div>')
    stamp = t.get("stamp", "")
    st = (f'<div id="st"><b>{esc(stamp)}</b></div>' if stamp else "")
    tile = t.get("tile", "AI 참가자")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:{bg}}}
#bg{{position:absolute;inset:0;background:radial-gradient(circle at 30% 40%,rgba(255,255,255,.35),transparent 55%),
  repeating-radial-gradient(circle at 0 0,rgba(0,0,0,.05) 0 2px,transparent 2px 26px)}}
#wb{{position:absolute;left:60px;top:64px;width:1400px;height:880px;background:linear-gradient(160deg,#FFFFFF,#F4F1EC);
  border:18px solid #C9CCD1;border-radius:18px;box-shadow:0 0 0 6px #8E9399,22px 26px 0 rgba(60,30,0,.35);transform:rotate(-1.2deg)}}
#wb:after{{content:'';position:absolute;left:30px;right:30px;top:20px;height:120px;background:linear-gradient(180deg,rgba(255,255,255,.9),transparent);border-radius:10px}}
#tray{{position:absolute;left:180px;top:930px;width:1180px;height:34px;background:#9AA0A6;border-radius:6px;box-shadow:0 10px 0 rgba(60,30,0,.3);transform:rotate(-1.2deg)}}
.mk{{position:absolute;top:-22px;width:150px;height:30px;border-radius:15px}}
#k{{position:absolute;left:110px;top:986px;font-size:46px;color:#fff;background:#1A1410;padding:6px 28px 12px;border-radius:999px;letter-spacing:-1px;transform:rotate(-1.2deg)}}
.ln{{position:absolute;left:130px;white-space:nowrap;color:#1A1410;transform:rotate(-1.2deg);transform-origin:left center}}
#t1{{top:150px;font-size:{t.get('size1', 168)}px;letter-spacing:-7px;line-height:1}}
#t2{{top:{t.get('top2', 360)}px;font-size:{t.get('size2', 186)}px;letter-spacing:-8px;line-height:1}}
#t2:before{{content:'';position:absolute;left:-14px;right:-18px;bottom:6px;height:62px;background:rgba(255,214,0,.75);border-radius:8px;z-index:-1;transform:skewX(-8deg)}}
#t3{{top:{t.get('top3', 610)}px;font-size:{t.get('size3', 104)}px;letter-spacing:-4px;color:#3A2E24}}
#tile{{position:absolute;left:1060px;top:640px;width:330px;height:220px;background:#1A1410;border-radius:22px;border:6px solid #1A1410;
  box-shadow:0 0 0 6px {acc};transform:rotate(-1.2deg);overflow:hidden}}
#tile .dot{{position:absolute;left:115px;top:38px;width:100px;height:100px;border-radius:50%;
  background:radial-gradient(circle,#FFF6D8 0 22%,{bg} 40%,{acc} 62%,transparent 64%);box-shadow:0 0 60px {bg}}}
#tile .nm{{position:absolute;left:14px;bottom:12px;font-size:30px;color:#fff;background:rgba(255,255,255,.14);padding:2px 14px 6px;border-radius:10px}}
#tile .rec{{position:absolute;right:16px;top:14px;width:22px;height:22px;border-radius:50%;background:#FF3B30;box-shadow:0 0 14px #FF3B30}}
.nt{{position:absolute;width:330px;height:240px;box-shadow:10px 14px 0 rgba(60,30,0,.35);border-radius:4px 4px 4px 28px}}
.nt .pin{{position:absolute;left:150px;top:-12px;width:30px;height:30px;border-radius:50%;background:{acc};border:4px solid #1A1410}}
.nt .ni{{position:absolute;left:26px;top:44px;width:120px;height:120px}}
.nt b{{position:absolute;left:160px;right:14px;top:70px;font-size:58px;line-height:1.05;color:#1A1410;letter-spacing:-3px;word-break:keep-all}}
#st{{position:absolute;left:1700px;top:40px;width:180px;height:180px;border-radius:50%;background:{acc};border:8px solid #1A1410;
  display:flex;align-items:center;justify-content:center;transform:rotate(14deg);box-shadow:8px 10px 0 rgba(60,30,0,.35)}}
#st b{{font-size:64px;color:#fff;letter-spacing:-3px}}
</style></head><body><div id="bg"></div>
<div id="wb"></div>
<div id="tray"><i class="mk" style="left:120px;background:#1A1410"></i><i class="mk" style="left:320px;background:{acc}"></i></div>
<div class="ln" id="t1">{_mk(t.get('line1', ''), acc)}</div>
<div class="ln" id="t2">{_mk(t.get('line2', ''), acc)}</div>
<div class="ln" id="t3">{_mk(t.get('line3', ''), acc)}</div>
<div id="tile"><i class="dot"></i><i class="rec"></i><div class="nm">{esc(tile)}</div></div>
{''.join(nhtml)}
{st}
<div id="k">{esc(t.get('badge', ''))}</div>
<script>for(const id of ['t1','t2','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);
const lim=id==='t3'?1020:1400;while(e.getBoundingClientRect().right>lim&&f>60){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
