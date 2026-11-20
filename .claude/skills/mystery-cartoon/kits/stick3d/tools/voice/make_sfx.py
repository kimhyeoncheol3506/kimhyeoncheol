#!/usr/bin/env python3
"""Synthesizes the SFX set (no downloads needed). usage: make_sfx.py outdir. All peak at -3 dBFS; the video mixes them at -10..-20 dB."""
import numpy as np, wave, sys, os
SR=48000; out=sys.argv[1]; os.makedirs(out,exist_ok=True); rng=np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def save(name,x):
    x=x/np.max(np.abs(x))*0.708; n=int(0.004*SR); x[:n]*=np.linspace(0,1,n); x[-n:]*=np.linspace(1,0,n)
    w=wave.open(f'{out}/{name}.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
def bp(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,len(x))
# pop: soft bubble
x=t(.16); f=260+900*np.exp(-x*30); ph=2*np.pi*np.cumsum(f)/SR; save('pop',np.sin(ph)*np.exp(-x*26)+0.25*np.sin(2*ph)*np.exp(-x*40))
# tick: tiny click
x=t(.035); save('tick',bp(rng.standard_normal(len(x)),1800,6000)*np.exp(-x*160)+np.sin(2*np.pi*1500*x)*np.exp(-x*220))
# whoosh: swept noise
x=t(.55); n=rng.standard_normal(len(x)); y=np.zeros_like(n); seg=len(x)//6
for i in range(6):
    lo=300+i*i*90; hi=lo*2.2; y[i*seg:(i+1)*seg]=bp(n[i*seg:(i+1)*seg],lo,hi)
env=np.sin(np.pi*np.clip(x/.55,0,1))**2; save('whoosh',y*env)
# draw: quick rising swish for wires
x=t(.30); n=bp(rng.standard_normal(len(x)),2500,9000); save('draw',n*np.sin(np.pi*np.clip(x/.30,0,1))**1.5)
# impact: low thump + transient
x=t(.6); f=48+90*np.exp(-x*18); ph=2*np.pi*np.cumsum(f)/SR; save('impact',np.sin(ph)*np.exp(-x*7)+0.5*bp(rng.standard_normal(len(x)),200,2500)*np.exp(-x*40))
# ding: coin/cash chime
x=t(.75); save('ding',(np.sin(2*np.pi*1318*x)+0.6*np.sin(2*np.pi*1760*x)+0.3*np.sin(2*np.pi*2637*x))*np.exp(-x*7))
# stamp: slam
x=t(.35); f=70+180*np.exp(-x*40); ph=2*np.pi*np.cumsum(f)/SR; save('stamp',np.sin(ph)*np.exp(-x*12)+0.6*bp(rng.standard_normal(len(x)),800,5000)*np.exp(-x*60))

def note(y,f,st,dec,amp=1.0,dur=1.0):
    x=t(dur); n=np.sin(2*np.pi*f*x)*np.exp(-x*dec)*amp; i=int(st*SR); L=min(len(y)-i,len(n)); 
    if L>0: y[i:i+L]+=n[:L]
# chime: soft two-note bell
y=np.zeros(int(SR*1.3)); note(y,880,0,5,1,1.3); note(y,1318,0.09,6,0.55,1.2); note(y,2637,0.09,10,0.2,1.2); save('chime',y)
# sparkle: rising bell arpeggio
y=np.zeros(int(SR*1.0))
for k,fr in enumerate([1568,2093,2637,3136,3951]): note(y,fr,k*0.055,9,0.8,0.9)
save('sparkle',y)
# click: UI click
x=t(.05); save('click',bp(rng.standard_normal(len(x)),1500,6000)*np.exp(-x*200)+np.sin(2*np.pi*1900*x)*np.exp(-x*140))
# typing burst: soft keys
y=np.zeros(int(SR*1.0)); tt=0.0
while tt<0.88:
    k=t(.03); c=bp(rng.standard_normal(len(k)),1200,5500)*np.exp(-k*170)*rng.uniform(.5,1)+np.sin(2*np.pi*rng.uniform(150,230)*k)*np.exp(-k*90)*.5
    i=int(tt*SR); y[i:i+len(c)]+=c; tt+=rng.uniform(.06,.11)
save('typing',y)
# roll: odometer ratchet slowing down
y=np.zeros(int(SR*1.0)); tt=0.0; rate=48.0
while tt<0.95:
    k=t(.012); c=bp(rng.standard_normal(len(k)),2200,7000)*np.exp(-k*380)+np.sin(2*np.pi*1100*k)*np.exp(-k*300)*.4
    i=int(tt*SR); y[i:i+len(c)]+=c*(0.5+0.5*(1-tt)); tt+=1.0/rate; rate=max(9,rate*0.965)
save('roll',y)
# ping: radar
x=t(1.2); save('ping',(np.sin(2*np.pi*1250*x)+0.3*np.sin(2*np.pi*2500*x))*np.exp(-x*4.5))
# lock: thunk + short metallic ring
x=t(.45); save('lock',np.sin(2*np.pi*(110+60*np.exp(-x*40))*x)*np.exp(-x*22)+0.5*np.sin(2*np.pi*1750*x)*np.exp(-x*16)*(x>0.01)+bp(rng.standard_normal(len(x)),1000,4000)*np.exp(-x*120)*.4)
# swing: soft low whoosh
x=t(.65); save('swing',bp(rng.standard_normal(len(x)),160,1100)*np.sin(np.pi*np.clip(x/.65,0,1))**2)
# riser: filtered swell
x=t(.9); n=rng.standard_normal(len(x)); y=np.zeros_like(n); seg=len(x)//8
for i in range(8): y[i*seg:(i+1)*seg]=bp(n[i*seg:(i+1)*seg],400+i*i*70,1200+i*i*160)
save('riser',y*(np.clip(x/.9,0,1)**2)*np.exp(-np.clip(x-.8,0,1)*30))
# glass: tap
x=t(.5); save('glass',(np.sin(2*np.pi*2093*x)+.6*np.sin(2*np.pi*3136*x)+.3*np.sin(2*np.pi*4186*x))*np.exp(-x*13))
# success: three rising notes
y=np.zeros(int(SR*1.0)); note(y,1047,0,7,1,1.0); note(y,1319,0.07,7,.9,1.0); note(y,1568,0.14,6,.9,1.0); save('success',y)
# sand: soft shh
x=t(1.0); save('sand',bp(rng.standard_normal(len(x)),900,4200)*(np.sin(np.pi*np.clip(x/1.0,0,1))**1.5))
# heart: double thump
y=np.zeros(int(SR*0.7))
for st,am in [(0,1.0),(0.24,0.7)]:
    k=t(.3); th=np.sin(2*np.pi*(62+40*np.exp(-k*30))*k)*np.exp(-k*16)*am; i=int(st*SR); y[i:i+len(th)]+=th
save('heart',y)
# slash: quick blade swipe
x=t(.3); save('slash',bp(rng.standard_normal(len(x)),2500,9000)*np.exp(-x*14)*np.clip(x/.02,0,1)+np.sin(2*np.pi*3200*x)*np.exp(-x*30)*.25)
print('sfx ok')
