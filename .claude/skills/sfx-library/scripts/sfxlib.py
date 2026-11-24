#!/usr/bin/env python3
"""sfx-library: 실제 녹음 효과음·배경음악(라이선스 증빙 포함)을 찾고, neogul-edit에 끼우고, 출처 문구를 만든다.

  python3 sfxlib.py list [--kind sfx|music|stinger|transition] [--category money-foley]
  python3 sfxlib.py search 키워드 [--limit 20]          # id·제목·태그에서 찾기 (영문 태그 + 일부 중국어 태그)
  python3 sfxlib.py show <id>
  python3 sfxlib.py preset <이름> <출력폴더>           # neogul-edit용 wav 5종 + sfx_files.json 생성
  python3 sfxlib.py export <id,id,...> <출력폴더>       # 고른 파일 + 라이선스 + CREDITS.md 복사
  python3 sfxlib.py credits <id,id,...>                # 설명란에 붙일 출처 문구(저작자 표시 필요한 것만 + CC0 한 줄)

preset 이름: presets/*.json (기본 = basic).  표준 라이브러리 + ffmpeg 만 쓴다.
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAT = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
A = {x["id"]: x for x in CAT["assets"]}


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def row(x):
    return "%-48s %-6s %-18s %5.2fs %-10s %s" % (x["id"], x["kind"], x["category"], x.get("duration", 0), x["license"]["id"], ",".join(x.get("tags", [])[:5]))


def peak_db(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"max_volume: ([-\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else 0.0


def to_wav(src, dst, peak=-3.0, maxdur=None):
    """48kHz 스테레오 wav, 최고 레벨을 peak dBFS로 맞춘다(합성 효과음과 비슷한 크기 → rules.json 볼륨이 그대로 통함)."""
    g = peak - peak_db(src)
    af = "volume=%.2fdB" % g
    if maxdur:
        af += ",afade=t=out:st=%.2f:d=0.15" % max(0, maxdur - 0.15)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src] + (["-t", str(maxdur)] if maxdur else []) + ["-af", af, "-ar", "48000", "-ac", "2", dst]
    subprocess.run(cmd, check=True)


def credits(ids):
    need, cc0 = [], []
    for i in ids:
        x = A[i]; L = x["license"]
        if L.get("attribution_required"):
            att = [l for l in (L.get("attribution") or x["title"]).split("\n") if l.strip() and not l.startswith("Library copy")]
            need.append("· " + "\n  ".join(att))
        else:
            cc0.append(x.get("author", ""))
    out = []
    if need:
        out.append("🎵 음악·효과음 출처")
        out += need
        out.append("  (영상에 맞춰 일부 구간을 자르고 음량·페이드를 조정했습니다)")
    if cc0:
        out.append("효과음 일부: %s (CC0 퍼블릭 도메인)" % ", ".join(sorted(set(a for a in cc0 if a))))
    return "\n".join(out)


def main():
    c = sys.argv[1] if len(sys.argv) > 1 else "help"
    if c == "list":
        k, cat = arg("--kind"), arg("--category")
        for x in CAT["assets"]:
            if (not k or x["kind"] == k) and (not cat or x["category"] == cat):
                print(row(x))
    elif c == "search":
        q = sys.argv[2].lower(); n = int(arg("--limit", 20))
        hits = [x for x in CAT["assets"] if q in (x["id"] + " " + x["title"] + " " + " ".join(x.get("tags", [])) + " " + x["category"]).lower()]
        for x in hits[:n]:
            print(row(x))
        print("(%d개 중 %d개)" % (len(hits), min(n, len(hits))))
    elif c == "show":
        x = dict(A[sys.argv[2]]); print(json.dumps({k: v for k, v in x.items() if "sha" not in k}, ensure_ascii=False, indent=1))
        print("파일:", os.path.join(ROOT, x["path"]))
    elif c == "preset":
        name, out = sys.argv[2], os.path.abspath(sys.argv[3])
        P = json.load(open(os.path.join(ROOT, "presets", name + ".json"), encoding="utf-8"))
        os.makedirs(out, exist_ok=True)
        m = {}
        for key, spec in P["sfx"].items():
            x = A[spec["id"]]
            dst = os.path.join(out, "%s.wav" % key)
            to_wav(os.path.join(ROOT, x["path"]), dst, spec.get("peak", -3.0), spec.get("max"))
            m[key] = dst
        json.dump(m, open(os.path.join(out, "sfx_files.json"), "w"), ensure_ascii=False, indent=1)
        ids = [s["id"] for s in P["sfx"].values()]
        open(os.path.join(out, "CREDITS.txt"), "w", encoding="utf-8").write(credits(ids) + "\n")
        print(json.dumps(m, ensure_ascii=False, indent=1))
        print("project.json 에 \"sfx_files\": (위 내용) 을 넣으면 된다.  출처 문구:", os.path.join(out, "CREDITS.txt"))
    elif c == "export":
        ids, out = sys.argv[2].split(","), os.path.abspath(sys.argv[3])
        os.makedirs(out, exist_ok=True); lic = set()
        for i in ids:
            x = A[i]; shutil.copy2(os.path.join(ROOT, x["path"]), os.path.join(out, os.path.basename(x["path"])))
            lic.add(x["license"]["id"])
        for f in os.listdir(os.path.join(ROOT, "licenses")):
            shutil.copy2(os.path.join(ROOT, "licenses", f), out)
        open(os.path.join(out, "CREDITS.md"), "w", encoding="utf-8").write(credits(ids) + "\n")
        json.dump([{k: v for k, v in A[i].items() if "sha" not in k} for i in ids], open(os.path.join(out, "selection.json"), "w"), ensure_ascii=False, indent=1)
        print("내보냄 %d개 →" % len(ids), out)
    elif c == "credits":
        print(credits(sys.argv[2].split(",")))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
