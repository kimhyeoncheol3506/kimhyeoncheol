# -*- coding: utf-8 -*-
"""랭킹 영상 대본 빌더 (ranking-video 스킬 v2.0.0)

사용법:
    python3 -I build_script.py <대본데이터.json> <출력폴더>

입력 JSON 형식 (examples/노량진_TOP10.json 참고):
{
  "title": "영상 제목",
  "total_seconds": 1200,          # 전체 러닝타임(초)
  "end_card_seconds": 15,         # 마지막 섹션 내레이션 뒤 엔드카드 여백
  "max_chunk": 100,               # TTS 한 덩어리 최대 글자 수
  "display_map": [["삼천이백십팔 개", "3,218개"], ...],  # TTS 한글숫자 → 자막 표기
  "sections": [
    {"name": "인트로", "start": 0, "end": 60,
     "sentences": [["문장", "연출메모(선택)"], ...]},
    ...
  ]
}
출력: 01_대본/전체대본_한글.txt, 01_대본/대본_캡컷용_분할.txt, 02_자막/자막_srt.srt
"""
import json, os, re, sys

RANK = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5",
        "육": "6", "칠": "7", "팔": "8", "구": "9", "십": "10"}


def mmss(x):
    x = int(round(x)); return f"{x // 60:02d}:{x % 60:02d}"


def srt_t(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main(data_path, out):
    D = json.load(open(data_path, encoding="utf-8"))
    MAX = D.get("max_chunk", 100)
    total_sec = D.get("total_seconds", 1200)
    end_card = D.get("end_card_seconds", 15)
    secs = D["sections"]
    for s in secs:
        s["sentences"] = [(x[0], x[1] if len(x) > 1 else "") for x in s["sentences"]]
    voice_end = {secs[-1]["name"]: secs[-1]["end"] - end_card}

    def disp(t):
        mp = dict(D.get("display_map", []))  # v2.3.0: 긴 표현부터 한 번에 바꿈(순서대로 바꾸면 '이만 원'→'2만 원'→'21만 원'처럼 겹쳐 깨짐)
        if mp: t = re.sub("|".join(re.escape(k) for k in sorted(mp, key=len, reverse=True)), lambda m: mp[m.group(0)], t)
        return re.sub(r"(?<![가-힣])([일이삼사오육칠팔구십])위", lambda m: RANK[m.group(1)] + "위", t)

    # 덩어리 분할 (섹션 경계 유지)
    chunks = []
    for s in secs:
        cur = []
        for t, m in s["sentences"]:
            if len(t) > MAX:
                print(f"[경고] {s['name']}: 한 문장이 {len(t)}자로 {MAX}자를 넘습니다 → {t[:20]}…")
            if cur and len(" ".join(x for x, _ in cur + [(t, m)])) > MAX:
                chunks.append((s["name"], cur)); cur = []
            cur.append((t, m))
        if cur: chunks.append((s["name"], cur))

    # 타임스탬프: 섹션 시간을 글자 수 비례로 배분
    timed = []
    for s in secs:
        cs = [c for c in chunks if c[0] == s["name"]]
        a, e = s["start"], voice_end.get(s["name"], s["end"])
        tot = sum(len(" ".join(t for t, _ in c[1])) for c in cs)
        t0 = a
        for c in cs:
            d = (e - a) * len(" ".join(t for t, _ in c[1])) / tot
            timed.append((s["name"], t0, t0 + d, c[1])); t0 += d

    os.makedirs(f"{out}/01_대본", exist_ok=True); os.makedirs(f"{out}/02_자막", exist_ok=True)

    total = 0; parts = []; report = []
    for s in secs:
        body = " ".join(t for t, _ in s["sentences"]); total += len(body); report.append((s["name"], len(body)))
        parts.append(f"■ {s['name']} [{mmss(s['start'])}~{mmss(s['end'])}]  ({len(body)}자)\n{body}\n")
    with open(f"{out}/01_대본/전체대본_한글.txt", "w", encoding="utf-8") as f:
        f.write(f"{D['title']} — 전체 대본 (내레이션: 캡컷 TTS '애덤')\n")
        f.write(f"총 {total:,}자 (공백 포함) / 러닝타임 {mmss(total_sec)} 기준\n")
        f.write("※ 숫자는 TTS 발음용으로 한글 표기. 자막(SRT)에는 아라비아 숫자로 표기됨.\n\n")
        f.write("\n".join(parts))

    with open(f"{out}/01_대본/대본_캡컷용_분할.txt", "w", encoding="utf-8") as f:
        f.write(f"{D['title']} — 캡컷 '애덤' TTS 분할 대본\n")
        f.write("사용법: 'TTS▶' 줄만 복사 → 캡컷 [텍스트]→[텍스트 음성 변환]→'애덤'. '연출' 줄은 붙여넣지 마세요.\n")
        f.write("권장 속도: 애덤 0.9x (본문 사이 1~2초 B롤 현장음 여백으로 러닝타임 맞춤)\n")
        f.write("표기: 느리게▲ = 0.8x 또는 앞 0.5초 쉼 / 빠르게▼ = 1.0~1.1x / (효과음: OO) = 덩어리 시작점 삽입\n")
        f.write("=" * 60 + "\n")
        last = None
        for i, (name, a, b, items) in enumerate(timed, 1):
            if name != last: f.write(f"\n━━━━ {name} ━━━━\n"); last = name
            txt = " ".join(t for t, _ in items)
            memo = [f"「{t[:12]}…」 {m}" for t, m in items if m]
            f.write(f"\n#{i:03d} [{mmss(a)}] ({len(txt)}자)\n")
            if memo: f.write("연출: " + " / ".join(memo) + "\n")
            f.write(f"TTS▶ {txt}\n")

    def one_line(text, limit=D.get("subtitle_max", 20)):
        """참고 스타일: 자막은 한 줄. 길면 쉼표 → 띄어쓰기 순으로 나눠 여러 큐로"""
        if len(text) <= limit: return [text]
        parts, cur = [], ""
        for seg in re.split(r"(?<=[,.]) ", text):
            if cur and len(cur) + 1 + len(seg) > limit: parts.append(cur); cur = seg
            else: cur = f"{cur} {seg}".strip()
        parts.append(cur)
        res = []
        for p in parts:
            while len(p) > limit + 4:
                cut = p.rfind(" ", 0, limit + 1)
                if cut <= 0: break
                res.append(p[:cut]); p = p[cut + 1:]
            res.append(p)
        return res

    n = 0
    with open(f"{out}/02_자막/자막_srt.srt", "w", encoding="utf-8") as f:
        for name, a, b, items in timed:
            tot = sum(len(t) for t, _ in items); t0 = a
            for t, _ in items:
                d = (b - a) * len(t) / tot
                lines = one_line(disp(t)); lt = sum(len(x) for x in lines)
                for x in lines:
                    dd = d * len(x) / lt
                    n += 1
                    f.write(f"{n}\n{srt_t(t0)} --> {srt_t(t0 + dd - 0.05)}\n{x}\n\n")
                    t0 += dd

    print(f"총 {total:,}자 / 덩어리 {len(timed)}개 / 자막 {n}큐")
    for name, c in report: print(f"  {name}: {c}자")
    lens = [len(" ".join(t for t, _ in c[3])) for c in timed]
    print(f"  덩어리 길이 {min(lens)}~{max(lens)}자")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
