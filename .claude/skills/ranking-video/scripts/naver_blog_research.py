# -*- coding: utf-8 -*-
"""네이버 블로그 자료 조사: 최근 N개월 글 중 잘 쓴 블로그 글을 골라 점수와 발췌를 남긴다 (ranking-video v2.1.0)

사용법:
    python3 -I naver_blog_research.py <출력폴더> "검색어1" ["검색어2" ...] [--months 3] [--max 30]
출력:
    <출력폴더>/블로그조사.tsv       점수 높은 순: 점수, 작성일, 본문 글자 수, 사진 수, 광고표시, 제목, URL
    <출력폴더>/블로그_발췌/*.txt    본문 앞부분(읽고 사실을 확인하는 용도. 그대로 베껴 쓰지 않는다)

점수(100점): 본문 길이 35 + 사진 수 20 + 구성(소제목·번호 목록) 15 + 최신성 20 + 광고·협찬 표시 없음 10,
  여기에 주제 관련도(검색어 낱말이 제목·본문 앞부분에 들어 있는 비율)를 곱한다(0.4~1.0배).
- 광고·협찬·체험단·원고료·소정의 등 표시가 있으면 '광고표시=예'로 남기고 10점을 주지 않는다(사실 확인용으로만 참고).
- 기간 밖(작성일이 N개월보다 오래된) 글은 제외한다.
- 네이버 검색은 `where=blog&nso=so:r,p:{N}m`(관련도순, 최근 N개월)로 요청한다.
"""
import datetime as dt, html, os, re, subprocess, sys, time, urllib.parse

UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
UA_M = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"
AD = ["광고", "협찬", "원고료", "체험단", "제공받", "소정의", "업체로부터", "지원받"]


def get(url, ua):
    # v2.3.0: 파이썬 urllib 요청은 네이버가 403으로 막는 일이 잦아 curl로 받는다
    r = subprocess.run(["curl", "-sS", "--compressed", "-m", "25", "-A", ua, "-H", "Accept-Language: ko-KR,ko", "-w", "\n%{http_code}", url],
                       capture_output=True, text=True, errors="ignore")
    body, _, code = r.stdout.rpartition("\n")
    if code != "200": raise RuntimeError(f"HTTP {code}")
    return body


def parse_date(h, today):
    m = re.search(r"(20\d\d)\.\s?(\d{1,2})\.\s?(\d{1,2})\.\s?\d{1,2}:\d{2}", h)
    if m: return dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"(\d+)\s*(시간|분) 전", h)
    if m: return today
    m = re.search(r"(\d+)\s*일 전", h)
    if m: return today - dt.timedelta(days=int(m[1]))
    return None


def analyze(blog_id, log_no, today):
    h = get(f"https://m.blog.naver.com/PostView.naver?blogId={blog_id}&logNo={log_no}", UA_M)
    title = re.search(r"<title>(.*?)</title>", h, re.S)
    title = html.unescape(title.group(1)).replace(": 네이버 블로그", "").strip() if title else ""
    i = h.find("se-main-container")
    seg = h[i:i + 120000] if i >= 0 else h
    for end in ("post_footer", "commentWrap", "_postFooter", "btn_like"):
        j = seg.find(end)
        if j > 0: seg = seg[:j]; break
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", seg, flags=re.S)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
    text = text.replace('se-main-container">', "").strip()
    imgs = len(re.findall(r"se-image-resource", seg))
    heads = len(re.findall(r"se-section-sectionTitle|se-quotation|se_textarea_title", seg)) + len(re.findall(r"(?:^| )\d{1,2}\.\s", text[:6000]))
    ad = any(k in text for k in AD)
    return dict(id=blog_id, no=log_no, title=title, date=parse_date(h, today), text=text, imgs=imgs, heads=heads, ad=ad,
                url=f"https://blog.naver.com/{blog_id}/{log_no}")


def score(p, today, months, queries=()):
    s = 35 * min(len(p["text"]) / 3500, 1) + 20 * min(p["imgs"] / 12, 1) + 15 * min(p["heads"] / 5, 1)
    if p["date"]: s += 20 * max(0, 1 - (today - p["date"]).days / (31 * months))
    if not p["ad"]: s += 10
    hay = p["title"] + " " + p["text"][:3000]
    rel = max((sum(w in hay for w in q.split()) / max(1, len(q.split())) for q in queries), default=1)
    return round(s * (0.4 + 0.6 * rel), 1)


def main():
    a = sys.argv[1:]
    months = int(a[a.index("--months") + 1]) if "--months" in a else 3
    mx = int(a[a.index("--max") + 1]) if "--max" in a else 30
    a = [x for k, x in enumerate(a) if x not in ("--months", "--max") and (k == 0 or a[k - 1] not in ("--months", "--max"))]
    out, queries = a[0], a[1:]
    os.makedirs(os.path.join(out, "블로그_발췌"), exist_ok=True)
    today = dt.date.today(); seen = []
    for q in queries:
        u = "https://search.naver.com/search.naver?" + urllib.parse.urlencode({"ssc": "tab.blog.all", "where": "blog", "query": q, "nso": f"so:r,p:{months}m"})
        h = ""
        for k in range(4):  # 네이버가 연속 요청을 403으로 막을 때가 있다 → 쉬었다가 다시, 끝내 안 되면 그 검색어만 건너뜀
            try:
                h = get(u, UA_PC); break
            except Exception as e:
                print("검색 재시도", q, e); time.sleep(5 * (k + 1))
        for bid, no in re.findall(r"https://blog\.naver\.com/([A-Za-z0-9_\-]+)/(\d{9,})", h):
            if (bid, no) not in seen: seen.append((bid, no))
        time.sleep(1.0)
    posts = []
    for bid, no in seen[:mx]:
        try:
            p = analyze(bid, no, today); time.sleep(0.8)
        except Exception as e:
            print("건너뜀", bid, no, e); continue
        if p["date"] and (today - p["date"]).days > 31 * months: continue
        p["score"] = score(p, today, months, queries); posts.append(p)
    posts.sort(key=lambda p: -p["score"])
    with open(os.path.join(out, "블로그조사.tsv"), "w", encoding="utf-8") as f:
        f.write("점수\t작성일\t글자수\t사진\t광고표시\t제목\tURL\n")
        for p in posts:
            f.write(f"{p['score']}\t{p['date'] or '?'}\t{len(p['text'])}\t{p['imgs']}\t{'예' if p['ad'] else ''}\t{p['title']}\t{p['url']}\n")
    for p in posts[:15]:
        open(os.path.join(out, "블로그_발췌", f"{p['score']:05.1f}_{p['id']}_{p['no']}.txt"), "w", encoding="utf-8").write(
            f"{p['title']}\n{p['url']}\n작성일 {p['date']} · 사진 {p['imgs']} · 광고표시 {'예' if p['ad'] else '아니오'}\n\n{p['text'][:6000]}\n")
    print(f"글 {len(posts)}개 분석 → 상위 5개")
    for p in posts[:5]: print(f"  {p['score']:5.1f}  {p['date']}  {p['title'][:40]}  {p['url']}")


if __name__ == "__main__":
    main()
