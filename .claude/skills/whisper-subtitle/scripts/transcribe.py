#!/usr/bin/env python3
"""faster-whisper 받아쓰기 → srt / words.json / txt, 대본 대조(check.tsv)."""
import argparse, difflib, json, os, re, subprocess
import numpy as np

def load_pcm(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)

def split_line(words, maxc=30):
    """단어 목록을 30자 이하 줄로 나눈다(문장 끝·쉼표 우선)."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        text = "".join(x["w"] for x in cur).strip()
        if len(text) >= maxc or re.search(r"[.?!]$", w["w"].strip()) or (len(text) > maxc * 0.6 and w["w"].strip().endswith(",")):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media"); ap.add_argument("--out", default=".")
    ap.add_argument("--model", default="medium"); ap.add_argument("--device", default="cpu"); ap.add_argument("--compute", default="int8")
    ap.add_argument("--lang", default="ko"); ap.add_argument("--script")
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    os.makedirs(a.out, exist_ok=True)
    name = os.path.splitext(os.path.basename(a.media))[0]
    m = WhisperModel(a.model, device=a.device, compute_type=a.compute)
    segs, info = m.transcribe(load_pcm(a.media), language=a.lang, beam_size=5, word_timestamps=True, vad_filter=True)
    words, full = [], []
    for s in segs:
        full.append(s.text.strip())
        for w in (s.words or []):
            words.append({"w": w.word, "start": round(w.start, 3), "end": round(w.end, 3)})
    json.dump(words, open(os.path.join(a.out, name + ".words.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    open(os.path.join(a.out, name + ".txt"), "w", encoding="utf-8").write("\n".join(full) + "\n")
    with open(os.path.join(a.out, name + ".srt"), "w", encoding="utf-8") as f:
        for i, ln in enumerate(split_line(words)):
            f.write("%d\n%s --> %s\n%s\n\n" % (i + 1, ts(ln[0]["start"]), ts(ln[-1]["end"]), "".join(x["w"] for x in ln).strip()))
    print("[whisper] %s: 문장 %d개, 단어 %d개 → %s.srt" % (name, len(full), len(words), name))
    if a.script:
        norm = lambda s: re.sub(r"[^가-힣0-9A-Za-z]", "", s)
        lines = [l.strip().split(" || ")[0].lstrip("!") for l in open(a.script, encoding="utf-8") if l.strip() and l.strip()[0] not in "#@"]
        hyp = norm("".join(full)); pos = 0; rows = []
        for i, l in enumerate(lines):
            ref = norm(l); best = (0, pos, pos)
            for st in range(max(0, pos - 5), min(len(hyp), pos + 15) + 1):
                for ln in (len(ref) - 3, len(ref), len(ref) + 3):
                    if ln <= 0: continue
                    r = difflib.SequenceMatcher(None, ref, hyp[st:st + ln]).ratio()
                    if r > best[0]: best = (r, st, st + ln)
            pos = best[2]; rows.append((i + 1, best[0], l, hyp[best[1]:best[2]]))
        with open(os.path.join(a.out, name + ".check.tsv"), "w", encoding="utf-8") as f:
            f.write("줄\t일치율\t대본\t받아쓰기\n")
            for r in rows: f.write("%d\t%.2f\t%s\t%s\n" % r)
        bad = [r for r in rows if r[1] < 0.85]
        print("[check] %d줄 중 의심 %d줄 → %s.check.tsv" % (len(rows), len(bad), name))
        for r in bad[:20]: print("  %3d %.2f | %s | %s" % r)

if __name__ == "__main__":
    main()
