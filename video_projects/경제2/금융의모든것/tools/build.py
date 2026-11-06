#!/usr/bin/env python3
"""금융의 모든 것 — 대본(script/*.txt) → 음성 원고(chunks.json) / 문장 정렬 / 파트별 project.json.

명령:
  python tools/build.py chunks  <작업폴더>            # TTS 원고 묶음 만들기 (tts/chunks.json)
  python tools/build.py align   <작업폴더> [--tempo 1.0]  # tts/chunk_XXX.mp3 → 문장별 wav, 파트별 voice.wav/srt
  python tools/build.py project <작업폴더>            # 파트별 project.json (neogul-edit 형식)
  python tools/build.py say "문장"                     # 숫자 읽기 변환 확인

대본 형식: 한 줄 = 한 문장. '@'로 시작하는 줄은 장면 지시(다음 문장부터 적용).
  @part N / @section 라벨 / @hook pd:키 | 헤드라인1 | 헤드라인2 / @broll pd:키 / @pip pd:키
  @mascot 캡션 / @sub 캡션 / @outro / @toc 제목 | 항목;항목 / @big 제목 | 값 | 단위 | 캡션
  @s {json 슬라이드}  — "at":"L2" 는 장면 안 세 번째 문장이 시작되는 순간(초)으로 바뀜.
  '문장 || 읽기' : 자막은 앞, 음성은 뒤.  '!문장' : 강조 자막(R-T3).
"""
import json, os, re, subprocess, sys, glob, math, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT_DIR = os.path.join(ROOT, "script")

# ------------------------------------------------------------------ 숫자 읽기
DIG = "영일이삼사오육칠팔구"
NATIVE = {1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯", 7: "일곱", 8: "여덟", 9: "아홉", 10: "열",
          20: "스무", 30: "서른", 40: "마흔", 50: "쉰", 60: "예순", 70: "일흔", 80: "여든", 90: "아흔"}
NATIVE_TENS = {10: "열", 20: "스물", 30: "서른", 40: "마흔", 50: "쉰", 60: "예순", 70: "일흔", 80: "여든", 90: "아흔"}
NATIVE_ONES = {1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯", 7: "일곱", 8: "여덟", 9: "아홉"}


def sino4(n):
    s = ""
    for unit, name in ((1000, "천"), (100, "백"), (10, "십"), (1, "")):
        d = n // unit % 10
        if d:
            s += ("" if (d == 1 and name) else DIG[d]) + name
    return s


def sino(n):
    if n == 0:
        return "영"
    parts = []
    for unit, name in ((10 ** 16, "경"), (10 ** 12, "조"), (10 ** 8, "억"), (10 ** 4, "만"), (1, "")):
        g = n // unit % 10000
        if g:
            w = sino4(g)
            if name == "만" and g == 1:
                w = ""
            parts.append(w + name)
    return "".join(parts)


def native(n):
    if n in NATIVE and n < 10:
        return NATIVE[n]
    if n == 20:
        return "스무"
    t, o = n // 10 * 10, n % 10
    if o == 0:
        return NATIVE_TENS[t]
    return NATIVE_TENS[t] + NATIVE_ONES[o]


def read_num(tok):
    tok = tok.replace(",", "")
    if "." in tok:
        a, b = tok.split(".", 1)
        return sino(int(a)) + " 점 " + "".join(DIG[int(c)] for c in b)
    return sino(int(tok))


COUNTERS = r"(명|개(?!월|국)|번째|번(?!호)|살|시간|척|가지|배(?!당|럴|를|에서|와))"
ACRO = {"IMF": "아이엠에프", "CDO": "씨디오", "CDS": "씨디에스", "MBS": "엠비에스", "AAA": "트리플 에이", "FTX": "에프티엑스",
        "DNA": "디엔에이", "GDP": "지디피", "VOC": "브이오씨", "TARP": "타프", "SEC": "에스이씨", "J.P.": "제이피", "PQ": "피큐", "MV": "엠브이"}


def say(text):
    t = text
    t = re.sub(r"^\s*!|\*\*|\[Q\]", "", t)
    t = t.replace("9.11", "구일일")
    for k, v in ACRO.items():
        t = re.sub(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", v, t)
    t = re.sub(r"(\d+)\s*~\s*(\d+)", lambda m: m.group(1) + "에서 " + m.group(2), t)
    t = re.sub(r"(?<!\d)6월", "유월", t)
    t = re.sub(r"(?<!\d)10월", "시월", t)

    def counter(m):
        n = int(m.group(1)); c = m.group(2)
        if c.startswith("배") and n > 10:
            return sino(n) + " " + c
        if n <= 99:
            return native(n) + " " + c
        return sino(n) + " " + c
    t = re.sub(r"(?<![\d.,])(\d{1,2})\s?" + COUNTERS, counter, t)
    t = re.sub(r"-(?=\d)", "마이너스 ", t)
    t = re.sub(r"(\d[\d,]*(?:\.\d+)?)\s*%", lambda m: read_num(m.group(1)) + " 퍼센트", t)
    t = re.sub(r"\d[\d,]*(?:\.\d+)?", lambda m: read_num(m.group(0)), t)
    t = t.replace("  ", " ")
    return t.strip()


# ------------------------------------------------------------------ 대본 파싱
def parse():
    sents, scenes = [], []
    part, section = 1, ""
    pending = []
    for f in sorted(glob.glob(os.path.join(SCRIPT_DIR, "*.txt"))):
        for raw in open(f, encoding="utf-8"):
            ln = raw.rstrip("\n").strip()
            if not ln or ln.startswith("#"):
                continue
            if ln.startswith("@"):
                cmd, _, arg = ln[1:].partition(" ")
                if cmd == "part":
                    part = int(arg)
                elif cmd == "section":
                    section = arg.strip()
                else:
                    pending.append((cmd, arg.strip(), section, part))
                continue
            disp, _, spk = ln.partition(" || ")
            disp = disp.strip(); spk = (spk or disp).strip()
            sid = len(sents)
            for p in pending:
                scenes.append({"cmd": p[0], "arg": p[1], "section": p[2], "part": p[3], "sid": sid})
            pending = []
            sents.append({"id": sid, "disp": disp, "say": say(spk), "part": part, "file": os.path.basename(f)})
    return sents, scenes


# ------------------------------------------------------------------ TTS 묶음
def cmd_chunks(work, maxc=1400):
    sents, scenes = parse()
    starts = {s["sid"] for s in scenes}
    chunks, cur = [], []
    for s in sents:
        clen = sum(len(x["say"]) + 1 for x in cur)
        newpart = cur and cur[-1]["part"] != s["part"]
        if cur and (newpart or (clen + len(s["say"]) > maxc and s["id"] in starts) or clen > maxc + 400):
            chunks.append(cur); cur = []
        cur.append(s)
    if cur:
        chunks.append(cur)
    out = [{"i": i, "part": c[0]["part"], "sids": [x["id"] for x in c], "text": " ".join(x["say"] for x in c)} for i, c in enumerate(chunks)]
    os.makedirs(os.path.join(work, "tts"), exist_ok=True)
    json.dump(out, open(os.path.join(work, "tts", "chunks.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sents, open(os.path.join(work, "tts", "sentences.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot = sum(len(c["text"]) for c in out)
    print("문장 %d개, 장면 %d개, 묶음 %d개, 총 %d자" % (len(sents), len(scenes), len(out), tot))
    for c in out:
        print("  chunk %02d part%d  %4d자  문장 %d~%d" % (c["i"], c["part"], len(c["text"]), c["sids"][0], c["sids"][-1]))


# ------------------------------------------------------------------ 정렬
def ffrun(args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y"] + args, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return r.stderr


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())


def silences(wav, db=-40, d=0.18):
    err = ffrun(["-i", wav, "-af", "silencedetect=n=%ddB:d=%.2f" % (db, d), "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))


def align_chunk(wav, texts):
    """문장 경계를 무음 구간에 맞춘다(동적계획법). returns [(t0,t1)] 문장별 소리 구간."""
    D = dur(wav)
    sil = [s for s in silences(wav) if s[1] - s[0] >= 0.18]
    lead = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    tail = sil[-1][0] if sil and sil[-1][1] > D - 0.05 else D
    inner = [s for s in sil if s[0] > lead + 0.05 and s[1] < tail - 0.05]
    n = len(texts)
    if n == 1:
        return [(lead, tail)], []
    w = [max(1, len(re.sub(r"\s", "", t))) for t in texts]
    tot = sum(w); speech = tail - lead
    exp = []; acc = 0
    for k in range(n - 1):
        acc += w[k]; exp.append(lead + speech * acc / tot)
    m = len(inner)
    if m < n - 1:
        raise ValueError("무음 구간(%d)이 문장 경계(%d)보다 적음" % (m, n - 1))
    INF = 1e18
    # cost: 시간 차이(초)^2 - 무음 길이 보너스
    def cost(k, j):
        mid = (inner[j][0] + inner[j][1]) / 2
        return ((mid - exp[k]) / max(1.0, speech * 0.04)) ** 2 - 6.0 * min(0.9, inner[j][1] - inner[j][0])
    dp = [[INF] * m for _ in range(n - 1)]; bk = [[-1] * m for _ in range(n - 1)]
    for j in range(m):
        dp[0][j] = cost(0, j)
    for k in range(1, n - 1):
        best, bj = INF, -1
        for j in range(m):
            if j - 1 >= 0 and dp[k - 1][j - 1] < best:
                best, bj = dp[k - 1][j - 1], j - 1
            if best < INF:
                dp[k][j] = best + cost(k, j); bk[k][j] = bj
    j = min(range(m), key=lambda x: dp[n - 2][x]); picks = [j]
    for k in range(n - 2, 0, -1):
        j = bk[k][j]; picks.append(j)
    picks.reverse()
    segs = []; t0 = lead
    for j in picks:
        segs.append((t0, inner[j][0])); t0 = inner[j][1]
    segs.append((t0, tail))
    used = set(picks)
    pauses = [inner[j] for j in range(m) if j not in used]
    return segs, pauses


def cut_sentence(wav, t0, t1, pauses, out, tempo):
    """문장 구간을 잘라 내고, 문장 안의 0.4초 넘는 쉼은 0.25초로 줄인다(R-A1)."""
    keep = []; cur = t0
    for a, b in pauses:
        if a >= t0 and b <= t1 and b - a > 0.4:
            keep.append((cur, a + 0.125)); cur = b - 0.125
    keep.append((cur, t1))
    fl = []
    for i, (a, b) in enumerate(keep):
        fl.append("[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS[p%d]" % (max(0, a - 0.02), b + 0.04, i))
    fl.append("".join("[p%d]" % i for i in range(len(keep))) + "concat=n=%d:v=0:a=1[c]" % len(keep))
    tail = ",atempo=%.3f" % tempo if abs(tempo - 1) > 1e-3 else ""
    fl.append("[c]afade=t=in:d=0.015,areverse,afade=t=in:d=0.03,areverse%s,highpass=f=70,equalizer=f=220:t=q:w=1.2:g=1.5,equalizer=f=3200:t=q:w=1.5:g=1.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2[o]" % tail)
    ffrun(["-i", wav, "-filter_complex", ";".join(fl), "-map", "[o]", "-ar", "48000", "-ac", "1", out])


def cmd_align(work, tempo=1.0, only_parts=None):
    """tts/fix/sXXXX.(wav|mp3) 문장별 음성 → 다듬기(R-A1 쉼 압축) → 파트별 voice.wav/srt."""
    sents = json.load(open(os.path.join(work, "tts", "sentences.json"), encoding="utf-8"))
    sd = os.path.join(work, "tts", "sent"); os.makedirs(sd, exist_ok=True)
    fix = os.path.join(work, "tts", "fix")
    report = []
    for s in sents:
        sid = s["id"]
        if only_parts and s["part"] not in only_parts:
            continue
        src = next((os.path.join(fix, "s%04d.%s" % (sid, e)) for e in ("wav", "mp3") if os.path.exists(os.path.join(fix, "s%04d.%s" % (sid, e)))), None)
        if not src:
            raise SystemExit("음성 없음: 문장 %d" % sid)
        out = os.path.join(sd, "s%04d.wav" % sid)
        if not (os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src)):
            D = dur(src); sl = silences(src, -42, 0.12)
            lead = sl[0][1] if sl and sl[0][0] < 0.05 else 0.0
            tail = sl[-1][0] if sl and sl[-1][1] > D - 0.05 else D
            cut_sentence(src, lead, tail, sl, out, tempo)
        report.append({"sid": sid, "dur": round(dur(out), 2), "chars": len(s["say"])})
        if sid % 100 == 0:
            print("  다듬기 %d/%d" % (sid, len(sents)), flush=True)
    json.dump(report, open(os.path.join(work, "tts", "align_report.json"), "w"), indent=0)
    # 파트별 voice.wav / voice.srt (문장 사이 쉼: 문장 끝 부호에 따라 0.28~0.45초, 약간의 흔들림)
    random.seed(7)
    parts = sorted({s["part"] for s in sents})
    for p in parts:
        if only_parts and p not in only_parts:
            continue
        pd_ = os.path.join(work, "part%d" % p); os.makedirs(pd_, exist_ok=True)
        ids = [s["id"] for s in sents if s["part"] == p]
        lst = os.path.join(pd_, "voice_list.txt"); t = 0.0; subs = []
        gaps = {}
        with open(lst, "w") as f:
            for k, sid in enumerate(ids):
                w = os.path.join(sd, "s%04d.wav" % sid)
                d = dur(w)
                subs.append((t, t + d, sents[sid]["disp"]))
                t += d
                f.write("file '%s'\n" % w)
                if k < len(ids) - 1:
                    end = sents[sid]["disp"].rstrip()[-1:]
                    g = (0.42 if end in "?!" else 0.34 if end in ".다요죠" else 0.26) + random.uniform(-0.04, 0.05)
                    g = round(g / tempo, 3)
                    gp = os.path.join(work, "tts", "gap_%d.wav" % int(g * 1000))
                    if not os.path.exists(gp):
                        ffrun(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(g), gp])
                    f.write("file '%s'\n" % gp); t += g
        ffrun(["-f", "concat", "-safe", "0", "-i", lst, "-ar", "48000", "-ac", "1", os.path.join(pd_, "voice.wav")])
        with open(os.path.join(pd_, "voice.srt"), "w", encoding="utf-8") as f:
            for i, (a, b, x) in enumerate(subs):
                f.write("%d\n%s --> %s\n%s\n\n" % (i + 1, srt_t(a), srt_t(b), x))
        json.dump({"ids": ids, "starts": [s[0] for s in subs]}, open(os.path.join(pd_, "timing.json"), "w"))
        print("[part%d] 문장 %d개, %.1f분" % (p, len(ids), t / 60))


def srt_t(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


# ------------------------------------------------------------------ project.json
def resolve_media(arg):
    a = arg.strip()
    if a.startswith("pd:"):
        return "../assets/pd/%s.jpg" % a[3:]
    return a


def scene_from(sc, sents, timing, scene_end_sid):
    cmd, arg = sc["cmd"], sc["arg"]
    sec = sc["section"]
    if cmd == "hook":
        p = [x.strip() for x in arg.split("|")]
        return {"type": "hook", "media": resolve_media(p[0]).replace("/pd/", "/pd16/"), "headline": p[1:]}
    if cmd == "broll":
        return {"type": "broll", "media": resolve_media(arg).replace("/pd/", "/pd16/")}
    if cmd == "pip":
        return {"type": "pip", "media": resolve_media(arg).replace("/pd/", "/pipv/").replace(".jpg", ".mp4")}
    if cmd == "mascot":
        return {"type": "mascot", "media": "../assets/mascot/mascot_shock.png", "caption": arg, "at": 0.3}
    if cmd == "sub":
        return {"type": "subscribe", "media": "../assets/mascot/mascot_plead.png", "channel": "경제2", "caption": arg or "도와주세요..제발", "click_at": 1.2}
    if cmd == "outro":
        return {"type": "outro", "media": "../assets/mascot/mascot_thumb.png"}
    if cmd == "toc":
        title, _, items = arg.partition("|")
        cards = [{"text": x.strip().replace(" ", "\n", 1) if len(x.strip()) > 7 else x.strip(), "size": 40} for x in items.split(";") if x.strip()]
        rows = [cards[:3], cards[3:]] if len(cards) > 4 else [cards]
        cards[-1]["fill"] = "yellow"
        return {"type": "slide", "section": sec, "theme": "cream", "title": "오늘 영상에서 다룰 순서", "subtitle": title.strip(),
                "bullets": [{"text": "%d. %s" % (i + 1, c["text"].replace("\n", " "))} for i, c in enumerate(cards)], "build_step": 0.9}
    if cmd == "big":
        p = [x.strip() for x in arg.split("|")] + ["", "", "", ""]
        return {"type": "slide", "section": sec, "title": p[0], "bignum": {"value": p[1], "unit": p[2], "caption": p[3], "color": "yellow"}}
    if cmd == "s":
        d = json.loads(arg)
        d.setdefault("type", "slide"); d.setdefault("section", sec)
        d.pop("news", None)
        if d.get("image") and not d["image"].startswith(".."):
            d["image"] = "../assets/" + d["image"]
        return d
    raise ValueError("알 수 없는 장면: @" + cmd)


def fix_at(obj, base_t, line_ts, dur_):
    """'L2' / 'L2+0.5' → 장면 시작 기준 초."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k in ("at", "arrow_at", "underline_at") and isinstance(v, str) and v.startswith("L"):
                m = re.match(r"L(\d+)([+-][\d.]+)?", v)
                i = min(int(m.group(1)), len(line_ts) - 1)
                t = line_ts[i] - base_t + 0.25 + float(m.group(2) or 0)
                obj[k] = round(max(0.2, min(t, dur_ - 0.4)), 2)
            else:
                fix_at(v, base_t, line_ts, dur_)
    elif isinstance(obj, list):
        for v in obj:
            fix_at(v, base_t, line_ts, dur_)


def cmd_project(work, only_parts=None):
    sents, scenes = parse()
    parts = sorted({s["part"] for s in sents})
    for p in parts:
        if only_parts and p not in only_parts:
            continue
        pd_ = os.path.join(work, "part%d" % p)
        tm = json.load(open(os.path.join(pd_, "timing.json")))
        ids, starts = tm["ids"], tm["starts"]
        pos = {sid: i for i, sid in enumerate(ids)}
        total = starts[-1] + 5
        psc = [s for s in scenes if s["part"] == p]
        out = []
        for k, sc in enumerate(psc):
            d = scene_from(sc, sents, tm, None)
            d.setdefault("section", sc["section"])
            li = pos[sc["sid"]]
            nxt = pos[psc[k + 1]["sid"]] if k + 1 < len(psc) else len(ids)
            # 같은 문장에서 시작하는 연속 장면(@pip 뒤 @s 등)은 간격을 둔다
            same = [x for x in psc if x["sid"] == sc["sid"]]
            if len(same) > 1:
                order = same.index(sc)
                t0 = starts[li]
                t1 = starts[li + 1] if li + 1 < len(starts) else total
                d["start"] = round(t0 + (t1 - t0) * order / len(same), 3) if order else (0 if li == 0 else t0)
            else:
                d["start"] = 0 if li == 0 else starts[li]
            line_ts = starts[li:max(nxt, li + 1)]
            end_t = starts[nxt] if nxt < len(starts) else total
            fix_at(d, d["start"], line_ts, end_t - d["start"])
            out.append(d)
        if out and out[0]["type"] not in ("hook",):
            out[0]["start"] = 0
        proj = {"title": "금융의 모든 것 part%d" % p, "voice": "voice.wav", "srt": "voice.srt", "tighten": False,
                "output": "part%d.mp4" % p, "tail": 0.8, "scenes": out}
        json.dump(proj, open(os.path.join(pd_, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[part%d] 장면 %d개 -> project.json" % (p, len(out)))


def _parts():
    if "--parts" in sys.argv:
        return {int(x) for x in sys.argv[sys.argv.index("--parts") + 1].split(",")}
    return None


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "say":
        print(say(sys.argv[2]))
    elif c == "chunks":
        cmd_chunks(sys.argv[2])
    elif c == "align":
        tempo = float(sys.argv[sys.argv.index("--tempo") + 1]) if "--tempo" in sys.argv else 1.0
        cmd_align(sys.argv[2], tempo, _parts())
    elif c == "project":
        cmd_project(sys.argv[2], _parts())
