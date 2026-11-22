# -*- coding: utf-8 -*-
"""3개 샘플 대본 -> 여의도여자(Voicebox) 문장별 생성 -> voice.wav + script.txt + timings.json(단어별, 음절 비례)"""
import json, os, re, subprocess, sys, time, urllib.request, wave

URL = "http://127.0.0.1:17493"
INSTRUCT = ("미스터리 다큐멘터리 내레이터 톤. 낮고 차분하지만 긴장감 있게, 약간 빠른 속도. "
            "숫자와 핵심 낱말은 또박또박 힘주어 읽고, 마지막 문장은 여운을 남기며 닫는다.")
ROOT = os.environ.get("OUT_DIR") or os.getcwd()  # 출력 폴더 (OUT_DIR 또는 현재 폴더)
SCRIPTS = {
    "A_legion": ["서기 2세기, 로마 최정예 제9군단이 기록에서 사라졌습니다.",
                 "오천 명의 병사, 그런데 전투 기록도, 시신도 없었죠.",
                 "그들은 대체 어디로 간 걸까요?"],
    "B_voynich": ["1912년, 한 고서상이 아무도 읽을 수 없는 책을 샀습니다.",
                  "백 년 넘게, 어떤 천재도 한 줄을 해독하지 못했죠.",
                  "그런데 종이의 나이는, 무려 육백 년이었습니다."],
    "C_celeste": ["1872년, 대서양 한가운데서 유령선 한 척이 발견됐습니다.",
                  "식량도 화물도 그대로인데, 열 명이 감쪽같이 사라졌죠.",
                  "없어진 건, 구명보트 단 한 척뿐이었습니다."],
}
GAP = 0.28
FF = "ffmpeg"


def vb(path, body=None, raw=False, timeout=600):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(URL + path, data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with op.open(req, timeout=timeout) as r:
        d = r.read()
    return d if raw else json.loads(d.decode("utf-8"))


def tts(text, out, seed=11):
    profs = vb("/profiles")
    p = next(x for x in profs if x["name"] == "여의도여자")
    body = {"profile_id": p["id"], "text": text, "language": "ko", "model_size": "1.7B",
            "engine": "qwen_custom_voice", "seed": seed, "instruct": INSTRUCT}
    gid = vb("/generate", body)["id"]
    for _ in range(900):
        h = vb("/history/%s" % gid, timeout=30)
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError(h.get("error"))
        time.sleep(2)
    open(out, "wb").write(vb("/audio/%s" % gid, raw=True))


def speech_bounds(wav):
    """앞뒤 무음 잘라낸 구간(초)"""
    r = subprocess.run([FF, "-i", wav, "-af", "silencedetect=n=-40dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr).groups()[2]) + 60 * float(re.search(r"Duration: (\d+):(\d+)", r.stderr).group(2))
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    a = ends[0] if starts and starts[0] < 0.02 and ends else 0.0
    b = starts[-1] if starts and (not ends or starts[-1] > ends[-1]) else dur
    return max(0, a - 0.03), min(dur, b + 0.08)


def syl(w):
    return max(1, len(re.findall(r"[가-힣0-9A-Za-z]", w)))


for name, lines in SCRIPTS.items():
    d = os.path.join(ROOT, name); os.makedirs(d, exist_ok=True)
    parts, words, t = [], [], 0.0
    for i, line in enumerate(lines):
        raw = os.path.join(d, "s%d_raw.wav" % i)
        if not os.path.exists(raw):
            t0 = time.time(); tts(line, raw); print(name, i, "tts %.0fs" % (time.time() - t0), flush=True)
        a, b = speech_bounds(raw)
        cut = os.path.join(d, "s%d.wav" % i)
        subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-ss", "%.3f" % a, "-to", "%.3f" % b, "-ar", "48000", "-ac", "1", cut], check=True)
        L = b - a
        toks = line.split()
        tot = sum(syl(w) for w in toks)
        # 쉼표 뒤 짧은 쉼 반영: 음절 비례 분배
        c = t
        for w in toks:
            dw = L * syl(w) / tot
            words.append({"word": w, "start": round(c, 3), "end": round(c + dw * 0.92, 3)})
            c += dw
        parts.append(cut); t += L
        if i < len(lines) - 1:
            t += GAP
    # concat with gaps
    gap = os.path.join(d, "gap.wav")
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(GAP), gap], check=True)
    lst = os.path.join(d, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for i, p in enumerate(parts):
            f.write("file '%s'\n" % p.replace("\\", "/"))
            if i < len(parts) - 1:
                f.write("file '%s'\n" % gap.replace("\\", "/"))
    subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "48000", "-ac", "1", os.path.join(d, "voice.wav")], check=True)
    open(os.path.join(d, "script.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(words, open(os.path.join(d, "timings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(name, "total %.2fs" % t, len(words), "words", flush=True)
