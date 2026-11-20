---
name: toon2d-shorts
description: Make vertical 1080x1920 cartoon Shorts (30-70 s) in a rich fully-2D style - round-headed ink characters with detailed costumes, painted parallax sets in 4-6 depth planes, light that follows the story acts (day setup, blue night with warm practicals, golden explanation close-up, sunset/dawn ending), a camera that never stops, and 1-2 word captions on the word onsets. CPU only (skia-python + numpy + ffmpeg via pip), resumable chunked rendering, works in the Claude phone app sandbox and on a PC. Use when asked to make, plan, render or fix a 2D cartoon Short from a voice-over, or captions only (no voice: silent track, words at reading pace).
---

# toon2d-shorts

Turns `voice.wav` + `script.txt` (+ optional `music.*` supplied by the owner) into `final.mp4`: 1080x1920, 30 fps,
-14 LUFS, burned-in captions. With no voice-over, `script.txt` alone makes a captions-only Short (step 2, Path B). Everything is pip-installable and CPU-only. No GPU, no browser, no system packages.

## 0. Setup: run doctor first (every new machine, sandbox or chat)

```bash
python t2d.py doctor                     # checks skia-python, numpy, imageio-ffmpeg (+ ffmpeg); optional ones listed
pip install -r requirements.txt          # only if doctor says packages are missing (or: python t2d.py doctor --install)
python t2d.py doctor                     # must end with DOCTOR OK before anything else
```

If doctor says pip cannot reach the package index, or `pip install` fails with a network error (connection, proxy,
403, "no matching distribution"), stop and tell the user exactly this: "Turn on Code execution and file creation and
Use internet while making files in Settings > Capabilities on claude.ai in your browser (not in the app), then start
a NEW chat." Nothing else in this skill works without the packages, and the setting only applies to new chats.

* Use `python` exactly as written. If `python` is not found (macOS, some Linux), use `python3`. On Windows never use
  `python3`: it opens the Microsoft Store stub ("Python was not found", exit 9009); use `python` or `py`.
* Never ask the user for a Hugging Face token (or any key). If a "set HF_TOKEN" warning appears, ignore it: the
  models are public, and without a download `words` falls back to the built-in aligner.
* Storyboard and word files are checked before planning: `plan` stops with a list of the problems (unknown set,
  mood or type, word index out of range, a number outside its range). Fix them and run `plan` again.
* ffmpeg comes from the `imageio-ffmpeg` wheel. To use another ffmpeg, set `TOON2D_FFMPEG=/path/to/ffmpeg`.
* Whisper models download once into `<project>/.models` (or `TOON2D_MODELS`). `small.en` is the default and gives
  the most accurate word ends. Use `--model base.en` on very slow machines. If the model host is blocked (the phone
  sandbox can return 403 for model downloads), `words` falls back to a built-in aligner that needs no download.
* **Claude phone app / cloud sandbox:** commands have short time limits. Every step below finishes in under about 4
  minutes. `render` is time-boxed (default `--budget 200` s, set bake included) and resumable, so run it again until
  it prints `DONE`. If commands are cut off sooner (e.g. a 2-minute limit), use `--budget 90`.
  Use `--workers 2` on 2 CPUs. Ask the user to keep the app open (screen on, app in front) while it works. If the
  environment resets (files gone, packages missing), ask the user to attach the zip again, run `doctor`, and continue
  from the script and storyboard already written in the chat: write them back into the project folder, redo the
  word timings (`silent` or `words`), then `plan` and `render` again. Never ask the user to start over.
* **PC:** use a portable or venv Python. Raise `--workers` to the number of cores you want to use.

## 1. Project folder

Make each project folder OUTSIDE the skill folder (the skill folder can be read-only, e.g. in the phone sandbox):
copy `examples/demo` to `./myshort` or start an empty folder. Commands take the project path.

```
myshort/
  voice.wav        the narration (starts at 0.0 s, fast and warm); captions only: `silent` writes a silent one
  script.txt       the exact words, one sentence per line
  music.mp3        OPTIONAL, only a track the owner supplied (never fetch music from anywhere)
  storyboard.json  you write this in step 3
```

## 2. Word timings

Two paths, pick one. Both end with `words.json`; everything after step 2 is the same.

**Path A: with a voice-over** (`voice.wav` + `script.txt`): see "Voice path" below.

**Path B: no-voice path, captions only** (only `script.txt`; the captions tell the story over a silent soundtrack):
silent `voice.wav` + timings at reading pace + `words --from timings.json`, all in one command:
```bash
python t2d.py silent myshort --script script.txt --duration 15   # silent voice.wav + timings.json + words.json
```
It writes a silent `voice.wav`, puts every script word at a reading pace (about 2.3 words/s, 0.35 s pause after each
sentence, a short breath after commas: `--rate` and `--pause` change them) and runs `words` on those timings. If the
script does not fit `--duration`, it keeps the pauses and reads a little faster (it says so; over 4 words/s it stops
and asks for a shorter script). It prints the `end_pad` to put in the storyboard so the video is exactly `--duration` long. `join` skips loudness
normalisation when the track peaks below -70 dBFS (music in the folder still gets mixed and normalised), and
`check` prints "silent track, loudness not applicable" instead of failing. Then continue with step 3.

**Voice path (Path A):**

```bash
python t2d.py words myshort                       # never dead-ends, see the order below
python t2d.py words myshort --from timings.json   # use timings the user brought
python t2d.py words myshort --offline --force     # skip whisper, redo with the built-in aligner
```
Writes `words.json`. The script's spelling and punctuation always win; every source only supplies times. Order:

1. `words.json` already in the project: kept as it is (say so to the user; `--force` redoes it).
2. Timings the user brought (`--from FILE`: absolute, or relative to the project folder or the current folder; or `timings.json` / `timings.csv` / `timestamps.json` /
   `alignment.json` in the project): an ElevenLabs "with timestamps" JSON (character alignment, grouped into words)
   or a plain CSV/JSON of `word,start,end` in seconds (milliseconds are detected).
3. faster-whisper with the model in `<project>/.models` (downloads once if the network allows).
4. If whisper cannot load or download: the built-in aligner (speech/silence detection on `voice.wav`, the
   script's words spread by syllables inside each speech run, sentence ends snapped to pauses). It prints a
   WARNING: captions may be a little less exact. Measured against whisper on a 19 s test voice: median 75 ms,
   90 % within 205 ms. Tell the user, and offer options 2 or 5.
5. **Whisper on the phone without a download:** on a PC run `python t2d.py words <any project>` once, then copy the
   project's `.models` folder (e.g. `.models/models--Systran--faster-whisper-small.en`, ~480 MB; `base.en` ~140 MB)
   into the phone project folder next to `voice.wav`, or point `TOON2D_MODELS` at it. Then `words --force` runs
   whisper fully offline.

Print the words with their index; you need the indices for the storyboard.

## 3. Write storyboard.json (the creative step)

Read `docs/STYLE.md` (the look and the script rules) and `docs/LIBRARY.md` (every set, mood, character, pose,
expression, prop and frame shorthand) first. `examples/demo/storyboard.json` is a complete example.

* **Scenes change only when the set or the light changes.** Light = act structure: `day`/`interior` for the
  setup, `night` for tension/secrets/waiting, `dream` for memories and fantasies, `golden` for the explanation
  ("You see, ..."), `sunset` or `dawn` for the ending. Aim for a darker middle (50-70 % of the runtime) and a more
  saturated ending.
* **keys**: one framing per sentence or clause (`{"w": word_index, "frame": ...}`). The director adds extra beats
  so the framing changes every ~0.86 s, moves take 19 frames with ease-in-out, and the camera drifts between moves.
  The director keeps every framed face whole (never sliced by an edge, never a head sitting on the bottom edge) by
  nudging framings at plan time; `check` lists any face still cut, with times. The tightest framing is `h` 800
  (painted planes stay crisp); characters stay sharp in motion blur. Favour push-ins about 2:1 over pull-outs. Put an extreme close-up of the key object inside the first second.
  Give the explanation scene `"calm": true` for longer, slower holds.
* **frame** = `[cx, cy, h]` in set pixels (`h` = visible height, 1920 = whole set), or `"wide"`, `"two"`,
  `"<actor>"`, `"<actor>:face"`, `"<actor>:full"`.
* **cast**: actors with `type` (archetype), `x`, `y` (feet), `scale`, `z` (depth plane; use the set's ground
  plane, e.g. 0.95-1.05, so they do not slide against the floor), `pose`, `expr`, `face`, `dir`.
* **acts**: per-word changes: `pose`, `expr`, `x`/`y` (walks or runs there), `talk` (mouth flaps for quoted
  lines), `hold` (prop in hand: `earth`, `planet:<kind>`, `sign:<TEXT>`, `tag:<TEXT>`, `newspaper:<A|B>`).
* Explanations live **inside the set** (a sign, a price tag, a counter, a calendar, a newspaper, a cross-section)
  and never in a floating card. If no set has the prop you need, add it to a set function (see `docs/LIBRARY.md`).

## 4. Plan, stills, critic loop

```bash
python t2d.py plan myshort              # -> plan.json, prints beats/min and caption count
python t2d.py stills myshort            # -> stills/*.png (one per scene + every 3rd beat)
```
Look at every still before rendering. Score each one 1-10 on characters, set detail, light and depth, and fix
anything under 8: framing (keys), actor placement, wrong mood, a prop hidden behind a plane. `stills --at 3.2,7.5`
renders exact times.

## 5. Render (resumable) and join

```bash
python t2d.py render myshort --workers 2     # repeat until it prints DONE (each run stays under ~3.5 min)
python t2d.py join myshort                   # -> final.mp4 (voice + optional music bed ~14 dB under, -14 LUFS)
python t2d.py check myshort                  # format, loudness, pacing, captions, faces cut by an edge
```
Set bakes are cached in `<project>/.cache`, so the first `render` spends about 1 minute baking. Measured on 2 CPU
cores: ~0.08-0.11 s per frame after baking, so a 60 s Short takes about 5 minutes in total.

## Rules

* Characters, sets and logos are original. Never imitate an existing show, channel, character or brand.
* Only use music the owner put in the project folder. Never download music or SFX.
* Never open or print `.env` files, and never ask for API keys. Nothing is uploaded anywhere.
* Captions: lowercase as spoken with punctuation kept, 1-2 words, Poppins ExtraBold (OFL, bundled in
  `toon2d/fonts`), centred at 70 % height inside the safe zone. The renderer does this; do not add text overlays.
* If a still looks flat: add a near-foreground object (blurred plane), a practical light, or a stronger light change.
  Don't add more text.

## Files

`t2d.py` CLI launcher. `toon2d/` engine (character.py characters, sets.py/outdoor.py/interiors.py sets,
setkit.py/textures.py/props.py pieces, light.py moods, scene.py camera and compositing, director.py beats/captions,
render.py chunks, audio.py mix, words.py timings, checks.py/qa.py checks). `docs/` style, library and preview sheets.
