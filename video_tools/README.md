# 영상 제작 도구 테스트 (ranking-video v2.14.0)
| 폴더 | 도구 | 5초 테스트 렌더 |
|---|---|---|
| hf_test/ | HyperFrames 0.8.214 (npx) | `npx --yes hyperframes@0.8.214 render -o out/hf_test.mp4 -q draft` |
| remotion_test/ | Remotion 4.0.541 (React) | `npx remotion render src/index.ts Hello out/hello.mp4 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell` |
| manim_test/ | Manim Community 0.22.1 | `~/.cache/manim-venv/bin/manim -qh --fps 30 --media_dir media test_scene.py PriceLine` (가상 값 — 실제 영상에 쓰지 말 것) |
새 세션에서는 `bash video_tools/setup.sh` 먼저(약 2~3분). 장면별 도구 선택은 `.claude/skills/ranking-video/SKILL.md`의 '장면별 도구 선택'.
