# -*- coding: utf-8 -*-
"""역사 쇼츠 사운드 마감: BGM(분위기 전환·덕킹) + 장면 배경음(bed) + 대본 키워드 효과음 + 크레딧.
Stickman Video Director(MIT)의 사운드 원칙을 toon2d 파이프라인에 맞춘 것:
  - 대사가 말하는 사건은 '들려야' 한다(칼·말발굽·성문·물살·판결봉).
  - 효과음은 꼭 필요한 곳만(최소 간격), 배경음은 내레이션보다 훨씬 작게 계속 깔기.
  - 첫 프레임부터 소리가 있어야 한다(무음 인트로 금지).
  - 음악은 내레이션이 나올 때 내려가고(사이드체인), 쉼에서 올라온다.

사용: python sfx_bgm.py <프로젝트> [--video final.mp4] [--out final_sfx.mp4] [--ep 1] [--plan sfx_plan.json] [--dry]
  - 프로젝트에 plan.json, words.json 필요(t2d.py plan 이후). video 기본값 final.mp4(join 결과, 음악 없음).
  - 처음 실행하면 자동 스팟팅 결과를 sfx_plan.json 으로 저장. 고친 뒤 --plan sfx_plan.json 으로 다시 돌리면 그대로 씀.
  - --dry: 믹스 없이 sfx_plan.json 만 만들고 표로 출력.
  - 결과: out mp4(영상 복사, 오디오만 새로), audio_credits.txt(실제로 쓴 CC BY 음원 크레딧 → 업로드 TXT 설명에 붙임).
음원: ../audio/music/T_*.mp3(긴장), S_*.mp3(슬픔·여운), ../audio/sfx/*. 출처는 ../audio/CREDITS.md. 음원을 내려받지 않는다.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.environ.get("HTS_AUDIO") or os.path.normpath(os.path.join(HERE, "..", "audio"))
try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FF = "ffmpeg"

# 키워드(부분 문자열) → 효과음. 위에서부터 먼저 맞는 것 하나만.
RULES = [
    (("베라", "베였", "베어", "베던", "처형", "목이", "칼끝", "칼을"), [("swish_sword_1.wav", 0.0, 0.55), ("hit_heavy.ogg", 0.12, 0.6)]),
    (("판결", "재판"), [("gavel_wood.ogg", 0.0, 0.8), ("gavel_wood.ogg", 0.28, 0.6)]),
    (("말머리", "흰 말", "기병", "말발굽", "회군.", "회군한"), [("horse_gallop_ground.mp3", 0.0, 0.5, 4)]),
    (("성문", "문을", "궁궐"), [("door_wood.ogg", 0.0, 0.7)]),
    (("떠내려", "여울", "강물", "물에"), [("splash.ogg", 0.0, 0.5)]),
    (("반전", "첫째", "둘째"), [("bell_heavy.ogg", 0.0, 0.45)]),
    (("환호", "반겼", "맞이", "몰려"), [("crowd_shouting.ogg", 0.0, 0.22, 0, 2.5)]),
    (("통보", "명령", "왕명", "독촉"), [("thud_soft.ogg", 0.0, 0.6)]),
]
MIN_GAP = 2.6          # 효과음 사이 최소 간격(초)
OUTDOOR = {"river_camp", "mountain_pass", "fortress_wall", "village_road", "sea_battle", "field", "street", "desert_rails", "prehistoric"}
SAD = {"sunset", "dawn", "golden", "dream"}


def bed_for(scene):
    st, md = scene.get("set"), scene.get("mood")
    if str(st).startswith("map"):
        return None, 0
    if st in OUTDOOR:
        if md == "night" and st in ("river_camp", "mountain_pass"):
            return "bed_rain_loop.ogg", 0.10
        return "bed_outdoor_loop.ogg", 0.08
    if md == "night":
        return "bed_fire.wav", 0.07
    return None, 0


def autospot(plan, words):
    ev, last = [], -99.0
    sent_used = set()
    for i, w in enumerate(words):
        tok = w["w"]
        nxt = words[i + 1]["w"] if i + 1 < len(words) else ""
        for keys, hits in RULES:
            if any(k in tok or (" " in k and k in tok + " " + nxt) for k in keys):
                t = float(w["s"])
                if t - last < MIN_GAP or w.get("sent") in sent_used:
                    break
                for h in hits:
                    f, dt, g = h[0], h[1], h[2]
                    loops = h[3] if len(h) > 3 else 0
                    dur = h[4] if len(h) > 4 else None
                    ev.append({"t": round(t + dt, 3), "sfx": f, "gain": g, "loops": loops, "dur": dur, "why": tok})
                last = t; sent_used.add(w.get("sent"))
                break
    # 장면 전환 휙(약하게)
    for prev, s in zip(plan["scenes"], plan["scenes"][1:]):
        if s.get("set") == prev.get("set"):
            continue
        t = float(s["t0"])
        if all(abs(t - e["t"]) > 0.6 for e in ev):
            ev.append({"t": round(max(0, t - 0.08), 3), "sfx": "swish_soft.wav", "gain": 0.25, "loops": 0, "dur": None, "why": "scene:" + s["id"]})
    ev.sort(key=lambda e: e["t"])
    return ev


def music_segments(plan, dur, ep):
    T = sorted(f for f in os.listdir(os.path.join(AUD, "music")) if f.startswith("T_"))
    S = sorted(f for f in os.listdir(os.path.join(AUD, "music")) if f.startswith("S_"))
    segs = []
    for s in plan["scenes"]:
        c = "S" if s.get("mood") in SAD else "T"
        if not segs or segs[-1][1] != c:
            segs.append([float(s["t0"]), c])
    merged = []
    for i, (t0, c) in enumerate(segs):
        t1 = segs[i + 1][0] if i + 1 < len(segs) else dur
        if merged and (t1 - t0 < 15 or merged[-1][1] == c):
            continue
        merged.append([t0, c])
    out = []
    for t0, c in merged:
        if out and out[-1][1] == c:
            continue
        out.append([t0, c])
    out[0][0] = 0.0
    ti, si, res = ep, ep, []
    for i, (t0, c) in enumerate(out):
        t1 = out[i + 1][0] if i + 1 < len(out) else dur
        if c == "T":
            f = T[ti % len(T)]; ti += 1
        else:
            f = S[si % len(S)]; si += 1
        res.append((t0, t1, f))
    return res


def bed_segments(plan, dur):
    res = []
    for i, s in enumerate(plan["scenes"]):
        f, g = bed_for(s)
        t0 = float(s["t0"]); t1 = float(plan["scenes"][i + 1]["t0"]) if i + 1 < len(plan["scenes"]) else dur
        if f and res and res[-1][2] == f and abs(res[-1][1] - t0) < 0.01:
            res[-1][1] = t1
        elif f:
            res.append([t0, t1, f, g])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj")
    ap.add_argument("--video", default="final.mp4")
    ap.add_argument("--out", default="final_sfx.mp4")
    ap.add_argument("--ep", type=int, default=1)
    ap.add_argument("--plan", default=None)
    ap.add_argument("--music", type=float, default=0.30, help="음악 크기(덕킹 전)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    P = os.path.abspath(a.proj)
    plan = json.load(open(os.path.join(P, "plan.json"), encoding="utf-8"))
    words = json.load(open(os.path.join(P, "words.json"), encoding="utf-8"))
    dur = float(plan["duration"])
    if a.plan:
        ev = json.load(open(os.path.join(P, a.plan) if not os.path.isabs(a.plan) else a.plan, encoding="utf-8"))
    else:
        ev = autospot(plan, words)
        json.dump(ev, open(os.path.join(P, "sfx_plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    mus = music_segments(plan, dur, a.ep)
    beds = bed_segments(plan, dur)
    print("효과음 %d개 / 음악 %d구간 / 배경음 %d구간" % (len(ev), len(mus), len(beds)))
    for e in ev:
        print("  %6.2fs  %-22s %.2f  (%s)" % (e["t"], e["sfx"], e["gain"], e["why"]))
    for t0, t1, f in mus:
        print("  음악 %5.1f-%5.1f %s" % (t0, t1, f))
    for t0, t1, f, g in beds:
        print("  배경 %5.1f-%5.1f %s" % (t0, t1, f))
    if a.dry:
        return

    vid = os.path.join(P, a.video)
    args = [FF, "-v", "error", "-y", "-i", vid]
    fil, k = [], 0
    mlab, blab, slab = [], [], []
    XF = 1.5
    for i, (t0, t1, f) in enumerate(mus):
        k += 1; args += ["-stream_loop", "-1", "-i", os.path.join(AUD, "music", f)]
        L = (t1 - t0) + (XF if i + 1 < len(mus) else 0)
        fin = 0.3 if i == 0 else XF          # 첫 프레임부터 들리게
        fo = 2.5 if i + 1 == len(mus) else XF
        fil.append("[%d:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=%.2f,afade=t=out:st=%.3f:d=%.2f,adelay=%d|%d[m%d]" % (k, L, fin, max(0, L - fo), fo, int(t0 * 1000), int(t0 * 1000), i))
        mlab.append("[m%d]" % i)
    for i, (t0, t1, f, g) in enumerate(beds):
        k += 1; args += ["-stream_loop", "-1", "-i", os.path.join(AUD, "sfx", f)]
        L = t1 - t0 + 0.6
        fil.append("[%d:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=%.2f,afade=t=out:st=%.3f:d=0.6,volume=%.3f,adelay=%d|%d[b%d]" % (k, L, 0.05 if t0 == 0 else 0.5, max(0, L - 0.6), g, int(t0 * 1000), int(t0 * 1000), i))
        blab.append("[b%d]" % i)
    for i, e in enumerate(ev):
        k += 1
        loops = int(e.get("loops") or 0)
        if loops:
            args += ["-stream_loop", str(loops)]
        args += ["-i", os.path.join(AUD, "sfx", e["sfx"])]
        trim = ",atrim=0:%.3f,afade=t=out:st=%.3f:d=0.5" % (e["dur"], max(0, e["dur"] - 0.5)) if e.get("dur") else ""
        fil.append("[%d:a]aformat=sample_rates=48000:channel_layouts=stereo%s,volume=%.3f,adelay=%d|%d[s%d]" % (k, trim, e["gain"], int(e["t"] * 1000), int(e["t"] * 1000), i))
        slab.append("[s%d]" % i)
    fil.append("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=3[v1][v2][v3]")
    fil.append("%samix=inputs=%d:normalize=0:duration=longest,volume=%.3f[mus]" % ("".join(mlab), len(mlab), a.music))
    fil.append("[mus][v1]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=500:makeup=1[mduck]")
    extra = "".join(blab + slab)
    n_ex = len(blab) + len(slab)
    if n_ex:
        fil.append("%samix=inputs=%d:normalize=0:duration=longest[fx]" % (extra, n_ex))
        fil.append("[fx][v2]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300:makeup=1[fxd]")
        fil.append("[v3][mduck][fxd]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    else:
        fil.append("[v3][mduck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    out = os.path.join(P, a.out)
    args += ["-filter_complex", ";".join(fil), "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "%.3f" % dur, "-movflags", "+faststart", out]
    subprocess.run(args, check=True)

    # 크레딧(실제로 쓴 CC BY 음원만)
    names = {"T_decisions.mp3": "Decisions", "T_five-armies.mp3": "Five Armies", "T_temple-of-the-manes.mp3": "Temple of the Manes",
             "S_heartbreaking.mp3": "Heartbreaking", "S_teller-of-the-tales.mp3": "Teller of the Tales"}
    lines = ["[음악·효과음 출처]"]
    for f in sorted({m[2] for m in mus}):
        lines += ['"%s" Kevin MacLeod (incompetech.com)' % names.get(f, f), "Licensed under Creative Commons: By Attribution 4.0 License", "http://creativecommons.org/licenses/by/4.0/"]
    used = {e["sfx"] for e in ev}
    if used & {"horse_gallop_ground.mp3", "horse_gallop_grass.mp3"}:
        lines.append('Horse gallop SFX: adaptation by congusbongus (opengameart.org/content/horse-gallop-on-different-surfaces), CC BY 4.0')
    lines.append("기타 효과음: Kenney, artisticdude, StarNinjas, rubberduck, AntumDeluge, Kresiek (CC0)")
    lines.append("변경: 발췌·페이드·음량 조절(덕킹)·영상에 맞춘 편집")
    open(os.path.join(P, "audio_credits.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("OUT", out)
    print("CREDITS", os.path.join(P, "audio_credits.txt"))


if __name__ == "__main__":
    main()
