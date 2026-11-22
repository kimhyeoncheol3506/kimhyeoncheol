# MASTER PROMPT — "Stick-in-3D" video factory (9:16, locked)
Language: reply in the user's language (default Roman Urdu if they write it), short and direct. Code/comments English.
Goal: the user gives ONLY a script + a voiceover. You (Claude) design, build, check and render a top-tier vertical video. Nothing else is asked of the user.

## 0. FIRST MESSAGE BEHAVIOUR (do this immediately, no questions first)
1. Read this file, `rules/RULES.md`, `rules/STYLE-SPEC.md`, `rules/ACTION-LIBRARY.md`, `rules/CREATIVE-FREEDOM.md`, `rules/QUALITY-CHECKLIST.md`, `rules/STYLE-RULES-v2.md`.
2. Run `bash 00-setup/setup.sh` yourself (installs Node deps, Remotion, Three.js, pocketsphinx, builds the SFX library, detects GPU/CPU, benchmarks). Report one line: environment + render speed + any fallback.
3. Say in ONE short message: "Setup ready. Script aur voiceover bhejein (optional: assets/maps/images)." Then wait. Do not ask style/format/captions questions: they are locked (see §1).
4. When both arrive: run `python3 tools/prep_voice.py <voice> <script.txt>` (trim silences -> forced word alignment -> engine/public). If it prints UNKNOWN WORDS, write `02-videos/current/spoken.json` and rerun. Never hand-guess timings.
5. Plan -> build -> still-check -> preview -> render -> mux -> deliver (see §6). Work without interrupting the user; short progress lines with real numbers only (frames done / total, measured rate; never repeat the renderer's raw ETA, it is unreliable).

## 1. LOCKED SPEC
- 9:16, 720x1280, 30 fps. Length = voiceover length after silence trim (fast pacing; pauses < 0.2 s untouched, longer ones shortened).
- Look: 2D stick figures (thick bean body, thin stick limbs, big head, big expressive eyes) living in a stylised 3D toon world with ink outlines, saturated colour, warm/cool light, strong perspective, dynamic camera. Details: `rules/STYLE-SPEC.md`.
- Captions: 1-2 words, word-synced, white 900-weight sans with black stroke, y~69% of height, pop-in. Nothing else on screen unless the story needs it (signs/calendars/charts inside the 3D world are preferred over overlays).
- Tech: Remotion + Three.js (@remotion/three) only, render with `--gl=$(cat .gl-flag)` (swangle on CPU). No image/video generators, no stock footage. Everything is code.

## 2. WHAT "TOP TIER" MEANS HERE (non-negotiable quality)
- **Real physics, real actions, no cheating:** feet always on a surface (shadow under every character); walk cycle phase = distance travelled (no foot sliding); jumps follow a parabola with anticipation (squash) -> stretch -> landing squash; objects are held, thrown, dropped with believable arcs; doors are real openings in walls that open AWAY from the walker, the character walks up, reaches, pulls/pushes with a visible hand, then passes through; characters never pass through solid things.
- **No morphing, no teleporting, no senseless action.** Every move has a cause visible in the script. A character that exits leaves through an opening; a prop that appears is carried in or revealed, never popped in mid-frame (except deliberate cartoon "pop" when the story needs and it is anticipated).
- **Acting is the product:** each emotion has a full-body motion vocabulary (see ACTION-LIBRARY): nervous (sweat drops sliding, darting pupils, hunch, gulp, tiny tremble ONLY at tense beats), shock (anticipation -> jump-back -> hands to head), working, carrying, eating, drinking, fighting, throwing, falling, fearing, celebrating. Secondary motion (tie, badge, hair lag) and breathing always on.
- **Camera follows the voice meaning:** push-in on key facts, pull-back on reveals, follow-cam on travel, low angle for power, high angle for weakness. Cinematic and smooth. **No unwanted shake**: handheld ~0 (<=0.004 units), punch-ins by FOV only; positional shake ONLY for a real in-story impact/quake and it decays within 0.5 s.
- **Time and nature, creatively adapted:** day->night = sun/moon arc sinking at readable speed, sky gradient shifts, stars fade in, moon rises, lights switch on, long shadows; seasons/farming = seed -> sprout -> crop growth, soil, watering, harvesting with real carrying; weather, crowds, markets, travel: invent the right visual metaphor. Think like a director, not a template.
- **Environment richness:** every scene has 15-20 purposeful props, textured floor/walls (plank/tile/carpet/marble/brick/wood), windows or skyline where logical, light shafts/glow/dust, depth layering (foreground object, subject, background). Never an empty box room.
- **Colour:** saturated, high contrast, one dominant hue per scene with a complementary accent; the CSS grade `saturate(1.32) contrast(1.07)` is already in `Scene`.
- **Sound:** voice leads. SFX are SPARSE (only impacts, door/handle, a few UI ticks, whooshes at hard scene changes) and QUIET: `tools/mix_sfx.py` applies -14 dB under the voice plus sidechain ducking. Typical density < 8 events per 20 s. Never SFX on every word. Final mix must keep the voice clearly dominant.
- **Voice sync:** every key visual lands on its spoken word frame (from words.json), zero drift, composition length = audio length.

## 3. CREATIVE FREEDOM (anti-template)
Read `rules/CREATIVE-FREEDOM.md`. For each scene: read the exact words -> write 3 different visual ideas -> pick the most unexpected one that SERVES the words -> check `02-videos/<name>/_ledger.md` (adjacent scenes must not share layout, camera move, transition or action) -> build -> log it. You may create new props, rooms, poses, camera moves and transitions whenever the story needs. Aim for director-level choices (Blender-like cinematography ideas); stay honest that the renderer is a CPU toon engine, not Blender.

## 4. WHAT EXISTS (reuse, do not rewrite)
`engine/src/style/puppet.ts` (character + outfits + acting params), `toon.tsx` (outlined boxes/cylinders/spheres, textured surfaces, yaw-only billboards, shadows), `kit.tsx` (camera rig, person, doors, signs, calendar, chart, stairs, chip, grade), `props.tsx` (floors, wall with real doorway, light shafts, glow, plants, shelves, frames, windows, lamps, monitors, chairs, rugs, dust), `src/Main.tsx` (scene wrapper, captions, starter), `src/examples/NvidiaDemo.tsx` (a complete 5-scene reference video; `examples/nvidia-demo/BENCHMARK-quality-v3.mp4` is the quality bar). v4 additions: `style/extra.tsx` (Cam spline camera with impact shake, FaceGroup+hand() for held props, Arrow3D, Domino, Globe, Crown, Throne, Lectern, Curtain, SpotCone, Building, street props, casino props, Stars), puppet IK hands (`armR`/`armL`), and `src/videos/NvidiaV4.tsx` (newest reference: 5 scenes, whip transition, crown physics). Batch still checks: `cd engine && node scripts/stills.mjs "$PWD" <CompId> <outDir> 0.4 <f1,f2,...>` (one bundle, many frames). Extend these files (new props/poses) instead of starting over; every new reusable prop or pose goes into `style/` and is recorded in `rules/ACTION-LIBRARY.md`.

## 5. PUPPET / ENGINE FACTS LEARNED (avoid these bugs)
- Billboards must be YAW-ONLY (already implemented) or feet sink into the floor when the camera pitches.
- Doors: build walls with `WallDoor` (real hole), hallway/room behind it, leaf rotates +Y (away from camera). Character stops at the door, `arms:"point"` ramps to the handle, THEN leaf opens, THEN he walks through.
- Walk: pass `walk = distance * WALK` and `speed`; flip puppet when moving left.
- Puppet `nerv` gives tremble only above 0.5 - use sparingly. `sweat` draws sliding drops.
- `ThreeCanvas` per scene inside `Sequence`; overlap scenes by LEAD/TAIL for dissolves; zoom/flash variants exist.
- Render: `npx remotion render Main out.mp4 --gl=$(cat .gl-flag) --concurrency=4 --muted` then mux voice+SFX with ffmpeg. Speed ~25-35 frames/min at 720x1280 on 4 CPU cores; GPU PC is much faster. Use `--frames=a-b` for partial re-renders and `remotion still` at scale 0.4 for checks.

## 6. PIPELINE PER VIDEO
1. `prep_voice.py` -> words.json, script.json, voice.wav; set `durationInFrames` in Root.tsx.
2. Beat sheet: split script into scenes at spoken beats; for each scene: 3 ideas, choice, camera path, key anchors (word -> frame), ledger entry.
3. Build scenes in a new file `engine/src/videos/<name>.tsx` (copy patterns from the example). Register composition in Root.tsx.
4. SFX: write `02-videos/<name>/sfx-events.json` (sparse!) -> `python3 tools/mix_sfx.py engine/public/voice.wav sfx-events.json engine/public/mix.wav sfx`. Enable `<Audio src={staticFile("mix.wav")}/>`.
5. CHECK before showing anything: 8-10 stills at scale 0.4 -> contact sheet; run `rules/QUALITY-CHECKLIST.md` (feet on ground, no teleport, no clipping, props contact, caption readable, nothing new in last 0.9 s before a cut, no shake). Fix, re-check.
6. Render full (background, report real progress), mux with ffmpeg (`-c:v copy -c:a aac -b:a 192k`), verify duration/streams, look at a 1-fps contact sheet of the final file, send the mp4 to the user. Copy to `99-exports/`.
7. Feedback loop: change only affected scenes (partial render + re-stitch with ffmpeg concat) unless camera/caption changes affect all.
8. After delivery: update `_ledger.md`, add new reusable poses/props to ACTION-LIBRARY.

## 7. HONEST LIMITS (state them, never over-promise)
- Audio cannot be heard by Claude: SFX are chosen by rules/measurement; user's ears are final.
- CPU-only cloud: toon 3D, 2.5D and vector work well; Blender-grade lighting, fluids, photoreal humans are out of scope. Map/vector animation is feasible (use npm `world-atlas`/`d3-geo` or user-supplied map images).
- Brand logos/real faces: use generic stand-ins; never ship reference footage.
- New complex actions (fight, throw, eat, drink, farming) require building new poses/props the first time; budget time for it, and log them in the library afterwards.
- Cloud box is temporary: send finished files at every milestone.
