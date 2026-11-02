import re,sys,glob,os
pat=re.compile(r"(\d[\d,]*\s?원|\d+만\s?원|\d+\s?호|키오스크|예약|\d+\s?분|영업|오전|오후|\d{1,2}시|보냉|카톡|알림|두툼|두께|대기|웨이팅)")
for d in sys.argv[1:]:
    for f in sorted(glob.glob(d+"/*.txt"), reverse=True)[:5]:
        t=open(f,encoding='utf-8').read().replace("\n"," "); print("===",os.path.basename(f), len(t))
        seen=0; last=-100
        for m in pat.finditer(t):
            if m.start()-last<90: continue
            last=m.start(); print("  ·",t[max(0,m.start()-45):m.end()+55].replace("  "," ")); seen+=1
            if seen>=14: break
