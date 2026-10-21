#!/usr/bin/env python3
"""얼굴없는 유튜브 영상 자동 편집기.

사용:
  python make_video.py projects/주제.yaml            # 전체 제작 + 검수
  python make_video.py projects/주제.yaml --tts sherpa --no-qc
결과: output/<프로젝트이름>/ 아래 final.mp4, subtitles.srt, qc_report.md, contact_sheet.png
"""
import argparse
import os
import shutil
import sys
import time

import yaml

from facetube.build import load_style, build_timeline, render_video, write_srt, preflight
from facetube.textnorm import COMMON_TYPOS
from facetube.voice import Voice
from facetube import qc

ROOT = os.path.dirname(os.path.abspath(__file__))


def autocorrect(project, log):
    """확실한 맞춤법 오류는 대본 단계에서 바로 고친다(보고서에 기록)."""
    fixes = []
    for sc in project["scenes"]:
        say = sc.get("say")
        if not say:
            continue
        lst = [say] if isinstance(say, str) else say
        new = []
        for s in lst:
            o = s
            for bad, good in COMMON_TYPOS.items():
                if not good.endswith("확인") and bad in s:
                    s = s.replace(bad, good)
            if s != o:
                fixes.append(f"'{o}' → '{s}'")
            new.append(s)
        sc["say"] = new if isinstance(say, list) else new[0]
    for f in fixes:
        log("  자동 교정: " + f)
    return fixes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out", help="출력 폴더 (기본 output/<이름>)")
    ap.add_argument("--tts", default=None, help="auto | edge | sherpa")
    ap.add_argument("--no-qc", action="store_true")
    ap.add_argument("--procs", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()

    t0 = time.time()
    st = load_style()
    project = yaml.safe_load(open(a.project, encoding="utf-8"))
    name = project.get("slug") or os.path.splitext(os.path.basename(a.project))[0]
    out = a.out or os.path.join(ROOT, "output", name)
    work = os.path.join(out, "_work")
    os.makedirs(work, exist_ok=True)
    log = lambda m: print(m, flush=True)

    log("① 대본 사전검사")
    fixes = autocorrect(project, log)
    for i in preflight(project, st):
        log("  ! " + i)

    vc = project.get("voice", {})
    voice = Voice(backend=a.tts or vc.get("backend", "auto"), voice=vc.get("name"),
                  speed=vc.get("speed", 1.05), cer_retry=st["qc"]["asr_cer_retry"])
    log(f"② 음성 더빙 ({voice.backend}) + 덩어리별 음성인식 대조")
    tl = build_timeline(project, st, work, voice, log)
    log(f"   총 길이 {tl['total']:.1f}초, 장면 {len(tl['scenes'])}개, 자막 {sum(len(s['chunks']) for s in tl['scenes'])}개")

    log("③ 영상 렌더링")
    mp4 = os.path.join(out, "final.mp4")
    render_video(tl, st, work, mp4, procs=a.procs, log=log)
    write_srt(tl, os.path.join(out, "subtitles.srt"))

    if not a.no_qc:
        log("④ 품질검수")
        rep = qc.run_qc(mp4, tl, st, work, None, log=log)
        md = qc.report_md(rep, tl, st)
        if fixes:
            md += "\n## 대본 자동 교정\n" + "\n".join(f"- {f}" for f in fixes) + "\n"
        open(os.path.join(out, "qc_report.md"), "w", encoding="utf-8").write(md)
        if rep.get("sheet"):
            shutil.copy(rep["sheet"], os.path.join(out, "contact_sheet.png"))
        print(md)
    log(f"완료: {mp4}  ({time.time() - t0:.0f}초 소요)")


if __name__ == "__main__":
    sys.exit(main())
