"""완성본 검수: 음성↔대본 불일치, 소리 끊김, 화면 멈춤/검은화면, 개인정보 노출, 자막 오타.
결과는 qc_report.md / qc.json, 그리고 눈으로 확인할 contact sheet."""
import json
import os
import re
import subprocess

import numpy as np
import soundfile as sf

from .textnorm import cer, strip_markup, to_speech, lint_subtitle

PII_PATTERNS = {
    "전화번호": r"01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}",
    "일반전화": r"0(2|[3-6][1-5])[-\s.]?\d{3,4}[-\s.]?\d{4}",
    "주민등록번호": r"\d{6}\s?-\s?[1-4]\d{6}",
    "이메일": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "카드번호": r"\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b",
    "계좌번호": r"\b\d{3,6}-\d{2,6}-\d{3,8}\b",
    "차량번호": r"\b\d{2,3}[가-힣]\s?\d{4}\b",
    "IP주소": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
}


def _ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + args, capture_output=True, text=True).stderr


def detect_freeze(mp4, min_sec):
    err = _ff(["-i", mp4, "-vf", f"freezedetect=n=0.0008:d={min_sec}", "-map", "0:v", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", err)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def detect_black(mp4):
    err = _ff(["-i", mp4, "-vf", "blackdetect=d=0.3:pix_th=0.08", "-an", "-f", "null", "-"])
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)


def audio_stats(mp4):
    err = _ff(["-i", mp4, "-af", "astats=metadata=0,ebur128=peak=true", "-vn", "-f", "null", "-"])
    peak = re.findall(r"Peak level dB: ([-\d.inf]+)", err)
    lufs = re.findall(r"I:\s+([-\d.]+) LUFS", err)
    return {"peak_db": float(peak[-1]) if peak else None, "lufs": float(lufs[-1]) if lufs else None}


def narration_gaps(voice_wav, chunks, max_sil):
    """각 덩어리 '안쪽'에서 max_sil 이상 무음 = 음성 끊김."""
    x, sr = sf.read(voice_wav, dtype="float32")
    hop = int(sr * 0.02)
    gaps = []
    for c in chunks:
        seg = x[int(c["start"] * sr):int(c["end"] * sr)]
        if len(seg) < hop * 3:
            continue
        rms = np.array([np.sqrt(np.mean(seg[i:i + hop] ** 2)) for i in range(0, len(seg) - hop, hop)])
        quiet = rms < 0.008
        run = best = 0
        for q in quiet:
            run = run + 1 if q else 0
            best = max(best, run)
        if best * 0.02 >= max_sil:
            gaps.append({"t": round(c["start"], 2), "text": strip_markup(c["text"]), "silence": round(best * 0.02, 2)})
    return gaps


def final_asr(mp4, chunks, workdir):
    """완성본 오디오(배경음·효과음 섞인 상태)를 다시 받아적어 대본과 비교."""
    from .voice import transcribe
    wav = os.path.join(workdir, "final16k.wav")
    _ff(["-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav])
    x, sr = sf.read(wav, dtype="float32")
    rows = []
    for c in chunks:
        seg = x[max(0, int((c["start"] - 0.05) * sr)):int((c["end"] + 0.05) * sr)]
        hyp = transcribe(seg, sr)
        ref = to_speech(c["text"])
        rows.append({"t": round(c["start"], 2), "script": strip_markup(c["text"]), "spoken": ref, "heard": hyp,
                     "cer": round(cer(ref, hyp), 3)})
    return rows


def ocr_frames(mp4, workdir, every=1.0):
    d = os.path.join(workdir, "ocr")
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    _ff(["-y", "-i", mp4, "-vf", f"fps=1/{every},scale=1920:-1", os.path.join(d, "f_%05d.png")])
    hits = []
    for fn in sorted(os.listdir(d)):
        t = (int(fn[2:7]) - 1) * every
        tsv = subprocess.run(["tesseract", os.path.join(d, fn), "-", "-l", "kor+eng", "--psm", "11", "tsv"],
                             capture_output=True, text=True).stdout
        words = [r.split("\t") for r in tsv.splitlines()[1:] if r.count("\t") >= 11 and r.split("\t")[11].strip()]
        text = " ".join(w[11] for w in words)
        seen = set()
        for kind, pat in PII_PATTERNS.items():
            for m in re.finditer(pat, text):
                if m.group(0) in seen:      # 같은 문자열 중복 판정 방지(전화번호=계좌번호 패턴 등)
                    continue
                seen.add(m.group(0))
                box = None
                for w in words:   # 대략적인 위치(일치 단어의 박스)
                    if w[11] and w[11] in m.group(0):
                        l, tp, wd, ht = map(int, w[6:10])
                        box = [l, tp, wd, ht] if box is None else [min(box[0], l), min(box[1], tp),
                                                                     max(box[0] + box[2], l + wd) - min(box[0], l),
                                                                     max(box[1] + box[3], tp + ht) - min(box[1], tp)]
                hits.append({"t": t, "kind": kind, "text": m.group(0), "box": box})
    return hits


def blur_regions(mp4, hits, out_mp4, pad=30):
    """개인정보 감지 위치를 해당 시간대만 흐림 처리."""
    hits = sorted((h for h in hits if h.get("box")), key=lambda h: (h["text"], h["t"]))
    if not hits:
        return False
    spans = []   # 같은 글자·같은 위치의 연속 탐지는 한 구간으로
    for h in hits:
        if spans and spans[-1]["text"] == h["text"] and h["t"] - spans[-1]["t1"] <= 2.01 \
                and abs(spans[-1]["box"][0] - h["box"][0]) < 40 and abs(spans[-1]["box"][1] - h["box"][1]) < 40:
            spans[-1]["t1"] = h["t"]
        else:
            spans.append({"text": h["text"], "box": h["box"], "t0": h["t"], "t1": h["t"]})
    chain, last = [], "0:v"
    for i, h in enumerate(spans):
        x, y, w, hh = h["box"]
        x, y, w, hh = max(0, x - pad), max(0, y - pad), w + 2 * pad, hh + 2 * pad
        a, b = max(0, h["t0"] - 1.0), h["t1"] + 1.0
        chain.append(f"[{last}]split[m{i}][c{i}];[c{i}]crop={w}:{hh}:{x}:{y},boxblur=20:5[b{i}];"
                     f"[m{i}][b{i}]overlay={x}:{y}:enable='between(t,{a},{b})'[o{i}]")
        last = f"o{i}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-filter_complex", ";".join(chain), "-map", f"[{last}]",
                    "-map", "0:a", "-c:a", "copy", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", out_mp4], check=True)
    return True


def contact_sheet(mp4, chunks, out_png, cols=4):
    """각 자막 덩어리 중간 프레임을 모아 한 장으로(사람/AI 눈 검수용)."""
    import tempfile
    from PIL import Image, ImageDraw
    from .gfx import font
    tmp = tempfile.mkdtemp()
    thumbs = []
    for i, c in enumerate(chunks):
        tm = (c["start"] + c["end"]) / 2
        p = os.path.join(tmp, f"{i:04d}.png")
        _ff(["-y", "-ss", f"{tm:.2f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=480:-1", p])
        if os.path.exists(p):
            thumbs.append((tm, p))
    if not thumbs:
        return None
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480, rows * 300), "white")
    d = ImageDraw.Draw(sheet)
    for k, (tm, p) in enumerate(thumbs):
        im = Image.open(p)
        x, y = (k % cols) * 480, (k // cols) * 300
        sheet.paste(im, (x, y))
        d.text((x + 6, y + 274), f"{tm:5.1f}s", fill="black", font=font("Pretendard-Bold.otf", 20))
    sheet.save(out_png)
    return out_png


def run_qc(mp4, tl, st, workdir, script_lines, auto_fix=True, log=print):
    q = st["qc"]
    chunks = [c for sc in tl["scenes"] for c in sc["chunks"]]
    rep = {"file": mp4}
    log("  QC: 완성본 음성 재인식(대본 대조)…")
    rep["asr"] = final_asr(mp4, chunks, workdir)
    rep["asr_bad"] = [r for r in rep["asr"] if r["cer"] > q["asr_cer_fail"]]
    rep["tts_retried"] = [r for r in tl["tts"] if (r.get("tries") or 1) > 1]
    log("  QC: 소리 끊김 / 음량…")
    rep["gaps"] = narration_gaps(os.path.join(workdir, "voice.wav"), chunks, q["max_silence_sec"])
    rep["audio"] = audio_stats(mp4)
    log("  QC: 화면 멈춤 / 검은 화면…")
    rep["freeze"] = detect_freeze(mp4, q["freeze_sec"])
    rep["black"] = detect_black(mp4)
    log("  QC: 화면 OCR 개인정보 탐지…")
    rep["pii"] = ocr_frames(mp4, workdir, q["ocr_every_sec"])
    rep["subtitle_lint"] = [(strip_markup(c["text"]), lint_subtitle(c["text"])) for c in chunks if lint_subtitle(c["text"])]
    rep["fixed"] = []
    if auto_fix and rep["pii"]:
        fixed = mp4.replace(".mp4", "_pii.mp4")
        if blur_regions(mp4, rep["pii"], fixed):
            os.replace(fixed, mp4)
            rep["fixed"].append(f"개인정보 {len(rep['pii'])}건 흐림 처리")
    # 길이 일치
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                               capture_output=True, text=True).stdout.strip() or 0)
    rep["duration"] = round(dur, 2)
    rep["sheet"] = contact_sheet(mp4, chunks, os.path.join(workdir, "contact_sheet.png"))
    json.dump(rep, open(os.path.join(workdir, "qc.json"), "w"), ensure_ascii=False, indent=1, default=str)
    return rep


def report_md(rep, tl, st):
    q = st["qc"]
    L = [f"# 품질검수 보고서", "", f"- 파일: `{os.path.basename(rep['file'])}`  길이 {rep['duration']}초",
         f"- 음량: {rep['audio'].get('lufs')} LUFS (목표 {st['audio']['loudness_lufs']}), 피크 {rep['audio'].get('peak_db')} dB", ""]
    ok = lambda b: "✅" if b else "⚠️"
    L.append("| 항목 | 결과 |")
    L.append("|---|---|")
    L.append(f"| 음성↔대본 일치(완성본 재인식) | {ok(not rep['asr_bad'])} 불일치 {len(rep['asr_bad'])}/{len(rep['asr'])} 구간 (CER>{q['asr_cer_fail']}) |")
    L.append(f"| TTS 자동 재생성 | {len(rep['tts_retried'])}구간 재생성 후 최적본 채택 |")
    L.append(f"| 소리 끊김 | {ok(not rep['gaps'])} {len(rep['gaps'])}건 |")
    L.append(f"| 화면 멈춤({q['freeze_sec']}초 이상) | {ok(not rep['freeze'])} {len(rep['freeze'])}건 |")
    L.append(f"| 검은 화면 | {ok(not rep['black'])} {len(rep['black'])}건 |")
    L.append(f"| 개인정보 노출(OCR) | {ok(not rep['pii'])} {len(rep['pii'])}건 {'→ 자동 흐림' if rep['fixed'] else ''} |")
    L.append(f"| 자막 맞춤법/형식 | {ok(not rep['subtitle_lint'])} {len(rep['subtitle_lint'])}건 |")
    L.append("")
    L.append("## 구간별 음성 대조")
    L.append("| 시간 | 자막(대본) | TTS가 읽은 문장 | 완성본에서 들린 말 | CER |")
    L.append("|---|---|---|---|---|")
    for r in rep["asr"]:
        flag = " ⚠️" if r["cer"] > q["asr_cer_fail"] else ""
        L.append(f"| {r['t']} | {r['script']} | {r['spoken']} | {r['heard']} | {r['cer']}{flag} |")
    for title, key in (("소리 끊김", "gaps"), ("화면 멈춤", "freeze"), ("개인정보", "pii"), ("자막 검사", "subtitle_lint")):
        if rep[key]:
            L += ["", f"## {title}"] + [f"- {x}" for x in rep[key]]
    if rep["fixed"]:
        L += ["", "## 자동 수정"] + [f"- {x}" for x in rep["fixed"]]
    return "\n".join(L) + "\n"
