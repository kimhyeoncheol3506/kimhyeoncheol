# -*- coding: utf-8 -*-
"""랭킹 영상 자동 렌더러 (ranking-video 스킬 v2.1.0)

대본데이터.json + 문장별 TTS mp3 + 이미지 + 07_그래픽 PNG → 완성 MP4 (1920×1080, 30fps, H.264)

사용법:
    python3 -I render_video.py <대본데이터.json> <작업폴더> --tts <tts폴더> --img <이미지폴더> --sfx <효과음폴더> [--work <임시폴더>] [--jobs 4] [--until 초] [--bgm 파일명]
  --until: 앞부분만 샘플로 렌더링(예: 175) → 08_완성영상/샘플.mp4
  완성본은 1080p 원본과 함께 30MB 이하 720p 전달본(<제목>_완성본_720p.mp4)을 자동으로 만든다(파일 전송 한도 30MB).

- tts 폴더: {섹션번호:02d}_{문장번호:02d}.mp3 (make_tts.py 결과)
- 이미지 폴더: meta.json([{id, section, ...}]) + {id}.jpg, 제외할 id는 exclude.txt에 한 줄씩
- 효과음 폴더: 칼 소리.wav, 물방울.wav, 쿠궁.wav, 코인.wav, 갈매기.wav, bgm_loop.wav
출력: <작업폴더>/08_완성영상/완성영상.mp4, 자막_실제타이밍.srt, 타임라인.json
"""
import argparse, concurrent.futures as cf, json, os, random, re, subprocess, wave
import numpy as np

SR = 48000
W, H, FPS = 1920, 1080, 30
GAP, GAP_SLOW, CARD, TITLE, TITLE_FIRST, BEAT, TAIL, END = 0.25, 0.15, 2.0, 3.0, 3.5, 2.0, 0.5, 4.0  # v1.3.0: 빠른 템포
RANK = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5", "육": "6", "칠": "7", "팔": "8", "구": "9", "십": "10"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(" ".join(cmd[:6]) + "\n" + r.stderr[-1500:])


def load_audio(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim(x, th=0.012, margin=0.04):
    env = np.convolve(np.abs(x), np.ones(240) / 240, "same")
    idx = np.where(env > th)[0]
    if not len(idx): return x
    a, b = max(0, idx[0] - int(margin * SR)), min(len(x), idx[-1] + int(margin * 2 * SR))
    return x[a:b]


def disp_fn(D):
    def disp(t):
        mp = dict(D.get("display_map", []))  # v2.3.0: 긴 표현부터 한 번에 바꿈(순서대로 바꾸면 '이만 원'→'2만 원'→'21만 원'처럼 겹쳐 깨짐)
        if mp: t = re.sub("|".join(re.escape(k) for k in sorted(mp, key=len, reverse=True)), lambda m: mp[m.group(0)], t)
        return re.sub(r"(?<![가-힣])([일이삼사오육칠팔구십])위", lambda m: RANK[m.group(1)] + "위", t)
    return disp


def one_line(text, limit=20):
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


def voice_split(audio, lens, dur):
    """한 문장의 자막 줄들이 바뀌는 시각을 실제 목소리에 맞춘다: 말소리가 있는 구간의 누적량이 글자 수 비율에 닿는 곳, 그 뒤 쉼의 가운데."""
    n = len(lens); tot = float(sum(lens))
    if n == 1: return [dur]
    prop = [dur * l / tot for l in lens]
    try:
        hop = int(SR * 0.02); m = len(audio) // hop
        if m < 10: return prop
        e = np.sqrt(np.mean(np.asarray(audio[:m * hop], np.float64).reshape(m, hop) ** 2, axis=1))
        voiced = e > 0.08 * np.percentile(e, 95); cum = np.cumsum(voiced)
        if cum[-1] < 8: return prop
        bounds = [0.0]; c = 0
        for l in lens[:-1]:
            c += l; target = cum[-1] * c / tot; i = int(np.searchsorted(cum, target)); j = i + 1
            while j < m and not voiced[j]: j += 1
            bounds.append(min(dur, (i + min(j, m)) / 2 * 0.02))
        bounds.append(dur)
        out = [bounds[k + 1] - bounds[k] for k in range(n)]
        return out if all(d_ > 0.25 for d_ in out) and abs(sum(out) - dur) < 1e-6 else prop
    except Exception:
        return prop


def ass_time(t):
    cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("proj")
    ap.add_argument("--tts", required=True); ap.add_argument("--img", required=True); ap.add_argument("--sfx", required=True)
    ap.add_argument("--work", default=None); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--until", type=float, default=None); ap.add_argument("--bgm", default="bgm_upbeat_loop.wav")
    ap.add_argument("--lufs", type=float, default=-16.0, help="통합 음량 목표(LUFS), 0이면 끄기")
    ap.add_argument("--fontsdir", default=os.path.expanduser("~/.cache/ranking-video/fonts"))
    A = ap.parse_args()
    D = json.load(open(A.data, encoding="utf-8")); disp = disp_fn(D)
    G = os.path.join(A.proj, "07_그래픽"); OUT = os.path.join(A.proj, "08_완성영상"); os.makedirs(OUT, exist_ok=True)
    WORK = A.work or os.path.join(OUT, "_work"); os.makedirs(WORK, exist_ok=True)
    secs = D["sections"]; N = len(secs)
    cards_by_sec = {}
    for j, c in enumerate(D.get("graphics", {}).get("info_cards", []), 1):
        cards_by_sec.setdefault(c["section"], []).append((f"{G}/04_정보카드/{j:02d}_{c['section']}.png", c.get("at"), c.get("span", 1)))  # span: 카드가 걸치는 문장 수(v2.7.1)

    # ---------- 1) 타임라인 ----------
    t = 0.0; speech = []; visual = []; boosts = []; sfx_ev = []
    sec_spans = []
    for si, s in enumerate(secs):
        name = s["name"]; is_rank = bool(s.get("rank")); first_rank = s.get("rank") == 1
        is_titled = is_rank or bool(s.get("chapter"))  # v2.3.0: 순위 없는 정보 챕터(감별법, 비교 등)도 사진 타이틀 카드
        label = f"{G}/02_상단라벨/{si:02d}_{name}.png"
        badge = f"{G}/03_순위배지/{s['rank']:02d}위.png" if is_rank else None
        card = f"{G}/01_챕터카드/{si:02d}_{name}.png"
        tcard = f"{G}/08_타이틀카드/{si:02d}_{name}.png"
        if is_titled and os.path.exists(tcard): card, d = tcard, (TITLE_FIRST if first_rank else TITLE)  # PPT 표지 같은 대표 사진 카드
        else: d = CARD
        card_start = t
        if si > 0:  # 인트로는 훅부터 시작하고 카드는 card_at 문장 앞에
            visual.append(dict(kind="card", src=card, start=t, end=t + d)); boosts.append((t, t + d)); t += d
        ns = t; sent_times = []
        for ti, x in enumerate(s["sentences"]):
            text, memo = x[0], (x[1] if len(x) > 1 else "")
            if si == 0 and ti == s.get("card_at", -1):  # 인트로 타이틀 카드
                visual.append(dict(kind="card", src=card, start=t, end=t + CARD)); boosts.append((t, t + CARD)); t += CARD
            if is_titled and text.startswith("꿀팁입니다"):
                boosts.append((t, t + BEAT)); t += BEAT
            t += GAP + (GAP_SLOW if "느리게" in memo else 0)
            af = next((f"{A.tts}/{si:02d}_{ti:02d}.{e}" for e in ("wav", "mp3") if os.path.exists(f"{A.tts}/{si:02d}_{ti:02d}.{e}")), None)
            if not af: raise SystemExit(f"음성 파일 없음: {A.tts}/{si:02d}_{ti:02d}.wav|mp3")
            a = trim(load_audio(af))  # Voicebox(wav)와 Edge TTS(mp3) 모두 지원
            dur = len(a) / SR
            speech.append(dict(si=si, ti=ti, start=t, end=t + dur, text=text, memo=memo, audio=a))
            for e in re.findall(r"\(효과음: ([^)]+)\)", memo): sfx_ev.append((max(0, t - 0.15), e))
            sent_times.append((t, t + dur)); t += dur
        t += TAIL
        sec_spans.append(dict(si=si, name=name, start=ns, card_start=card_start, end=t, label=label, badge=badge, sent=sent_times))
    end_start = t
    if D.get("graphics", {}).get("channel_name"):  # v2.6.1: 채널명이 없으면 엔드카드를 붙이지 않는다
        visual.append(dict(kind="card", src=f"{G}/06_엔드카드/엔드카드.png", start=t, end=t + END)); t += END
    TOTAL = t

    # 섹션 안쪽: 정보 카드 / 요약 카드 / 사진 채우기
    meta = json.load(open(os.path.join(A.img, "meta.json"), encoding="utf-8"))
    excl = set(open(os.path.join(A.img, "exclude.txt")).read().split()) if os.path.exists(os.path.join(A.img, "exclude.txt")) else set()
    meta = [m for m in meta if m["id"] not in excl and os.path.exists(os.path.join(A.img, m["id"] + ".jpg"))]
    pool_all = [m["id"] for m in meta]; rnd = random.Random(42); used_count = {}
    own_only = {m["id"] for m in meta if m.get("own_only")}  # "own_only": 다른 섹션에 빌려주지 않음
    pools = {}; first = {m["id"]: m["section"] for m in meta if m.get("first")}  # "first": 그 섹션 첫 장면
    for m in meta: pools.setdefault(m["section"], []).append(m["id"])

    def pick(sec_name):
        cand = pools.get(sec_name, []) + [p for p in pool_all if p not in pools.get(sec_name, []) and p not in own_only]
        cand.sort(key=lambda p: (used_count.get(p, 0) + (0 if p in pools.get(sec_name, []) else 0.5) - (0.9 if first.get(p) == sec_name and not used_count.get(p) else 0), rnd.random()))
        p = cand[0]; used_count[p] = used_count.get(p, 0) + 1; return p

    for sp in sec_spans:
        s = secs[sp["si"]]; occupied = []
        cards = cards_by_sec.get(s["name"], [])
        for k, (cp, at, span) in enumerate(cards):
            idx = min(2 + 3 * k, len(sp["sent"]) - 1)
            if at:  # "at": 이 문장으로 시작하는 문장에 맞춰 카드 표시
                idx = next((i for i, x in enumerate(s["sentences"]) if x[0].startswith(at)), idx)
            st = sp["sent"][idx][0] - 0.2; en = max(st + 3.5, sp["sent"][min(idx + span - 1, len(sp["sent"]) - 1)][1] + 0.3) if at else st + 3.5
            occupied.append((st, en, dict(kind="info", src=cp)))
        if sp["si"] == N - 1:  # 아웃트로 요약 카드
            recap = [i for i, x in enumerate(s["sentences"]) if re.match(D.get("graphics", {}).get("recap_regex", r"^(일위|사위|칠위) "), x[0])]  # v2.3.0: 순위 수에 맞게 바꿀 수 있음
            if recap:
                seq_start = sp["start"]; k = 0
                occupied.append((seq_start, sp["sent"][recap[0]][0], dict(kind="info", src=f"{G}/05_요약카드/00.png")))
                for ri in recap:
                    a, b = sp["sent"][ri]; n = len(re.findall(D.get("graphics", {}).get("recap_item_regex", r"[일이삼사오육칠팔구십]위"), s["sentences"][ri][0]))  # v2.6.0: 순위 아닌 항목(첫째·둘째…)도
                    for q in range(n):
                        k += 1; occupied.append((a + (b - a) * q / n, a + (b - a) * (q + 1) / n, dict(kind="info", src=f"{G}/05_요약카드/{k:02d}.png")))
                last_end = sp["sent"][min(recap[-1] + 2, len(sp["sent"]) - 1)][1]
                nxt = [o[0] for o in occupied if o[0] >= sp["sent"][recap[-1]][1] - 0.3 and "05_요약카드" not in o[2]["src"]]  # v2.7.1: 요약 카드 유지 중에 다른 정보 카드가 시작하면 거기서 끝냄(카드가 먹히던 버그)
                if nxt: last_end = min(last_end, min(nxt))
                occupied.append((sp["sent"][recap[-1]][1], last_end, dict(kind="info", src=f"{G}/05_요약카드/{k:02d}.png")))
        occupied.sort(key=lambda o: o[0])
        # 겹침 정리 + 빈 구간 사진
        cur = sp["start"]; segs = []
        for a, b, v in occupied:
            a = max(a, cur)
            if b <= a: continue
            if a - cur > 0.05: segs.append((cur, a, None))
            segs.append((a, b, v)); cur = b
        if sp["end"] - cur > 0.05: segs.append((cur, sp["end"], None))
        for a, b, v in segs:
            if v:
                visual.append(dict(kind=v["kind"], src=v["src"], start=a, end=b, label=sp["label"])); continue
            n = max(1, round((b - a) / 5.0)); step = (b - a) / n
            for q in range(n):
                visual.append(dict(kind="photo", src=os.path.join(A.img, pick(s["name"]) + ".jpg"), start=a + q * step, end=a + (q + 1) * step,
                                   label=sp["label"], badge=sp["badge"], dir=len(visual) % 4))
    visual.sort(key=lambda v: v["start"])

    # ---------- 2) 오디오 믹스 ----------
    L = int(TOTAL * SR) + SR
    voice = np.zeros(L, np.float32)
    for sp in speech:
        i = int(sp["start"] * SR); voice[i:i + len(sp["audio"])] += sp["audio"]
    voice *= 0.95 / (np.max(np.abs(voice)) + 1e-9)
    bgp = os.path.join(A.sfx, A.bgm); bg = load_audio(bgp if os.path.exists(bgp) else os.path.join(A.sfx, "bgm_loop.wav")); bgm = np.tile(bg, L // len(bg) + 1)[:L]
    gain = np.full(L, 10 ** (-25 / 20), np.float32)  # 내레이션 아래에서는 낮게(목소리가 묻히지 않게)
    for a, b in boosts: gain[int(a * SR):int(b * SR)] = 10 ** (-16 / 20)
    gain[int(end_start * SR):] = 10 ** (-14 / 20)
    k = SR // 5; cs = np.concatenate([[0], np.cumsum(gain, dtype=np.float64)])  # 0.2초 이동평균으로 부드럽게
    sm = (cs[k:] - cs[:-k]) / k; gain = np.concatenate([np.full(k // 2, gain[0]), sm, np.full(len(gain) - len(sm) - k // 2, gain[-1])]).astype(np.float32)
    fade = np.ones(L, np.float32); fade[-3 * SR:] = np.linspace(1, 0, 3 * SR); fade[:SR] = np.linspace(0, 1, SR)
    mix = voice + bgm * gain * fade
    sfx_gain = {"칼 소리": -12, "물방울": -14, "쿠궁": -8, "코인": -12, "갈매기": -16}
    for tt, e in sfx_ev:
        p = os.path.join(A.sfx, f"{e}.wav")
        if not os.path.exists(p): continue
        x = load_audio(p) * 10 ** (sfx_gain.get(e, -12) / 20); i = int(tt * SR); mix[i:i + len(x)] += x[:max(0, L - i)]
    mix = np.clip(mix * (0.89 / (np.max(np.abs(mix)) + 1e-9)), -1, 1)
    wav = os.path.join(WORK, "mix.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())

    # ---------- 3) 영상 클립 ----------
    def clip(i, v):
        out = os.path.join(WORK, f"c{i:04d}.mp4")
        nf = int(round((v["end"] - v["start"]) * FPS)); d = round(nf / FPS, 4)
        if os.path.exists(out): return out
        # 프레임 수를 정확히 고정해야 조각을 이어도 소리와 어긋나지 않는다
        enc = ["-frames:v", str(nf), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-an", out]
        if v["kind"] == "photo":
            dx = ["(iw-ow)*t/{d}", "(iw-ow)*(1-t/{d})", "(iw-ow)/2", "(iw-ow)/2"][v["dir"]].format(d=d)
            dy = ["(ih-oh)/2", "(ih-oh)/2", "(ih-oh)*t/{d}", "(ih-oh)*(1-t/{d})"][v["dir"]].format(d=d)
            ins = ["-loop", "1", "-t", str(d + 1), "-i", v["src"], "-loop", "1", "-i", v["label"]]
            fc = f"[0]scale=2112:1188:force_original_aspect_ratio=increase,crop=2112:1188,eq=saturation=1.08,crop=1920:1080:x='{dx}':y='{dy}'[bg];[bg][1]overlay[a]"
            if v.get("badge"): ins += ["-loop", "1", "-i", v["badge"]]; fc += ";[a][2]overlay[o]"; last = "[o]"
            else: last = "[a]"
            run(["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", fc + f";{last}fps={FPS},format=yuv420p[v]", "-map", "[v]"] + enc)
        elif "08_타이틀카드" in v["src"]:  # v2.1.0: 타이틀 카드는 천천히 확대(켄 번스)
            fc = (f"[0]scale=2304:1296,zoompan=z='min(1+0.0011*on,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps={FPS},"
                  f"fade=t=in:st=0:d=0.25,format=yuv420p[v]")
            run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(d + 1), "-i", v["src"], "-filter_complex", fc, "-map", "[v]"] + enc)
        else:
            ins = ["-loop", "1", "-t", str(d + 1), "-i", v["src"]]; fc = "[0]scale=1920:1080,format=rgba[bg]"
            if v.get("label"): ins += ["-loop", "1", "-i", v["label"]]; fc += ";[bg][1]overlay[bg2]"; last = "[bg2]"
            else: last = "[bg]"
            fc += f";{last}fade=t=in:st=0:d=0.2,fps={FPS},format=yuv420p[v]"
            run(["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", fc, "-map", "[v]"] + enc)
        return out

    if A.until:  # 샘플: 앞부분만
        TOTAL = min(TOTAL, A.until)
        visual = [dict(v, end=min(v["end"], TOTAL)) for v in visual if v["start"] < TOTAL]
        speech[:] = [x for x in speech if x["start"] < TOTAL]
    # 프레임 단위로 길이를 맞춰 누적 오차 방지
    fr = [round(v["start"] * FPS) for v in visual] + [round(TOTAL * FPS)]
    for i, v in enumerate(visual): v["start"], v["end"] = fr[i] / FPS, fr[i + 1] / FPS
    visual = [v for v in visual if v["end"] - v["start"] >= 1 / FPS]
    with cf.ThreadPoolExecutor(A.jobs) as ex: files = list(ex.map(lambda p: clip(*p), enumerate(visual)))
    lst = os.path.join(WORK, "list.txt")
    open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    silent = os.path.join(WORK, "video_noaudio.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])
    vd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", silent], capture_output=True, text=True).stdout)
    if abs(vd - TOTAL) > 0.2: raise RuntimeError(f"영상 길이 {vd:.2f}s ≠ 타임라인 {TOTAL:.2f}s — 싱크가 어긋남")

    # ---------- 4) 자막 (ASS 굽기 + SRT) ----------
    hooks = {(sp_["si"], 0) for sp_ in sec_spans}
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Base,Pretendard,87,&H00FFFFFF,&H00FFFFFF,&H70000000,&H00000000,-1,0,0,0,100,100,0,0,3,20,0,2,60,60,64,1",
           "Style: Tip,Pretendard,87,&H007DC319,&H007DC319,&H70000000,&H00000000,-1,0,0,0,100,100,0,0,3,20,0,2,60,60,64,1",
           "Style: Emph,Pretendard ExtraBold,124,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,2,60,60,120,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    srt = []; n = 0
    for sp in speech:
        style = "Emph" if (sp["si"], sp["ti"]) in hooks else ("Tip" if sp["text"].startswith("꿀팁") or "꿀팁" in sp["memo"] else "Base")
        if secs[sp["si"]].get("rank") and sp["text"].startswith("꿀팁"): sp["_tip"] = True
        lines = one_line(disp(sp["text"]), 13 if style == "Emph" else 18); tot = sum(len(x) for x in lines); t0 = sp["start"]
        durs = voice_split(sp["audio"], [len(x) for x in lines], sp["end"] - sp["start"])  # v2.7.1: 글자 수가 아니라 실제 목소리(쉼 포함)에 맞춰 줄을 바꾼다
        for qi, x in enumerate(lines):
            d = durs[qi]
            xs = x if style == "Emph" else re.sub(r"(\d[\d,~·.]*(?:월|위|년|배|지|개|분|kg|%)?)", r"{\\c&H40D6FF&}\1{\\r}", x)  # 숫자·월은 노랑
            ass.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t0 + d)},{style},,0,0,0,,{xs}")
            n += 1; srt.append(f"{n}\n{srt_time(t0)} --> {srt_time(t0 + d)}\n{x}\n")
            t0 += d
    # 꿀팁 구간(꿀팁 문장부터 그 섹션의 맺음 직전까지)은 초록
    ass_path = os.path.join(WORK, "subs.ass"); open(ass_path, "w", encoding="utf-8").write("\n".join(ass) + "\n")
    if not A.until: open(os.path.join(OUT, "자막_실제타이밍.srt"), "w", encoding="utf-8").write("\n".join(srt))

    final = os.path.join(OUT, "샘플.mp4" if A.until else "완성영상.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-vf", f"subtitles={ass_path}:fontsdir={A.fontsdir}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
         *(["-af", f"loudnorm=I={A.lufs}:TP=-2.0:LRA=11,alimiter=limit=0.84:level=disabled"] if A.lufs else []),  # v2.7.0: 통합 음량을 -16 LUFS 근처로(이전엔 -19라 작았음)
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", final])
    if A.until: print(f"샘플 완성: {final}  길이 {int(TOTAL // 60)}:{int(TOTAL % 60):02d}"); return
    # 전달용: 2패스 720p, 목표 29MB (오디오 64k 모노)
    vk = max(150, int((29 * 8 * 1024) / TOTAL - 64))
    deliver = os.path.join(OUT, re.sub(r"[^\w가-힣]+", "", D.get("title", "영상"))[:30] + "_완성본_720p.mp4")
    pl = os.path.join(WORK, "pass")
    run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-pass", "1", "-passlogfile", pl, "-an", "-f", "null", "/dev/null"])
    run(["ffmpeg", "-y", "-v", "error", "-i", final, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-pass", "2", "-passlogfile", pl,
         "-c:a", "aac", "-b:a", "64k", "-ac", "1", "-movflags", "+faststart", deliver])
    print(f"전달본: {deliver} ({os.path.getsize(deliver) / 1e6:.1f}MB)")
    tl = [dict(section=secs[sp["si"]]["name"], start=round(sp["start"], 2)) for sp in sec_spans]
    json.dump(dict(total_seconds=round(TOTAL, 2), sections=[dict(name=secs[x["si"]]["name"], start=round(x["start"], 2)) for x in sec_spans],
                   chapters=[dict(name=secs[x["si"]]["name"], card=round(x["card_start"], 2)) for x in sec_spans],
                   images_used=sorted({os.path.basename(v["src"])[:-4] for v in visual if v["kind"] == "photo"})),
              open(os.path.join(OUT, "타임라인.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"완성: {final}  길이 {int(TOTAL // 60)}:{int(TOTAL % 60):02d}  클립 {len(visual)}개  자막 {n}큐")


if __name__ == "__main__":
    main()
