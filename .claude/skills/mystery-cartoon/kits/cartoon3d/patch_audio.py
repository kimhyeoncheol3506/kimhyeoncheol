# -*- coding: utf-8 -*-
import re, json
s = open("audio.py", encoding="utf-8").read()
s = s.replace("DUR = 592 / 30", "DUR = 353 / 30")
s = s.replace('"voice.mp3"', '"../samples/A_legion/voice.wav"')
s = s.replace("MUSIC_END = 14.15", "MUSIC_END = 9.35")
a = s.index("F = lambda f: f / 30")
b = s.index("voice = load_voice()")
cues = '''F = lambda f: f / 30
place(sfx, whoosh(0.6), F(16), 0.5)            # hook pull-back reveal
place(sfx, thunk(80, 0.35), F(52), 0.8)        # ranks stamp
place(sfx, whoosh(0.5), F(70), 0.45)           # cut to the march
place(sfx, leaves(2.4), F(80), 0.3)            # wind in the mist
place(sfx, rumble(1.6), F(95), 0.5)            # they vanish
place(sfx, ting(), F(100), 0.35)
place(sfx, thunk(70, 0.4), F(134), 0.8)        # the whole legion
place(sfx, whoosh(0.4), F(174), 0.6)           # flash: field empty
place(sfx, leaves(2.5), F(182), 0.3)
place(sfx, scrape(0.7), F(232), 0.45)          # helmet in the grass
place(sfx, whoosh(0.6), F(281), 0.4)
place(sfx, sting(), 11.17, 0.85)               # "걸까요?"
'''
s = s[:a] + cues + "\n" + s[b:]
open("audio.py", "w", encoding="utf-8").write(s)

# captions (ASS) from timings
W = json.load(open("../samples/A_legion/timings.json", encoding="utf-8"))
groups = [[0, 1], [2, 3], [4], [5], [6], [7, 8], [9], [10], [11, 12], [13], [14], [15], [16], [17, 18], [19]]
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); sec = t % 60
    return "%d:%02d:%05.2f" % (h, m, sec)
lines = []
for i, g in enumerate(groups):
    st = W[g[0]]["start"]
    en = W[groups[i + 1][0]]["start"] if i + 1 < len(groups) else 353 / 30
    if i + 1 < len(groups) and groups[i + 1][0] in (7, 15):  # sentence gap: keep until the word ends + small hold
        en = min(en, W[g[-1]]["end"] + 0.25)
    txt = " ".join(W[k]["word"] for k in g)
    lines.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,{\\fscx86\\fscy86\\t(0,120,\\fscx100\\fscy100)}%s" % (ts(st), ts(en), txt))
ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Pretendard ExtraBold,96,&H00FFFFFF,&H00FFFFFF,&H00201B1B,&H8C000000,0,0,0,0,100,100,0,0,1,7,4,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ass += "".join("Dialogue: " + l.split("Dialogue: ", 1)[1].replace("Dialogue: 0,", "") + "\n" for l in lines)
# position at 70% height via \\pos
ass = ass.replace("{\\fscx86", "{\\pos(540,1344)\\fscx86")
open("caps.ass", "w", encoding="utf-8").write(ass)
print(ass)
