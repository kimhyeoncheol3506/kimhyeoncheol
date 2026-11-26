
# ---------------------------------------------------------------- 가락시장 품목 시세 편 공통 생성기 (topic.json 하나로 대본·화면 데이터)
import csv, collections
def _bat(w):
    c = w.strip()[-1:] if w.strip() else ""
    return bool(c) and "가" <= c <= "힣" and (ord(c) - 0xAC00) % 28 != 0
def J(w, a, b): return w + (a if _bat(w) else b)          # J("감귤","은","는") → 감귤은
CSV = "/home/user/kimhyeoncheol/video_projects/가락시장_시리즈/00_data/garak.csv"
THIS, LAST = ("2026.11.12", "2026.11.26"), ("2025.11.12", "2025.11.26")
kgof = lambda u: float(re.match(r"([\d.]+)", u).group(1)) if re.match(r"[\d.]+키로", u) else None
R = collections.defaultdict(list)
for r in csv.reader(open(CSV, encoding="utf-8")):
    d, _, it, u, g, p = r; p = int(p.replace(",", ""))
    if p <= 0 or not ("11.12" <= d[5:] <= "11.26"): continue
    y = d[:4]; R[("this" if y == "2026" else "last" if y == "2025" else y, it, u, g)].append((d, p))
def st_(y, it, u, g):
    v = sorted(set(R.get((y, it, u, g), [])));
    if not v or len({p for _, p in v}) < min(3, len(v)): return None      # 값이 매일 같으면(갱신 안 된 기록) 쓰지 않음
    return dict(avg=round(sum(p for _, p in v) / len(v)), days=len(v), daily=v, lo=min(v, key=lambda x: x[1]), hi=max(v, key=lambda x: x[1]))
GR = ["특", "상", "중", "하"]
ITEMS = CFG["items"]                     # [{name: 화면 이름, kamis: KAMIS 품목명}]
def main_unit(it):
    c = collections.Counter(u for (y, i, u, g) in R if y == "this" and i == it and kgof(u))
    best = None
    for u, _ in c.most_common():
        n = (st_("this", it, u, "상") or {}).get("days", 0)
        n = n + (100 if kgof(u) > 1 else 0)
        if best is None or n > best[1]: best = (u, n)
    return best[0] if best else None
INFO = {}
for x in ITEMS:
    it = x["kamis"]; u = main_unit(it)
    if not u: continue
    t, l = st_("this", it, u, "상"), st_("last", it, u, "상")
    INFO[x["name"]] = dict(kamis=it, unit=u, kg=kgof(u), t=t, l=l if (l and l["days"] >= 5) else None,
                           grades={g: st_("this", it, u, g) for g in GR}, lgrades={g: st_("last", it, u, g) for g in GR},
                           units={uu: st_("this", it, uu, "상") for (y, i, uu, g) in R if y == "this" and i == it and g == "상" and kgof(uu)})
NAMES = [n for n in (x["name"] for x in ITEMS) if n in INFO and INFO[n]["t"]]
M = NAMES[0]; MI = INFO[M]
perkg = lambda n: INFO[n]["t"]["avg"] / INFO[n]["kg"]
yoy = lambda n: round((INFO[n]["t"]["avg"] - INFO[n]["l"]["avg"]) / INFO[n]["l"]["avg"] * 100) if INFO[n]["l"] else None
uname = lambda u: u.replace("키로", "kg ").strip()
r1000 = lambda v: (lambda r: (f"{r // 10}만" if r >= 10 else "") + (f" {r % 10}천" if r % 10 else ""))(int(v / 1000 + 0.5)).strip()
r100 = lambda v: int(round(v, -2))
md = lambda d: f"{int(d[5:7])}/{int(d[8:10])}"
SUBFIX += [("두 주", "2주"), ("세 가지", "3가지"), ("다섯 가지", "5가지"), ("일 킬로그램", "1kg"), ("킬로그램", "kg"), ("특품", "특품"), ("열한 월", "11월")]
SUBFIX += CFG.get("subfix", [])
K_ = lambda u: f"{{kd:{kgof(u):g}}}" if kgof(u) % 1 else f"{{k:{int(kgof(u))}}}"   # 상자 무게 토큰
mt, ml = MI["t"], MI["l"]; MY = yoy(M)
# ---- 1 오프닝
hook_cards = [dict(sig=["q", 1], kick=f"가락시장 경락가 · {M} {uname(MI['unit'])} 상품", photo=CFG["photo_main"], big=f"{mt['avg']:,}원", bigsize=130,
                   lines=[f"kg당 약 {r100(perkg(M)):,}원" + (f" · 작년보다 {MY:+d}%" if MY is not None else "")], top=150)]
hook_s = [S(CFG["hook_q"], q=1),
          S(f"가락시장 경락가로 {M} {K_(MI['unit'])} 상자 상품이 최근 두 주 평균 {{e:{mt['avg']}}}입니다.", q=1),
          S(f"킬로그램으로 나누면 약 {{e:{r100(perkg(M))}}}이에요." + (f" 작년 같은 때보다 약 {{pc:{abs(MY)}}} {'올랐' if MY > 0 else '내렸'}습니다." if MY is not None else ""), q=1)]
if len(NAMES) > 1:
    cheap = min(NAMES, key=perkg); dear = max(NAMES, key=perkg)
    hook_cards.append(dict(sig=["c", 1], kick="kg당 상품 경락가 · 최근 2주", vs=[(f"가장 비싼 {dear}", [f"약 {r100(perkg(dear)):,}원"]), (f"가장 싼 {cheap}", [f"약 {r100(perkg(cheap)):,}원"])], top=200))
    hook_s.append(S(f"같은 {J(CFG['group'], '이라도', '라도')} 킬로그램당 {J(dear, '은', '는')} 약 {{e:{r100(perkg(dear))}}}, {J(cheap, '은', '는')} 약 {{e:{r100(perkg(cheap))}}}으로 차이가 큽니다.", c=1))
hook_cards.append(dict(sig=["agenda", 1], kick="오늘 정리", lines=CFG["agenda"], size=48, top=200))
hook_s.append(S("오늘은 " + ", ".join(CFG["agenda_tts"]) + "까지 봅니다.", agenda=1))
SECS = [dict(id="hook", kind="calc", name="오프닝", vis=dict(cards=hook_cards), sentences=hook_s)]
# ---- 2 데이터 설명
SECS.append(dict(id="title", kind="title", name="데이터 설명", vis=dict(cards=[
    dict(sig=["src", 1], kick="SOURCE · 가락시장 경락가", photo=CFG["photo_src"], lines=["KAMIS 도매가격(가락시장 경락가격)", "<span style='color:#8C919B;font-size:36px'>2026년 11/12~11/26 일별 평균가 · 작년 같은 기간과 비교</span>"], top=200),
    dict(sig=["warn", 1], kick="꼭 알아 두세요 ①", big="경락가 ≠ 가게 값", bigsize=110, lines=["새벽 경매 도매 낙찰가"], top=260),
    dict(sig=["warn", 2], kick="꼭 알아 두세요 ②", big="상자 단위 값", bigsize=110, lines=["kg당 값은 상자 무게로 나눈 계산"], top=260),
    dict(sig=["warn", 3], kick="꼭 알아 두세요 ③", big="작년 값은 있는 것만", bigsize=100, lines=["작년 경매 기록이 5일 미만이면 비교 안 함"], top=260)]), sentences=[
    S("가격은 한국농수산식품유통공사 KAMIS가 공개하는 가락시장 경락가격, 새벽 경매의 도매 낙찰가예요.", src=1),
    S("올해 십일월 십이일부터 이십육일까지 하루 평균가를 다시 평균 냈고, 작년 같은 기간과 비교했습니다.", src=1),
    S("세 가지를 먼저 알아 두세요.", warn=0),
    S("첫째, 경락가는 도매가라서 동네 가게에서 사는 값과 다릅니다.", warn=1),
    S("둘째, 경매는 상자 단위라서, 킬로그램당 값은 상자 무게로 나눠 계산했어요.", warn=2),
    S("셋째, 작년 경매 기록이 닷새가 안 되는 품목은 작년과 비교하지 않았습니다.", warn=3)]))
SUBFIX += [("십일월 십이일부터 이십육일", "11월 12일부터 26일")]
# ---- 2b 왜 가락시장 경락가인가
SECS.append(dict(id="why", kind="calc", name="왜 가락시장 경락가를 보나", vis=dict(cards=[
    dict(sig=["y", 1], kick="가락시장 (서울신문 2025-06-16)", big="서울 수요의 55%", bigsize=110, lines=["전국 33개 공영도매시장 거래량의 33%"], top=250),
    dict(sig=["y", 2], kick="경락가", big="가게 값의 출발점", bigsize=110, lines=["새벽 경매 낙찰가 → 중도매인 → 가게"], top=250)]), sentences=[
    S("왜 가락시장 경락가를 볼까요?", y=0),
    S("서울신문 보도로는 서울에서 소비되는 농산물의 오십오 퍼센트, 전국 공영도매시장 거래량의 삼십삼 퍼센트가 가락시장을 거쳐요.", y=1),
    S("여기서 새벽에 정해진 경매 가격이 중도매인과 가게를 거쳐 우리가 사는 값의 출발점이 됩니다.", y=2),
    S("그래서 경락가를 알면, 가게 값이 비싼지 싼지 가늠하는 기준이 생겨요.".replace("그래서 ", "결국 "), y=2)]))
SUBFIX += [("오십오 퍼센트", "55%"), ("삼십삼 퍼센트", "33%")]
CFG.setdefault("sources", []).append("서울신문 2025-06-16 '가락시장 40년' (서울 수요 55%·전국 33%) https://m.seoul.co.kr/news/2025/06/16/20250616002003")
# ---- 3 일별 흐름
dl = mt["daily"]; ldl = ml["daily"] if ml and ml["days"] >= 5 else None
lines = [dict(name="올해", c="#F1D9A0", p=[p for _, p in dl])] + ([dict(name="작년", c="#8C919B", p=[p for _, p in ldl][:len(dl)] + [None] * max(0, len(dl) - len(ldl)))] if ldl else [])
lines = lines[::-1] if ldl else lines
vals = [p for l in lines for p in l["p"] if p]; lo_, hi_ = min(vals), max(vals); step = max(1000, int(round((hi_ - lo_) / 4, -3)) or 1000)
ymin = max(0, int(lo_ // step) * step - step); ymax = int(hi_ // step) * step + 2 * step
rc = [["line", 0 if not ldl else 1, f"올해 · {M} 상품", [f"2주 평균 {mt['avg']:,}원", f"가장 높은 날 {md(mt['hi'][0])} {mt['hi'][1]:,}원", f"가장 낮은 날 {md(mt['lo'][0])} {mt['lo'][1]:,}원"]]]
fs = [S(f"{M} 값이 두 주 동안 어떻게 움직였는지 볼게요.", chart=1)]
if ldl:
    rc.insert(0, ["line", 0, f"작년 · {M} 상품", [f"같은 기간 평균 {ml['avg']:,}원", f"경매 기록 {ml['days']}일"]])
    fs.append(S(f"작년 같은 기간 평균은 {{e:{ml['avg']}}}이었어요.", line=0))
fs += [S(f"올해는 평균 {{e:{mt['avg']}}}. 가장 높은 날은 {{e:{mt['hi'][1]}}}, 가장 낮은 날은 {{e:{mt['lo'][1]}}}이었습니다.", line=1 if ldl else 0),
       S(f"하루 사이에도 최고와 최저가 약 {{pc:{round((mt['hi'][1] - mt['lo'][1]) / mt['avg'] * 100)}}} 차이가 나요.", end=1),
       S("따라서 하루 값보다 두 주 평균으로 보는 게 정확합니다.", end=1)]
SECS.append(dict(id="flow", kind="flow", name=f"{M} 값, 두 주 흐름", vis=dict(title=f"가락시장 {M} {uname(MI['unit'])} 상품 경락가 · 일별", x=[md(d) for d, _ in dl], ymin=ymin, ymax=ymax, step=step, lines=lines, rc=rc), sentences=fs))
# ---- 4 등급별
G = MI["grades"]; LG = MI["lgrades"]; gs = [g for g in GR if G.get(g)]
rows = [[f"{g}품", f"경매 {G[g]['days']}일", [(f"{G[g]['avg']:,}원", ""), (f"약 {r100(G[g]['avg'] / MI['kg']):,}원", ""), ((f"{(G[g]['avg'] - LG[g]['avg']) / LG[g]['avg'] * 100:+.0f}%" if LG.get(g) and LG[g]['days'] >= 5 else "-"), "")]] for g in gs]
gsent = [S(f"같은 {J(M, '이라도', '라도')} 등급에 따라 값이 크게 달라요.")]
if G.get("특") and G.get("하"):
    RT = round(G["특"]["avg"] / G["하"]["avg"], 1); SUBFIX.append((f"{dec(str(RT))}배", f"{RT:g}배"))
    gsent.append(S(f"특품 한 상자는 평균 {{e:{G['특']['avg']}}}, 하품은 {{e:{G['하']['avg']}}}. 약 {dec(str(RT))}배 차이입니다.", row=0))
for i, g in enumerate(gs):
    if g in ("상", "중"): gsent.append(S(f"{g}품은 {{e:{G[g]['avg']}}}, 킬로그램당 약 {{e:{r100(G[g]['avg'] / MI['kg'])}}}이에요.", row=i))
gsent.append(S("선물용이라면 특품이나 상품, 집에서 먹을 거라면 중품만으로도 충분하다는 분이 많죠. 등급은 크기와 모양, 흠이 기준이에요.".replace("선물용이라면", "선물용이면"), foot=1))
SECS.append(dict(id="grade", kind="table", name="등급별 값", vis=dict(kick=f"{M} {uname(MI['unit'])} · 등급별 경락가 · 최근 2주 평균", head0="등급 · 경매일", head=["상자당", "kg당", "작년 대비"], rows=rows, foot="kg당 = 상자 값 ÷ 상자 무게 · 작년 기록 5일 미만은 '-'"), sentences=gsent))
# ---- 5 상자 크기
US = {u: s for u, s in MI["units"].items() if s and s["days"] >= 3}
ul = sorted(US, key=kgof)
if len(US) >= 2 and abs((US[ul[0]]["avg"] / kgof(ul[0]) - US[ul[-1]]["avg"] / kgof(ul[-1])) / (US[ul[-1]]["avg"] / kgof(ul[-1]))) >= 0.05:
    a, b = ul[0], ul[-1]; pa, pb = US[a]["avg"] / kgof(a), US[b]["avg"] / kgof(b)
    SECS.append(dict(id="size", kind="calc", name="상자 크기별 kg당 값", vis=dict(cards=[
        dict(sig=["u", 1], kick=f"{M} 상품 · 상자 크기별", vs=[(f"{uname(a)} 상자", [f"{US[a]['avg']:,}원", f"kg당 약 {r100(pa):,}원"]), (f"{uname(b)} 상자", [f"{US[b]['avg']:,}원", f"kg당 약 {r100(pb):,}원"])], top=200),
        dict(sig=["u", 2], kick="작은 상자 vs 큰 상자", big=f"kg당 {abs(round((pa - pb) / pb * 100))}% {'비쌈' if pa > pb else '쌈'}", bigsize=110, lines=[f"{uname(a)} 상자가 {uname(b)} 상자보다"], top=260)]), sentences=[
        S(f"상자 크기에 따라서도 킬로그램당 값이 달라요.", u=1),
        S(f"상품 기준 {K_(a)} 상자는 평균 {{e:{US[a]['avg']}}}, {K_(b)} 상자는 {{e:{US[b]['avg']}}}입니다.", u=1),
        S(f"킬로그램당으로 바꾸면 작은 상자가 약 {{e:{r100(pa)}}}, 큰 상자가 약 {{e:{r100(pb)}}}. 작은 상자가 약 {{pc:{abs(round((pa - pb) / pb * 100))}}} {'비싸' if pa > pb else '싸'}요.", u=2),
        S("여럿이 나눌 거라면 큰 상자가, 조금만 필요하면 작은 상자가 낫겠죠.", u=2)]))
# ---- 6 품목·품종 비교
if len(NAMES) > 1:
    pr = sorted(NAMES, key=perkg)
    rows6 = [[n, uname(INFO[n]["unit"]) + " 상", [(f"{INFO[n]['t']['avg']:,}원", ""), (f"약 {r100(perkg(n)):,}원", ""), ((f"{yoy(n):+d}%" if yoy(n) is not None else "-"), "")]] for n in pr]
    s6 = [S(CFG["compare_intro"])]
    for i, n in enumerate(pr):
        y_ = yoy(n); s6.append(S(f"{J(n, '은', '는')} 킬로그램당 약 {{e:{r100(perkg(n))}}}" + (f", 작년보다 약 {{pc:{abs(y_)}}} {'올랐어요' if y_ > 0 else '내렸어요'}." if y_ is not None and y_ != 0 else "이에요."), row=i))
    SECS.append(dict(id="items", kind="table", name=CFG["compare_name"], vis=dict(kick=f"{CFG['group']}별 상품 경락가 · 최근 2주 평균 · kg당 싼 순", head0=f"{CFG['group']} · 상자", head=["상자당", "kg당", "작년 대비"], rows=rows6[:8], foot="상품 등급 · 가장 많이 거래된 상자 기준 · 작년 기록 5일 미만은 '-'"), sentences=s6[:9]))
# ---- 6b 품목별 등급 값 (주 품목 말고 최대 3개)
for j, n in enumerate([x for x in NAMES if x != M][:3]):
    I = INFO[n]; g = I["grades"]; gk = [x for x in GR if g.get(x)]
    if len(gk) < 2: continue
    top, bot = gk[0], gk[-1]; rt = round(g[top]["avg"] / g[bot]["avg"], 1); SUBFIX.append((f"{dec(str(rt))}배", f"{rt:g}배"))
    SECS.append(dict(id=f"g{j}", kind="calc", name=f"{n} 등급별 값", vis=dict(cards=[
        dict(sig=["gg", 1], kick=f"{n} {uname(I['unit'])} · 등급별 상자 값", lines=[f"{x}품 {g[x]['avg']:,}원 · kg당 약 {r100(g[x]['avg'] / I['kg']):,}원" for x in gk], size=46, top=220),
        dict(sig=["gg", 2], kick=f"{top}품 ÷ {bot}품", big=f"{rt:g}배", bigsize=160, lines=[f"같은 {n}, 같은 상자"], top=250)]), sentences=[
        S(f"{n}도 등급별로 볼게요. {K_(I['unit'])} 상자 기준이에요.", gg=1),
        S(f"{top}품은 평균 {{e:{g[top]['avg']}}}, {bot}품은 {{e:{g[bot]['avg']}}}입니다.", gg=1),
        S(f"같은 상자인데 약 {dec(str(rt))}배 차이가 나요." + (f" 상품은 킬로그램당 약 {{e:{r100(g['상']['avg'] / I['kg'])}}}이에요." if g.get("상") else ""), gg=2)]))
# ---- 6c 작년 대비 오르고 내린 것
YY = [(n, yoy(n)) for n in NAMES if yoy(n) is not None]
if len(YY) >= 2:
    YY.sort(key=lambda x: x[1]); YY = YY if len(YY) <= 10 else YY[:5] + YY[-5:]; up = [x for x in YY if x[1] > 0]; dn = [x for x in YY if x[1] < 0]
    ss = [S(f"작년 같은 기간과 비교하면 어떨까요?", bars=1)]
    if dn: ss.append(S(", ".join(f"{J(n, '은', '는')} 약 {{pc:{abs(v)}}}" for n, v in dn[:3]) + " 내렸어요.", row=0))
    if up: ss.append(S(", ".join(f"{J(n, '은', '는')} 약 {{pc:{v}}}" for n, v in up[::-1][:3]) + " 올랐습니다.", row=len(dn)))
    ss.append(S("같은 철이라도 품목마다 작황이 달라서, 오른 것과 내린 것이 갈립니다.", foot=1))
    SECS.append(dict(id="yoy", kind="pctbars", name="작년보다 오른 것·내린 것", vis=dict(kick="가락시장 상품 경락가 · 작년 같은 기간(11/12~26) 대비", rows=[(n, v, uname(INFO[n]["unit"])) for n, v in YY], foot="같은 상자·상품 등급 · 작년 기록 5일 이상만"), sentences=ss))
# ---- 6d 지난주 vs 이번 주 (11/16~21 vs 11/23~26, 상품)
def wavg(n, a, b):
    v = [p for d, p in INFO[n]["t"]["daily"] if a <= d <= b]; return (sum(v) / len(v), len(v)) if v else (None, 0)
WK = []
for n in NAMES:
    (a1, c1), (a2, c2) = wavg(n, "2026.11.16", "2026.11.21"), wavg(n, "2026.11.23", "2026.11.26")
    if c1 >= 3 and c2 >= 2: WK.append((n, round((a2 - a1) / a1 * 100), a1, a2))
if WK:
    WK.sort(key=lambda x: x[1]); WK = WK if len(WK) <= 8 else WK[:4] + WK[-4:]; w0 = WK[0]; w1 = WK[-1]
    ss = [S("이번엔 가장 최근 흐름이에요. 지난주와 이번 주를 비교했습니다.", bars=1)]
    for i, (n, pc, a1, a2) in enumerate(WK[:2] + WK[-2:] if len(WK) > 4 else WK):
        ss.append(S(f"{n} 상품은 지난주 평균 약 {{e:{r100(a1)}}}에서 이번 주 약 {{e:{r100(a2)}}}" + ("으로 거의 그대로예요." if pc == 0 else f", 약 {{pc:{abs(pc)}}} {'올랐어요' if pc > 0 else '내렸어요'}."), row=i))
    ss.append(S("이번 주는 아직 며칠 치라, 주말까지 더 지켜봐야 합니다.", foot=1))
    SECS.append(dict(id="week", kind="pctbars", name="지난주보다 이번 주", vis=dict(kick="가락시장 상품 경락가 · 지난주(11/16~21) → 이번 주(11/23~26)", rows=[(n, pc, f"{r100(a1):,}→{r100(a2):,}원") for n, pc, a1, a2 in WK], foot="이번 주는 11/23~26 경매분 · 상자당 평균"), sentences=ss))
# ---- 7 주제별 자료(출처 있는 사실)
for k, f in enumerate(CFG.get("facts", [])):
    SECS.append(dict(id=f"fact{k}", kind="calc", name=f["name"], vis=dict(cards=[dict(sig=["f", i + 1], kick=c["kick"], big=c.get("big"), bigsize=c.get("bigsize", 110), lines=c.get("lines", []), size=c.get("size", 50), top=c.get("top", 240), photo=c.get("photo")) for i, c in enumerate(f["cards"])]),
                     sentences=[S(t, f=j) for t, j in f["sentences"]]))
# ---- 7b 5년 같은 기간 비교 (11/12~11/26)
YRS = [(y, st_(y if y not in ("2026", "2025") else {"2026": "this", "2025": "last"}[y], MI["kamis"], MI["unit"], "상")) for y in ("2020", "2021", "2022", "2023", "2024", "2025", "2026")]
YRS = [(y, v) for y, v in YRS if v and v["days"] >= 5]
if len(YRS) >= 4:
    avg5 = sum(v["avg"] for y, v in YRS[:-1]) / len(YRS[:-1]); hiY = max(YRS, key=lambda x: x[1]["avg"]); loY = min(YRS, key=lambda x: x[1]["avg"]); pc5 = round((mt["avg"] - avg5) / avg5 * 100)
    SUBFIX += [(f"{sino(int(y))}년", f"{y}년") for y, _ in YRS]
    SECS.append(dict(id="years", kind="table", name=f"{M}, 최근 {len(YRS)}년 같은 기간", vis=dict(kick=f"{M} {uname(MI['unit'])} 상품 · 해마다 11/12~11/26 평균 경락가", head0="연도 · 경매일", head=["상자당", "kg당", "올해와 차이"],
        rows=[[f"{y}년", f"{v['days']}일", [(f"{v['avg']:,}원", ""), (f"약 {r100(v['avg'] / MI['kg']):,}원", ""), (("올해" if y == "2026" else f"{(mt['avg'] - v['avg']) / v['avg'] * 100:+.0f}%"), "")]] for y, v in YRS],
        foot="같은 상자·같은 등급 · 기록 5일 미만 연도 제외 · 올해와 차이 = 올해가 그해보다 얼마나 높은지"), sentences=[
        S(f"올해 값이 비싼 걸까요, 싼 걸까요? 같은 기간을 최근 {sino(len(YRS))} 해 동안 비교해 봤어요.", row=-1),
        S(f"{sino(int(hiY[0]))}년이 {{e:{hiY[1]['avg']}}}으로 가장 높았고, {sino(int(loY[0]))}년이 {{e:{loY[1]['avg']}}}으로 가장 낮았습니다.", row=0),
        S(f"올해 {{e:{mt['avg']}}}은 앞선 해들의 평균보다 약 {{pc:{abs(pc5)}}} {'높아요' if pc5 > 0 else '낮아요'}." if pc5 else f"올해 {{e:{mt['avg']}}}은 앞선 해들의 평균과 거의 같아요.", row=len(YRS) - 1),
        S("해마다 작황과 날씨가 달라서, 한 해만 보고 비싸다 싸다 하기보다 몇 년 흐름을 같이 보는 게 좋습니다.", foot=1)]))
# ---- 8 직접 확인하는 법
SECS.append(dict(id="howto", kind="calc", name="경락가 직접 확인하는 법", vis=dict(cards=[
    dict(sig=["h", 1], kick="STEP 1", big="KAMIS 검색", bigsize=110, lines=["'KAMIS 가락시장 경락가격'"], top=260),
    dict(sig=["h", 2], kick="STEP 2", big="기간·품목 선택", bigsize=110, lines=[f"품목에서 '{MI['kamis']}' 고르기"], top=260),
    dict(sig=["h", 3], kick="STEP 3", big="상자 무게로 나누기", bigsize=100, lines=["kg당 값으로 비교"], top=260)]), sentences=[
    S("이 값은 누구나 무료로 확인할 수 있어요.", h=0),
    S("검색창에 KAMIS 가락시장 경락가격을 찾아 들어가세요.", h=1),
    S(f"기간을 고르고, 품목에서 {J(MI['kamis'], '을', '를')} 고르면 날짜별, 등급별 값이 나옵니다.", h=2),
    S("상자 값을 상자 무게로 나누면 킬로그램당 값이 나와서, 상자 크기가 달라도 비교할 수 있어요.", h=3),
    S("등급은 특, 상, 중, 하로 나뉘니, 가게에서 사는 물건과 비슷한 등급을 골라 비교하는 게 좋아요.", h=3)]))
# ---- 8b 숫자 세 개로 요약
rec = [f"{M} {uname(MI['unit'])} 상품 평균 {mt['avg']:,}원", f"kg당 약 {r100(perkg(M)):,}원"] + ([f"작년보다 {MY:+d}%"] if MY is not None else []) + ([f"kg당 가장 싼 {min(NAMES, key=perkg)}"] if len(NAMES) > 1 else [])
SECS.append(dict(id="recap", kind="calc", name="숫자로 요약", vis=dict(cards=[dict(sig=["rc", 1], kick="오늘의 숫자", lines=rec, size=54, top=230)]), sentences=[
    S(f"오늘 숫자를 요약해 볼게요. {M} {K_(MI['unit'])} 상자 상품은 평균 {{e:{mt['avg']}}}, 킬로그램당 약 {{e:{r100(perkg(M))}}}이었어요.", rc=1)]
    + ([S(f"작년 같은 기간보다는 약 {{pc:{abs(MY)}}} {'비싸고' if MY > 0 else '싸고'}, 하루 사이에도 값이 꽤 오르내렸습니다.", rc=1)] if MY is not None else [])
    + ([S(f"킬로그램당으로는 {J(min(NAMES, key=perkg), '이', '가')} 가장 쌌고, {J(max(NAMES, key=perkg), '이', '가')} 가장 비쌌어요.", rc=1)] if len(NAMES) > 1 else [])))
# ---- 9 체크리스트·마무리
SECS.append(dict(id="check", kind="checklist", name=f"{M} 장보기 5단계", vis=dict(title=CFG["check_title"], rows=CFG["check_rows"]), sentences=[S(f"한 장으로 정리합니다. {CFG['check_title']}예요.", cal=1)] + [S(t, row=i) for i, t in enumerate(CFG["check_tts"])] + [S("이 화면은 캡처해 두셨다가 장 보러 갈 때 꺼내 보세요.", hold=1)]))
SECS.append(dict(id="outro", kind="outro", name="마무리", vis=dict(disc=["경락가 = 도매 낙찰가 ≠ 가게 판매가", "kg당 값 = 상자 값 ÷ 상자 무게", "작년 비교는 기록이 있는 것만"], take=CFG["take"]), sentences=[
    S("다시 한 번 말씀드립니다.", disc=0),
    S("오늘 값은 모두 가락시장 도매 경락가이고, 동네 가게에서 사는 값과는 달라요.", disc=1),
    S("킬로그램당 값은 상자 값을 상자 무게로 나눈 계산입니다.", disc=2),
    S(CFG["opinion"], opinion=1),
    S("노량진과 가락시장, 전국 시장의 도매가를 계속 정리해 드릴게요. 시세 재생목록도 함께 봐 주세요.", cta=1),
    S(CFG["ask"], end=1)]))
# ---- 메타·썸네일 기본값(topic.json에 비어 있으면 데이터로 채움)
pk = r100(perkg(M)); grp = CFG["group"]
if len(NAMES) > 1:
    ch_, de_ = min(NAMES, key=perkg), max(NAMES, key=perkg); RX = round(perkg(de_) / perkg(ch_), 1)
if not CFG.get("titles") or CFG["titles"] == [CFG["title"]]:
    CFG["titles"] = [f"{M} kg당 {pk:,}원{f' ({MY:+d}%)' if MY is not None else ''} | 가락시장 경매가로 본 {grp} 시세"] + ([f"{de_} vs {ch_} kg당 {RX:g}배 차이 | 가락시장 {grp} 경락가 비교"] if len(NAMES) > 1 else []) + [CFG["title"]]
if not CFG.get("desc_intro"):
    CFG["desc_intro"] = f"{CFG['hook_q']} KAMIS 가락시장 경락가(2026.11.12~11.26)로 {', '.join(NAMES[:6])} 값을 등급별·상자 크기별·kg당으로 비교하고, 작년과 최근 몇 년 같은 기간 값도 함께 봤습니다."
if not CFG.get("short_title"): CFG["short_title"] = f"{M} kg당 {pk:,}원, 가락시장 경매가 #가락시장 #{grp} #shorts"
if not CFG.get("short_desc"): CFG["short_desc"] = f"가락시장 경락가로 {M} {uname(MI['unit'])} 상자 상품 평균 {mt['avg']:,}원, kg당 약 {pk:,}원" + (f"(작년 대비 {MY:+d}%)" if MY is not None else "") + "."
if not CFG.get("thumb"):
    CFG["thumb"] = dict(top=f"가락시장 경매가 · {M} 상품", big=f"kg당<br>{pk:,}원", bigsize=150, sub=(f"작년보다 {MY:+d}%" if MY is not None else f"{uname(MI['unit'])} 상자 {mt['avg']:,}원"), subcol=("#FF5A3C" if (MY or 0) > 0 else "#5FE0C4"),
                        tag=f"{grp} 시세 총정리", b_top=f"가락시장 {grp} kg당 경락가", b_big=(f"{de_} {r100(perkg(de_)):,}원<br>{ch_} {r100(perkg(ch_)):,}원" if len(NAMES) > 1 else f"{M}<br>{mt['avg']:,}원"), b_bigsize=110,
                        b_sub=(f"{RX:g}배 차이" if len(NAMES) > 1 else "등급별·상자별 비교"), v_big=f"{M}<br>kg당 {pk:,}원")
D = dict(title=CFG["title"], hdr=CFG["hdr"], src_label="자료 · KAMIS 도매가격(가락시장 경락가격) 2026.11.12~11.26 · 작년 같은 기간", end_label="전국 시장 시세 · 장보기 데이터", hf_id=CFG["id"], sections=SECS)
if __name__ != "short":
    json.dump(D, open(f"{HERE}/대본데이터.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ch = sum(len(x[0].replace(" ", "")) for s_ in SECS for x in s_["sentences"]); n = sum(len(s_["sentences"]) for s_ in SECS)
    print("글자", ch, "문장", n, "예상", round((ch / 6.8 + n * 0.45) / 60 * 753.9 / 720, 1), "분")
    print("'그' 시작:", [x[0][:20] for s_ in SECS for x in s_["sentences"] if x[0].startswith("그")])
