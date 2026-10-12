import sys, subprocess, re, json
def fetch(url):
    return subprocess.run(["curl","-sS","-H","Accept-Language: ko-KR","-H","User-Agent: Mozilla/5.0",url],capture_output=True,text=True).stdout
def walk(o, out):
    if isinstance(o,dict):
        if "lockupViewModel" in o:
            l=o["lockupViewModel"]; vid=l.get("contentId")
            md=l.get("metadata",{}).get("lockupMetadataViewModel",{})
            title=md.get("title",{}).get("content")
            parts=[]
            for row in md.get("metadata",{}).get("contentMetadataViewModel",{}).get("metadataRows",[]):
                for p in row.get("metadataParts",[]): parts.append(p.get("text",{}).get("content"))
            out.append((vid,title,parts))
        if "videoRenderer" in o:
            v=o["videoRenderer"]; out.append((v.get("videoId"), "".join(r.get("text","") for r in v.get("title",{}).get("runs",[])), [v.get("viewCountText",{}).get("simpleText"), v.get("publishedTimeText",{}).get("simpleText"), v.get("lengthText",{}).get("simpleText")]))
        for x in o.values(): walk(x,out)
    elif isinstance(o,list):
        for x in o: walk(x,out)
def get(handle_or_id):
    base = f"https://www.youtube.com/channel/{handle_or_id}" if handle_or_id.startswith("UC") else f"https://www.youtube.com/{handle_or_id}"
    html=fetch(base+"/videos")
    m=re.search(r"var ytInitialData = (\{.*?\});</script>", html)
    out=[]; walk(json.loads(m.group(1)),out) if m else None
    # popular chip continuation
    pop=[]
    if m:
        d=json.loads(m.group(1)); s=json.dumps(d,ensure_ascii=False)
        chips=re.findall(r'"chipViewModel": \{"text": "(인기순|Popular)".*?"continuationCommand": \{"token": "([^"]+)"', s)
        if chips:
            key=re.search(r'"INNERTUBE_API_KEY":"([^"]+)"',html).group(1)
            ver=re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"',html).group(1)
            body=json.dumps({"context":{"client":{"clientName":"WEB","clientVersion":ver,"hl":"ko","gl":"KR"}},"continuation":chips[0][1]})
            r=subprocess.run(["curl","-sS","-H","Content-Type: application/json","-d",body,f"https://www.youtube.com/youtubei/v1/browse?key={key}"],capture_output=True,text=True).stdout
            walk(json.loads(r),pop)
    return out,pop
if __name__=="__main__":
    for h in sys.argv[1:]:
        latest,pop=get(h)
        json.dump({"latest":latest,"popular":pop},open("ch_"+re.sub(r'\W','_',h)+".json","w"),ensure_ascii=False)
        print("==",h,"latest",len(latest),"popular",len(pop))
        for v in (pop or latest)[:8]: print("  ",v[2],v[1])
