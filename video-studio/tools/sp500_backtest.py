# S&P500 98년 실제 기록 적립식 백테스트 (Damodaran 공개 자료 histretSP.xls 필요)
# 사용: curl -L -o histretSP.xls https://pages.stern.nyu.edu/~adamodar/pc/datasets/histretSP.xls && python3 tools/sp500_backtest.py
import xlrd, json, math, statistics as st
b=xlrd.open_workbook('histretSP.xls')
s=b.sheet_by_name('Returns by year'); ret={}
for r in range(s.nrows):
    y=s.cell_value(r,0)
    if isinstance(y,float) and 1900<y<2100 and isinstance(s.cell_value(r,1),float): ret[int(y)]=s.cell_value(r,1)
s=b.sheet_by_name('Inflation Rate'); inf={}
for r in range(s.nrows):
    y=s.cell_value(r,0); v=s.cell_value(r,1)
    if isinstance(y,float) and 1900<y<2100 and isinstance(v,float): inf[int(y)]=v/100
yrs=sorted(set(ret)&set(inf)); real={y:(1+ret[y])/(1+inf[y])-1 for y in yrs}
geo=lambda d: math.prod(1+d[y] for y in yrs)**(1/len(yrs))-1
print(f"{yrs[0]}~{yrs[-1]} 명목 연평균 {geo(ret):.2%}, 실질 {geo(real):.2%}, 하락한 해 {sum(ret[y]<0 for y in yrs)}/{len(yrs)}")
def fv(start,n,monthly):
    v=0
    for y in range(start,start+n): v=v*(1+real[y])+monthly*12*(1+real[y])**0.5
    return v
res={}
for n in (5,10,15,20,25,30):
    vals=[(y,fv(y,n,1.0)) for y in yrs if y+n-1<=yrs[-1]]
    xs=sorted(v for _,v in vals); w=min(vals,key=lambda x:x[1]); b_=max(vals,key=lambda x:x[1]); m=st.median(xs)
    res[n]=dict(cases=len(vals),worst_year=w[0],worst=w[1],best_year=b_[0],best=b_[1],median=m,principal=12*n,
                need_median=1e9/m/1e4,need_worst=1e9/w[1]/1e4,beat_principal=sum(v>12*n for v in xs)/len(xs))
    print(f"{n:2}년({len(vals)}구간) 원금대비 최악x{w[1]/(12*n):.2f}({w[0]}~) 중앙x{m/(12*n):.2f} 최고x{b_[1]/(12*n):.2f}({b_[0]}~) 원금초과 {res[n]['beat_principal']:.0%} | 10억: 중앙 월{res[n]['need_median']:.0f}만 / 최악 월{res[n]['need_worst']:.0f}만")
for n in (10,20,30):
    v=sorted(fv(y,n,100e4) for y in yrs if y+n-1<=yrs[-1])
    print(f"월100만 {n}년: 원금 {n*1.2:.0f}억 → 최악 {v[0]/1e8:.1f}억 중앙 {st.median(v)/1e8:.1f}억 최고 {v[-1]/1e8:.1f}억")
json.dump({"years":[yrs[0],yrs[-1]],"real_geo":geo(real),"nom_geo":geo(ret),"res":res},open("sim.json","w"),ensure_ascii=False,indent=1)
