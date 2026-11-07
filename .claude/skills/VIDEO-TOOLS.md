# 영상 보조 도구 5종 — 설치 기록 (2026-11-07)

현철님 요청(2026-11-07): HyperFrames · Remotion · Manim · remotion-video-skill · video-shotcraft 를 이 세션의 영상 제작에 적용.
**기본 파이프라인(`editorial/make_editorial.py` + `scene_neon.html`, 여의도여자 더빙, 검수·PUB 세트)은 그대로**이고, 이 도구들은 특정 장면을 따로 렌더해 `kind: clip` 으로 끼우는 보조 도구다.

| 저장소 | 종류 | 설치 위치 | 출처 커밋 | 라이선스 |
|---|---|---|---|---|
| heygen-com/hyperframes | 라이브러리 + 스킬 | npm `hyperframes@0.9.19` (`tools/motion`) · 스킬 `hyperframes`·`hyperframes-cli`·`hyperframes-registry`·`media-use`(10-28 설치, 그대로) + `figma`·`slideshow`·`remotion-to-hyperframes`(11-07 추가, 25a6101) | 25a6101 | Apache-2.0 → `LICENSE-hyperframes.txt` |
| remotion-dev/remotion | 라이브러리 | npm `remotion`·`@remotion/cli`·`@remotion/renderer`·`@remotion/bundler` 4.0.x (`tools/motion`) | npm 4.0.541 | **Remotion License**: 개인·직원 3명 이하 회사는 무료, 그 이상은 회사 라이선스 필요 |
| ManimCommunity/manim | 라이브러리 | `/root/.cache/manim-venv` (manim 0.22.1) + 공식용 LaTeX(texlive-latex-base/recommended/extra, dvisvgm) | PyPI 0.22.1 | MIT |
| wshuyi/remotion-video-skill | 스킬 | `.claude/skills/remotion-video/` (스킬 이름 `remotion-video`) | d16ebd9 | MIT(README 표기, 원본에 파일 없어 전문을 `remotion-video/LICENSE`·`LICENSE-remotion-video-skill.txt` 로 옮김) |
| Vincentwei1021/video-shotcraft | 스킬 | `.claude/skills/video-shotcraft/` (git 에 올라간 파일 그대로, 약 55MB: 샷 카드 124장 `references/shots/`, 데모 소스, 템플릿, BGM) | 1266a3e | Apache-2.0 → `video-shotcraft/LICENSE`·`LICENSE-video-shotcraft.txt` |

새 컨테이너에서 다시 깔기: `bash tools/motion/setup.sh` (apt·pip·npm, 약 3~5분).

## 시험 렌더(2026-11-07, 모두 5초)
- Manim: `tools/motion/manim/test_scene.py` → 1280x720, 한글(Pretendard)+MathTex 공식+그래프 ✅
- Remotion: `tools/motion/remotion/` (CounterDemo, 숫자 0→444.6 + 막대) → 1920x1080 ✅ (`--browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`, `--public-dir=../../assets/fonts`)
- HyperFrames: `tools/motion/hyperframes/index.html` (글자 하나씩 튀는 키네틱 제목) → 1920x1080, lint 0오류, 렌더 9초 ✅
- 파이프라인 끼우기: `projects/sample_motion_tools.yaml` (기존 hook 장면 + clip 장면 3개) → make_editorial 로 정상 빌드(결과는 VIDEO-TOOLS 표 아래 '파이프라인 시험' 참고)

## 주의
- 텔레메트리: HyperFrames 는 `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1`, Remotion 은 `DO_NOT_TRACK=1` 로 끄고 쓴다.
- 외부로 나가는 스크립트는 현철님이 요청할 때만: video-shotcraft `publish/upload_post.py`(SNS 업로드, api.upload-post.com) · `assets/scripts/sfx-source.py`(Freesound 키) · remotion-video `scripts/generate_audio_minimax.py`(MiniMax 유료 TTS). 우리 목소리는 여의도여자(Voicebox/Qwen Sohee) 그대로.
- video-shotcraft·remotion-video 스킬 본문은 중국어다. 둘 다 "제품 홍보 영상 전체를 Remotion 으로" 만드는 흐름이라, 우리 채널에서는 **샷 카드·리듬 규칙만 참고**하고 영상 전체를 그쪽 흐름으로 바꾸지 않는다.
