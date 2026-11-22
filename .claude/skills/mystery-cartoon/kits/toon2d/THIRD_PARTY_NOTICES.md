# Third-party notices

toon2d-shorts is MIT-licensed (see `LICENSE`). This zip bundles one third-party file. When you install and run the
tool, it also uses third-party software and model weights that are NOT included in this zip. Each keeps its own
licence.

## 1. Bundled in this zip

### Poppins ExtraBold (toon2d/fonts/Poppins-ExtraBold.ttf)
- Copyright 2020 The Poppins Project Authors (https://github.com/itfoundry/Poppins).
- Licensed under the SIL Open Font License, Version 1.1. The full licence is in `toon2d/fonts/OFL.txt`.
- The file is unmodified (identical to `ofl/poppins/Poppins-ExtraBold.ttf` in https://github.com/google/fonts).
- The OFL places no restrictions on videos and images you make with the font.

## 2. Installed by pip (`pip install -r requirements.txt` or `python t2d.py doctor --install`)

These are not included in this zip. pip downloads them from PyPI into your Python environment.

| Package | Licence | Notes |
|---|---|---|
| skia-python (and Skia) | BSD-3-Clause; the binary statically includes FreeType (FTL), HarfBuzz (MIT), libpng (libpng), zlib (Zlib), expat (MIT) and libjpeg-turbo (IJG/BSD-3-Clause) | 2D drawing |
| numpy | BSD-3-Clause (plus 0BSD, MIT, Zlib, CC0-1.0 for bundled parts) | |
| imageio-ffmpeg | BSD-2-Clause | Its platform wheel **contains an ffmpeg executable** (next row) |
| ffmpeg executable inside imageio-ffmpeg | **GPL-3.0-or-later** (GPL build with x264/x265) | Windows builds from gyan.dev, Linux from BtbN, macOS from evermeet.cx / osxexperts. Source: https://ffmpeg.org |
| Pillow | MIT-CMU | installed by default; used for still checks and contact sheets |
| faster-whisper | MIT | installed by default; used only by `words` for word timings; bundles the Silero VAD model (MIT) |
| ctranslate2 | MIT | faster-whisper dependency |
| onnxruntime | MIT (with its own ThirdPartyNotices.txt) | faster-whisper dependency |
| av (PyAV) | BSD-3-Clause; its wheel bundles FFmpeg libraries (LGPL-3.0-or-later) and libx264/libx265 (GPL-2.0-or-later) | faster-whisper dependency |
| tokenizers, huggingface_hub, hf-xet | Apache-2.0 | faster-whisper dependencies |
| tqdm | MPL-2.0 AND MIT | |
| other small dependencies (PyYAML, filelock, fsspec, httpx, idna, packaging, protobuf, ...) | MIT / BSD / Apache-2.0 / PSF | |

Running these programs on your own computer creates no obligations for you. The videos you render are your own
output; the GPL does not cover a program's output.

## 3. Downloaded the first time you run `python t2d.py words`

- Model: `Systran/faster-whisper-small.en` (default, about 480 MB) or `Systran/faster-whisper-base.en`
  (`--model base.en`, about 140 MB), from https://huggingface.co, saved in `<project>/.models` (or `TOON2D_MODELS`).
- Licence: MIT (the Systran conversion). It is converted from OpenAI's Whisper `small.en` / `base.en`, whose weights
  OpenAI released under the MIT licence.
- Nothing is downloaded if you use `silent`, `words --from FILE` or `words --offline` (the built-in aligner).

## 4. If you share a folder that contains installed packages

If you share a folder that includes `.deps/` (from pip --target) or a Python environment, you are redistributing
the software listed above, including GPL/LGPL ffmpeg binaries. In that case, include their licence texts and a way
to get their source code (for ffmpeg: https://ffmpeg.org/download.html and the build provider's source links). The
simplest option is to share the skill without `.deps/` and `.models/` and let pip and Hugging Face fetch them.

## 5. Trademarks

Product and service names mentioned in this project (for example Claude, ElevenLabs, YouTube Shorts, Windows,
macOS) are trademarks of their owners. They are used only to describe compatibility; this project is not affiliated
with or endorsed by them. All characters, sets and props in this project are original.
