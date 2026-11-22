# 20편 프로젝트 생성 -> 렌더 -> 다운로드\어랏 저장 -> 쇼츠 일기장 갱신
import json, os, re, sys, datetime, subprocess
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(os.path.expanduser("~"), "Downloads", "어랏")
EDITOR = os.path.dirname(B)   # scripts/ (wadda_edit.py 위치)
sys.path.insert(0, EDITOR)
import wadda_edit  # noqa
import registry

S = json.load(open(os.path.join(B, "segments.json"), encoding="utf-8"))
T = json.load(open(os.path.join(B, "titles.json"), encoding="utf-8"))
SRC = json.load(open(os.path.join(B, "sources.json"), encoding="utf-8"))
only = sys.argv[1:]  # 예: 김원훈 1


SURNAMES = set("김이박최정강조윤장임한오서신권황안송류홍전고문양손배백허유남심노하곽성차주우구민진나지엄채원천방공현함변염여추도석선설마길위표명기반왕금옥육인맹제모탁국어은편용")
NAMES = set("김원훈 이수지 장도연 박영진 허경환 김준호 이상준 엄지윤 김두영 김용명 박경호 탁재훈 유재석 강호동 서장훈 김구라 이수근 김희철 신동엽 이경규 박명수 정준하 하하 양세형 양세찬 조세호 남창희 김숙 송은이 박나래 장동민 유세윤 김대희 김지민 황제성 강재준 이은형 홍현희 제이쓴 김종민 이용진 이진호 곽범 정성호 김민경 이국주 안영미 신봉선 김신영 문세윤 김준현 유민상 이상민 임원희 최민수 김영철 이수만 김창옥 정형돈 데프콘 노홍철 전현무 김성주 붐 문상훈 조진세 김혜선 오나미 박성광 이세영 박휘순 홍인규 김병만 류승수 손석구 송중기 제니 지드래곤".split())
try:
    NAMES |= {r["video"].rsplit(" ", 1)[0] for r in registry.load() if r.get("video")}
except Exception:
    pass
for _p, _ss in SRC.items():
    NAMES.add(_p)
    for _s in _ss:
        for _w in re.findall(r"[가-힣]{3}", re.sub(r"[^가-힣 ]", " ", _s.get("title") or "")):
            if _w[0] in SURNAMES:
                NAMES.add(_w)


def clean_comments(person, cm):
    """댓글 줄 규칙: 키워드(인물 이름)나 다른 연예인 이름이 들어간 댓글은 쓰지 않는다.
    댓글 속 이름은 화면 속 인물과 다른 경우가 대부분이라서."""
    def low_quality(c):
        # 외국어, 타임스탬프, 욕설·비난, 화면 불평, 외모·체형 언급, 별명(키워드) -> 쓰지 않음
        nick = T.get(person, {}).get("nick", []) if isinstance(T, dict) else []
        if any(n in c for n in nick) or re.search(r"뚱땡|뚱뚱|돼지|머리크기|살은|살쪘|못생|거슬림|노잼|재미도없|스쿼드|몇살|\d+살", c):
            return True
        return bool(re.search(r"[A-Za-z]{4,}|[\u3040-\u30ff\u4e00-\u9fff]|\d{1,2}:\d{2}|ㅅㅂ|씨발|존나|ㅈㄴ|개병|짜증|않아와|안 나와|예쁜 여자|잘생긴 남자", c))

    def looks_named(c):
        if low_quality(c):
            return True
        # 2글자 + 이/아/야 호격·주격 (자윤이, 경호야) 와 두 명 이상 나열(박군 한영, 유미 유리)
        if re.search(r"(^|\s)[가-힣]{2}(이|아|야)(\s|$|[^가-힣])", c) and not re.search(r"(^|\s)(진짜|정말|너무|이거|그거|저거|우리|오늘|여기|거기)(이|아|야)", c):
            return True
        if person in c or any(n in c for n in NAMES):
            return True
        # 이름 두 글자만 쓴 경우 (경호, 두영, 용명 ...)
        if any(len(n) == 3 and n[1:] in c for n in NAMES | {person}):
            return True
        # 이름 + 호칭 (영철님, 유미누나, 은지 오빠, 수미 선생님, 원희씨, 탁형)
        if re.search(r"[가-힣]{1,2}\s?(님|누나|오빠|언니|형님|형의|형이|형은|씨|쌤|선배|선생님|옹)", c):
            return True
        # 성씨로 시작하는 세 글자 단어(+조사) = 사람 이름일 가능성 -> 제외 (예: 심자윤, 박영진이)
        for w in re.findall(r"[가-힣]+", c):
            if len(w) >= 3 and w[0] in SURNAMES and re.fullmatch(r"[가-힣]{3}(이|가|은|는|씨|님|아|야|랑|이랑|한테|의|도|만|이가|이는)?", w):
                return True
        return False
    out = [c for c in cm if not looks_named(c)]
    return out or ["ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ", "아 진짜 너무 웃기네ㅋㅋㅋ"]


def chapter(person, idx, k):
    c = S[person][idx]
    title, pop = T[person]["ch"][str(idx)]
    D = round(c["out"] - c["in"], 2)
    pad = c.get("pad", 1.0)
    c.setdefault("file", "clips/%s_%d_%d.mp4" % (c["id"], int(c["in"]), int(c["out"])))
    src = next(s for s in SRC[person] if s["id"] == c["id"])
    cm = clean_comments(person, src.get("comments") or [])
    subs = [dict(s) for s in c["subs"] if s["t0"] < D - 0.2]
    for s in subs:
        s["t1"] = min(s["t1"], D)
    # 가장 웃음이 몰린 시각 -> 팝
    L = c["laughs"] or [D - 3]
    best = max(L, key=lambda x: sum(1 for y in L if abs(y - x) <= 3))
    pat = max(0.8, min(D - 1.5, best - 0.9))
    pops = [{"at": round(pat, 2), "text": pop, "zoom": 1.22}]
    # 빈 구간에 (빵터짐ㅋㅋ) 상황 자막
    for lt in L:
        if not any(s["t0"] - 0.2 <= lt <= s["t1"] + 0.2 for s in subs) and lt + 1.2 < D:
            subs.append({"t0": round(lt, 2), "t1": round(lt + 1.2, 2), "text": "(빵터짐ㅋㅋㅋ)", "style": "paren"})
            break
    subs.sort(key=lambda s: s["t0"])
    return {"title": title, "src": os.path.join(B, c["file"]), "in": pad, "out": round(pad + D, 2), "x": 0.5, "y": 0.40, "zoom": 1.45,
            "comments": [{"at": 0, "text": cm[k % len(cm)]}, {"at": round(D / 2, 1), "text": cm[(k + 1) % len(cm)]}],
            "subs": subs, "pops": pops,
            "_src": "%s (%s)" % (src.get("channel"), src.get("title", "")[:40]), "_text": c["text"][:80]}


def diary(entry):
    p = os.path.join(OUTDIR, "쇼츠 일기장.txt")
    new = not os.path.exists(p)
    with open(p, "a", encoding="utf-8-sig" if new else "utf-8") as f:
        if new:
            f.write("■ 쇼츠 일기장 (와따마 스타일 개그 짤)\n\n")
        f.write(entry + "\n")


os.makedirs(OUTDIR, exist_ok=True)
for person in T.keys():
    idxs = [int(i) for i in T[person]["ch"].keys()]
    idxs = [i for i in range(len(S[person])) if i in idxs]          # 점수순
    nv = len(T[person]["videos"])                   # 만들 편수 = 영상 제목 개수
    groups = [idxs[v::nv] for v in range(nv)]
    for v, g in enumerate(groups, 1):
        start = T[person].get("start", 1)          # 이어 만들 때 시작 번호 (예: 6)
        name = "%s %d" % (person, v + start - 1)
        if only and name not in " ".join(only) and person not in only:
            continue
        if not only and os.path.exists(os.path.join(OUTDIR, name + ".mp4")):
            print("[건너뜀] 이미 있음", name); continue
        g = [i for i in g if os.path.exists(os.path.join(B, "clips/%s_%d_%d.mp4" % (S[person][i]["id"], int(S[person][i]["in"]), int(S[person][i]["out"]))))]
        USED = registry.load()
        g = [i for i in g if not registry.clashes(USED, S[person][i]["id"], S[person][i]["in"], S[person][i]["out"], S[person][i]["text"])]
        chs = [chapter(person, i, k) for k, i in enumerate(g)]
        proj = {"output": name + ".mp4", "chapters": chs}
        pj = os.path.join(B, "proj_%s_%d.json" % (person, v))
        json.dump(proj, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        out = os.path.join(OUTDIR, name + ".mp4")
        wadda_edit.render(pj, out)
        dur = float(subprocess.run([wadda_edit.FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = ["────────────────────────",
                 "일시: " + now,
                 "제목: " + T[person]["videos"][v - 1],
                 "파일: " + name + ".mp4 (%d분 %02d초)" % (dur // 60, dur % 60),
                 "주제: %s 웃음 터진 장면 모음 (게스트·MC 빵터진 순간 위주)" % person,
                 "영상내용:"]
        for k, ch in enumerate(chs, 1):
            lines.append("  %d) %s - %s" % (k, ch["title"], ch["_src"]))
        diary("\n".join(lines) + "\n")
        R = registry.load()
        for i, ch in zip(g, chs):
            c = S[person][i]
            registry.add(R, c["id"], c["in"], c["out"], c["text"], name, ch["title"])
        registry.save(R)
        print("[저장]", out, "%.1fs" % dur, flush=True)
