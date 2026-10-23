# -*- coding: utf-8 -*-
"""TTS 발음 검수: 문장별 음성을 음성 인식(Whisper)으로 다시 받아 적어 대본과 비교 (ranking-video v2.1.0)

사용법: python3 check_tts.py <대본데이터.json> <tts폴더> [--model small] [--th 0.85]
필요: pip install faster-whisper (모델은 huggingface에서 자동 다운로드, 약 500MB)
출력: <tts폴더>/발음검수.tsv  (유사도 낮은 순서). 콘솔에는 기준 미달 문장만 출력한다.

판정 기준: 대본을 자막용 표기(display_map, 숫자)로 바꾼 뒤 한글과 숫자만 남겨 비교한다.
유사도가 기준(기본 0.85)보다 낮은 문장은 TTS가 어색하게 읽었을 가능성이 높으므로
표현을 바꾸거나(외래어, 숫자, 약어) 띄어쓰기와 쉼표를 조정한 뒤 그 문장만 TTS를 다시 만든다.
※ 음성 인식 자체의 오류도 섞여 있으므로 최종 판단은 사람이 문장을 읽어 보고 한다.
"""
import difflib, json, os, re, subprocess, sys
import numpy as np

RANK = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5", "육": "6", "칠": "7", "팔": "8", "구": "9", "십": "10"}


def norm(t):
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t)
    return re.sub(r"[^가-힣0-9]", "", t)


def main():
    a = sys.argv[1:]
    model = a[a.index("--model") + 1] if "--model" in a else "small"
    th = float(a[a.index("--th") + 1]) if "--th" in a else 0.85
    D = json.load(open(a[0], encoding="utf-8")); tts = a[1]
    dm = D.get("display_map", [])
    def disp(t):
        for x, y in dm: t = t.replace(x, y)
        return re.sub(r"(?<![가-힣])([일이삼사오육칠팔구십])위", lambda m: RANK[m.group(1)] + "위", t)
    from faster_whisper import WhisperModel
    M = WhisperModel(model, device="cpu", compute_type="int8", download_root=os.path.expanduser("~/.cache/ranking-video/whisper"))
    rows = []
    for si, s in enumerate(D["sections"]):
        for ti, x in enumerate(s["sentences"]):
            f = next((os.path.join(tts, f"{si:02d}_{ti:02d}.{e}") for e in ("wav", "mp3") if os.path.exists(os.path.join(tts, f"{si:02d}_{ti:02d}.{e}"))), None)
            if not f: continue
            au = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, np.float32)
            segs, _ = M.transcribe(au, language="ko", beam_size=5)  # 대본을 힌트로 주지 않는다(오류를 가리므로)
            heard = " ".join(z.text.strip() for z in segs)
            r = difflib.SequenceMatcher(None, norm(disp(x[0])), norm(heard)).ratio()
            rows.append((r, f"{si:02d}_{ti:02d}", x[0], heard))
    rows.sort()
    with open(os.path.join(tts, "발음검수.tsv"), "w", encoding="utf-8") as o:
        o.write("유사도\t파일\t대본\t인식결과\n")
        for r, k, t, h in rows: o.write(f"{r:.2f}\t{k}\t{t}\t{h}\n")
    bad = [x for x in rows if x[0] < th]
    print(f"검수 {len(rows)}문장, 기준({th}) 미달 {len(bad)}문장")
    gs = [(f"{si:02d}_{ti:02d}", x[0]) for si, s_ in enumerate(D["sections"]) for ti, x in enumerate(s_["sentences"]) if x[0].lstrip().startswith("그")]
    if gs:  # v2.7.3: '그'로 시작하는 문장은 [그그]로 더듬는 경향 → 반드시 고친다
        print(f"⚠ '그'로 시작하는 문장 {len(gs)}개 (TTS가 '그그'로 읽음):")
        for sid, t in gs: print(f"   {sid}  {t[:40]}")
    for r, k, t, h in bad: print(f"  {r:.2f} {k}\n    대본: {t}\n    인식: {h}")


if __name__ == "__main__":
    main()
