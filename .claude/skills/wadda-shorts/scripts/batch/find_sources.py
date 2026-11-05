# 인물별 소스 영상 찾기 (Aside REPL 없이 yt-dlp만으로) -> sources.json
#   python find_sources.py 김원훈 이수지 ...
#   검색 -> (제목에 이름, 2~50분) -> 한국어 자동자막 json3의 [웃음]/[박수] 개수로 정렬 -> 상위 8개 + 실제 댓글
import json, os, re, subprocess, sys, shutil, glob
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(__file__))
SUB = os.path.join(B, "subs"); os.makedirs(SUB, exist_ok=True)


def ytdlp():
    p = shutil.which("yt-dlp")
    if p:
        return p
    hits = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\WinGet\Packages\yt-dlp.yt-dlp*\yt-dlp.exe"))
    return hits[0] if hits else sys.exit("yt-dlp 필요: pip install yt-dlp 또는 winget install yt-dlp.yt-dlp")


Y = ytdlp()
env = dict(os.environ, TEMP=SUB, TMP=SUB, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
LAUGH = re.compile(r"\[(웃음|박수|폭소|웃는 소리|환호|웃음소리)\]")
QUERIES = ["{} 레전드", "{} 빵터짐", "{} 라디오스타", "{} 아는형님", "{} 웃긴 장면", "{} 토크"]


def run(args):
    return subprocess.run([Y, "--encoding", "utf-8"] + args, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


out = json.load(open(os.path.join(B, "sources.json"), encoding="utf-8")) if os.path.exists(os.path.join(B, "sources.json")) else {}
for person in sys.argv[1:]:
    seen, cands = set(), []
    for q in QUERIES:
        txt = run(["--flat-playlist", "--print", "%(id)s\t%(duration)s\t%(view_count)s\t%(channel)s\t%(title)s", "ytsearch15:" + q.format(person)])
        for line in txt.splitlines():
            p = line.split("\t")
            if len(p) < 5 or p[0] in seen:
                continue
            seen.add(p[0])
            try:
                dur = float(p[1])
            except ValueError:
                continue
            if person in p[4] and 120 <= dur <= 3000 and "와따마" not in p[3]:
                cands.append({"id": p[0], "dur": dur, "views": p[2], "channel": p[3], "title": p[4]})
    for c in cands:
        f = os.path.join(SUB, c["id"] + ".ko.json3")
        if not os.path.exists(f):
            run(["--skip-download", "--write-auto-subs", "--sub-langs", "ko", "--sub-format", "json3", "-o", os.path.join(SUB, c["id"]), "https://www.youtube.com/watch?v=" + c["id"]])
        c["laugh"] = len(LAUGH.findall(open(f, encoding="utf-8").read())) if os.path.exists(f) else 0
    cands.sort(key=lambda c: -c["laugh"])
    top = [c for c in cands if c["laugh"] >= 10][:8]
    for c in top:   # 실제 댓글 (6~32자)
        j = run(["--skip-download", "--write-comments", "--extractor-args", "youtube:max_comments=40,all,0,0", "--print", "%(comments)j", "https://www.youtube.com/watch?v=" + c["id"]])
        try:
            cm = [x.get("text", "").replace("\n", " ").strip() for x in json.loads(j.strip().splitlines()[-1])]
        except Exception:
            cm = []
        c["comments"] = [t for t in cm if 6 <= len(t) <= 32 and not re.search(r"http|@|#", t)][:12]
    out[person] = top
    print(person, [(c["id"], c["laugh"], c["title"][:30]) for c in top])
json.dump(out, open(os.path.join(B, "sources.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
