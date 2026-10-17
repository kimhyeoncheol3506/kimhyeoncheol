"""효과음 라이브러리.

assets/sfx/<이름>.mp3|.wav 가 있으면 그 파일을, 없으면 ffmpeg 로 합성한 기본 효과음을 쓴다.
(저작권 걱정 없는 합성음이라 바로 쓸 수 있고, 마음에 드는 효과음 파일로 언제든 교체 가능)
"""
from __future__ import annotations

from pathlib import Path

from config import SFX_DIR
from utils import run_ffmpeg

NAMES = ("whoosh", "pop", "ding", "boom", "rise", "shutter")

# lavfi 합성 레시피
_RECIPES = {
    # 장면 전환: 대역 제한 핑크 노이즈가 커졌다 사라짐
    "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.55:c=pink:a=0.9",
               "-af", "highpass=f=400,lowpass=f=5000,afade=t=in:d=0.28,afade=t=out:st=0.28:d=0.27,volume=1.6"],
    # 문구 등장: 아래로 떨어지는 짧은 블립
    "pop": ["-f", "lavfi", "-i", "aevalsrc='0.8*sin(2*PI*(500*t+2400*(1-exp(-25*t))/25))*exp(-22*t)':d=0.18:s=48000"],
    # 포인트: 맑은 종소리(배음 2개)
    "ding": ["-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*1320*t)*exp(-4*t)+0.25*sin(2*PI*2640*t)*exp(-6*t)':d=1.1:s=48000"],
    # 충격 반응: 저음 임팩트
    "boom": ["-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(45*t+90*(1-exp(-7*t))/7))*exp(-3.2*t)':d=1.0:s=48000",
             "-af", "lowpass=f=900,volume=1.4"],
    # 긴장 고조: 위로 올라가는 톤
    "rise": ["-f", "lavfi", "-i", "aevalsrc='0.35*sin(2*PI*(220*t+260*t*t))*min(t/1.1\\,1)':d=1.3:s=48000",
             "-af", "afade=t=out:st=1.15:d=0.15"],
    # 사진 삽입: 셔터(노이즈 클릭 두 번)
    "shutter": ["-f", "lavfi", "-i", "anoisesrc=d=0.16:c=white:a=0.8",
                "-af", "volume='if(lt(t,0.03),1,if(lt(t,0.08),0.05,if(lt(t,0.11),0.8,0)))':eval=frame,highpass=f=1500"],
}


def sfx_path(name: str) -> Path | None:
    if not name or name == "none":
        return None
    for ext in (".mp3", ".wav", ".m4a"):
        user = SFX_DIR / f"{name}{ext}"
        if user.exists():
            return user
    if name not in _RECIPES:
        return None
    gen = SFX_DIR / "_generated" / f"{name}.wav"
    if not gen.exists():
        gen.parent.mkdir(parents=True, exist_ok=True)
        run_ffmpeg([*_RECIPES[name], "-ac", "2", "-ar", "48000", gen])
    return gen
