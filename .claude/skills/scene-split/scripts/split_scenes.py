#!/usr/bin/env python3
"""PySceneDetect로 컷 찾기 → scenes.csv / stats.json / scenes_sheet.png / clips/."""
import argparse, json, os, statistics, subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--out", default="scenes_out")
    ap.add_argument("--mode", choices=["content", "adaptive", "threshold"], default="content")
    ap.add_argument("--threshold", type=float, default=27.0); ap.add_argument("--min", type=float, default=0.6)
    ap.add_argument("--split", action="store_true"); ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    from scenedetect import open_video, SceneManager, ContentDetector, AdaptiveDetector, ThresholdDetector
    os.makedirs(a.out, exist_ok=True)
    v = open_video(a.video); fps = v.frame_rate
    sm = SceneManager()
    minf = max(1, int(a.min * fps))
    det = {"content": lambda: ContentDetector(threshold=a.threshold, min_scene_len=minf),
           "adaptive": lambda: AdaptiveDetector(min_scene_len=minf),
           "threshold": lambda: ThresholdDetector(threshold=12, min_scene_len=minf)}[a.mode]()
    sm.add_detector(det)
    sm.detect_scenes(v, show_progress=False)
    scenes = sm.get_scene_list()
    if not scenes:
        dur = v.duration.get_seconds(); scenes_s = [(0.0, dur)]
    else:
        sec = lambda t: t.seconds if hasattr(t, "seconds") else t.get_seconds()
        scenes_s = [(sec(s), sec(e)) for s, e in scenes]
    with open(os.path.join(a.out, "scenes.csv"), "w", encoding="utf-8") as f:
        f.write("장면,시작,끝,길이\n")
        for i, (s, e) in enumerate(scenes_s):
            f.write("%d,%.2f,%.2f,%.2f\n" % (i + 1, s, e, e - s))
    lens = sorted(e - s for s, e in scenes_s); total = scenes_s[-1][1]
    q = lambda p: lens[min(len(lens) - 1, int(len(lens) * p))]
    stats = {"video": a.video, "duration": round(total, 2), "scenes": len(scenes_s), "cuts_per_min": round((len(scenes_s) - 1) / total * 60, 2),
             "len_median": round(statistics.median(lens), 2), "len_p25": round(q(0.25), 2), "len_p75": round(q(0.75), 2),
             "over_8s": [{"scene": i + 1, "start": round(s, 1), "len": round(e - s, 1)} for i, (s, e) in enumerate(scenes_s) if e - s > 8]}
    json.dump(stats, open(os.path.join(a.out, "stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[scenes] %d장면, 분당 컷 %.2f, 장면 길이 중앙값 %.1f초, 8초 넘는 장면 %d개" % (stats["scenes"], stats["cuts_per_min"], stats["len_median"], len(stats["over_8s"])))
    if a.sheet:
        n = min(len(scenes_s), 48); cols = 6; args, fl = [], []
        for i, (s, e) in enumerate(scenes_s[:n]):
            args += ["-ss", "%.3f" % ((s + e) / 2), "-i", a.video]
            fl.append("[%d:v]scale=320:-2,drawtext=text='#%d %.1fs':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6[v%d]" % (i, i + 1, e - s, i))
        lay = "|".join("%s_%s" % ("+".join(["w0"] * (i % cols)) or "0", "+".join(["h0"] * (i // cols)) or "0") for i in range(n))
        fl.append("".join("[v%d]" % i for i in range(n)) + ("xstack=inputs=%d:layout=%s:fill=black" % (n, lay) if n > 1 else "null"))
        subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-filter_complex", ";".join(fl), "-frames:v", "1", os.path.join(a.out, "scenes_sheet.png")], check=True)
        print("[sheet] scenes_sheet.png (%d장면)" % n)
    if a.split:
        cd = os.path.join(a.out, "clips"); os.makedirs(cd, exist_ok=True)
        for i, (s, e) in enumerate(scenes_s):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % s, "-to", "%.3f" % e, "-i", a.video, "-c:v", "libx264", "-crf", "18",
                            "-c:a", "aac", os.path.join(cd, "scene_%03d.mp4" % (i + 1))], check=True)
        print("[split] clips/ %d개" % len(scenes_s))

if __name__ == "__main__":
    main()
