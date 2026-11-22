Generic voiceover/SFX/asset tools (style-independent):
- trim.py <in.mp3> <outdir>: shorten only short silent pauses (<0.20s untouched); writes trimmed wav/mp3 + cuts.json
- align.py <wav> <script.txt> <out.json>: forced alignment of the script to audio (offline pocketsphinx; needs `pip install pocketsphinx`). Spell numbers/symbols in script_spoken.txt; per-token overrides in spoken.json
- make_sfx.py <outdir>: synth SFX library (no downloads)
- prep_assets.py: photo resize, circle-crop logo without cropping glyphs, square crop
