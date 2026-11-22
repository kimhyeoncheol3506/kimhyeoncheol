# RULES (consolidated, in the user's own words + lessons from v1-v3)
1. Output locked: 9:16 720x1280 30 fps. Voiceover drives everything; trim silences for fast pace.
2. Characters: full natural movement; real physics; feet on ground (+shadow); no morphing; no teleporting; no senseless actions; doors opened with hands properly; objects picked/thrown/dropped realistically.
3. Actions to support (build when needed, log in library): open/close door, pick up, carry, put down, throw, catch, push, pull, sit/stand, run, walk, climb stairs, fall, jump, eat, drink, cook, farm (dig, sow, water, harvest), work at desk/typing, phone use, point, wave, clap, cry, laugh, fear (cower), fight (punch/dodge/knock-back), celebrate, die (cartoon-safe: faint/fall, no gore).
4. Reactions: nervous = sweat drops + darting eyes + hunch + subtle tremble only at tense beats; shock = anticipation, jump-back, hands to head; every action has anticipation, follow-through, overshoot.
5. Camera: dynamic and meaningful (follow, push-in on key word, pull-back reveal, orbit, low/high angle); smooth easing; NO unwanted shake; positional shake only for real in-story impact and decays < 0.5 s; punch-ins use FOV.
6. SFX: only where needed, quiet (-14 dB under voice + ducking by `tools/mix_sfx.py`), sparse (<8 per 20 s), none on captions.
7. Captions: 1-2 words, white, black stroke, y ~69%, word-synced.
8. Time/nature adaptation: day->night with believable sun/moon motion, stars appear, lights turn on; farming shows seed->crop growth; seasons, weather and travel are shown, not just said. Think creatively per story.
9. Environments: 15-20 props per scene, textures, depth layers, light shafts/glow/dust; saturated grade; never empty.
10. Creative freedom: 3 ideas per scene, choose the most unexpected that serves the words; adjacent scenes never repeat layout/camera/transition/action; ledger kept.
11. Hygiene: nothing overlapping captions' key area, nothing new in the last 0.9 s before a cut, no watermarks/debug, no clipped glyphs, palette discipline per scene.
12. Process: setup once, ask only for script+voiceover, check stills yourself before showing, partial renders for fixes, report real progress, deliver files at every milestone.
13. Honesty: state what is approximate or impossible; never promise Blender-grade realism.
