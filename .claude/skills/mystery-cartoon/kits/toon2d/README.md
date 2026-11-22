# toon2d-shorts

**Version 1.1.1**. Changes: prehistoric set + caveman + dino, captions-only mode (`silent`), `words --from` accepts relative paths; 1.1.1: input checks, pinned package versions, louder-voice fix, updated character designs, notices.

A Claude skill and a small CPU-only engine for vertical cartoon Shorts: original round-headed ink characters,
painted 2D sets in parallax depth planes, light that follows the story, a camera that never stops, and
word-synced captions.

* Input: `voice.wav`, `script.txt`, optional `music.*` that you own.
* Output: `final.mp4`, 1080x1920, 30 fps, -14 LUFS.
* Runs with `pip install -r requirements.txt` on Windows, macOS, Linux and in the Claude phone app sandbox
  (2 CPUs, no GPU). Rendering is resumable in short time-boxed runs.
* Speed (measured on 2 cores): about 1 minute of set baking, then ~0.11 s per frame, so ~5 minutes for a 60 s Short.

Use `python` as written (on macOS/Linux use `python3` if `python` is not found; on Windows never `python3`, it opens
the Microsoft Store stub). Quick start (the demo has a script and a storyboard but no voice: record or generate your own `voice.wav` first,
mono or stereo, starting at 0.0 s, and put it in `examples/demo/`; for your own Shorts make the project folder
outside the skill folder):
```bash
python t2d.py doctor                  # preflight; then pip install -r requirements.txt if it asks
python t2d.py words examples/demo     # whisper; if the model can't be downloaded, a built-in aligner (no download)
python t2d.py plan examples/demo
python t2d.py stills examples/demo
python t2d.py render examples/demo --workers 2     # repeat until DONE
python t2d.py join examples/demo
python t2d.py check examples/demo
```
No voice at all? `python t2d.py silent examples/demo --script script.txt --duration 15` makes a captions-only
Short (silent track, words at reading pace) and replaces the `words` step.

Already have word timings (e.g. an ElevenLabs timestamps JSON, or a word,start,end CSV)? Put the file in the
project and run `python t2d.py words examples/demo --from timings.json`.
See `SKILL.md` for the workflow and `docs/` for the style rules and the library.

## What gets installed and downloaded

* Install into a virtual environment so nothing touches your system Python:
  `python -m venv .venv`, then `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux),
  then `pip install -r requirements.txt`. `python t2d.py doctor --install` runs the same pip command in whatever
  Python started it.
* `requirements.txt` installs from PyPI: skia-python, numpy, imageio-ffmpeg, faster-whisper (with ctranslate2,
  onnxruntime, PyAV, tokenizers, huggingface_hub) and Pillow, about 400 MB in total. imageio-ffmpeg includes a
  ready-made **ffmpeg executable** (GPL-3.0, about 105 MB on Windows) inside the package; nothing is downloaded at
  run time. To use your own ffmpeg, set `TOON2D_FFMPEG=/path/to/ffmpeg`.
* The first `words` run without `--offline`, `--from` or a timings file downloads a speech model from
  huggingface.co: `Systran/faster-whisper-small.en` (MIT, about 480 MB, default) or `base.en` (about 145 MB,
  `--model base.en`). It is stored in `<project>/.models/` (or the folder in `TOON2D_MODELS`) and reused; Hugging
  Face's library may also create its cache folder (`~/.cache/huggingface`, or `HF_HOME`). If the download is blocked,
  `words` uses the built-in aligner, which needs no model. `silent`, `words --from FILE` and `words --offline` never
  download anything.
* `doctor` contacts the package index (`PIP_INDEX_URL` or pypi.org) only when a required package is missing.
  Nothing else uses the network, and nothing is ever uploaded.
* Files are written only inside the project folder, except `stills --out DIR` and `TOON2D_MODELS`.

## Licences

Code: MIT (`LICENSE`). Font Poppins ExtraBold: SIL Open Font License 1.1 (`toon2d/fonts/OFL.txt`), unmodified.
Nothing else is bundled. `THIRD_PARTY_NOTICES.md` lists what pip installs and what is downloaded on first run,
with their licences.
