"""위키미디어 공용 429(요청 과다)로 못 받은 사진을 다시 받는 스크립트(2026-11-13). 받은 뒤 photo_map.yaml 의 '# (못 구함)' 줄 주석을 풀고 manifest.yaml 에 항목을 되살린 뒤 build 를 다시 실행."""
import hashlib,urllib.parse,subprocess,time,os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media", "oneshot_saudi")
L=[("02_dammam7_1938b.jpg","Dammam Well-7, 1938 02.jpg",1200),
("04_abqaiq_1949.jpg","Abqaiq refinary.jpg",750),
("06_dammam_riyadh_rail_1951.png","Dammam–Riyadh line, 1951.png",902),
("09_opec_vienna.jpg","Wien - OPEC-Zentrale (a).JPG",4150),
("10_rub_al_khali.jpg","Rub al Khali 002.JPG",3553),
("11_riyadh_kafd.jpg","Riyadh Skyline showing the King Abdullah Financial District (KAFD) and the famous Kingdom Tower .jpg",6000),
("12_riyadh_metro.jpg","Riyadh Metro (2024).jpg",8256),
("13_jubail_port.jpg","King Fahad Industrial port,Jubail - panoramio.jpg",1600),
("14_jubail_petrochem.jpg","Jubail petrochem-industrial plants.jpg",3264),
("17_slochteren_1963.jpg","Gasbel te Slochteren Nederlandse Gas Unie werkzaamheden, Bestanddeelnr 915-2654.jpg",4154),
("18_ekofisk.jpg","Ekofisk complex.jpg",3712),
("19_oslo_harbour.jpg","Oslo harbour 2015 a.jpg",5720),
("20_tanker_gulf.jpg","US Navy 041207-N-6932B-014 The oil tanker Omala is one of hundreds of oil tankers from around the world that receives its payload from Iraq's Al Basrah Oil Terminal (ABOT).jpg",2464)]
def url(name,w):
    n=name.replace(' ','_'); h=hashlib.md5(n.encode()).hexdigest(); q=urllib.parse.quote(n)
    if w<=1280: return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"
    ext='' 
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/1280px-{q}"
for rnd in range(12):
    left=[x for x in L if not (os.path.exists(f"{OUT}/{x[0]}") and os.path.getsize(f"{OUT}/{x[0]}")>5000)]
    print("round",rnd,"left",len(left),flush=True)
    if not left: break
    for fn,name,w in left:
        u=url(name,w); dst=f"{OUT}/{fn}.part"
        r=subprocess.run(["curl","-sL","-m","90","-A","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36","-o",dst,"-w","%{http_code}",u],capture_output=True,text=True)
        code=r.stdout.strip(); print(fn,code,flush=True)
        if code=="200" and os.path.getsize(dst)>5000: os.rename(dst,f"{OUT}/{fn}")
        else:
            if os.path.exists(dst): os.remove(dst)
            if code=="429": time.sleep(150)
        time.sleep(15)
    time.sleep(300)
