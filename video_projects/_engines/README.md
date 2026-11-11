# 영상 보조 엔진 (HyperFrames · Remotion · Manim)

neogul-edit 파이프라인(대본 → 음성 → project.json → render)은 그대로 두고, **특정 장면의 영상 클립만** 이 엔진들로 만들어 끼워 넣는다.
어떤 장면에 어떤 엔진을 쓰는지는 `.claude/skills/neogul-edit/SKILL.md` 의 "장면별 도구 선택" 절을 따른다.

| 엔진 | 폴더 | 버전 | 라이선스 | 시험 렌더 |
|---|---|---|---|---|
| HyperFrames (HTML+GSAP → MP4) | `hyperframes/econ-test/` | hyperframes 0.9.19 | Apache-2.0 | 1080p 5초, 6.4초 걸림 |
| Remotion (React → MP4) | `remotion/` | remotion 4.0.541 | Remotion License (개인·3인 이하 회사 무료, 그 이상 회사는 유료) | 1080p 5초, 19초 걸림 |
| Manim Community (수식·그래프) | `manim/` | manim 0.22.1 | MIT | 720p 5초, 4초 걸림 |

## 설치 (새 컨테이너·PC에서 한 번)

```bash
cd video_projects/_engines/remotion && npm install
```
```bash
cd video_projects/_engines/hyperframes && npm install
```
```bash
pip install manim
```
- Manim은 시스템 라이브러리가 필요하다. 리눅스: `apt-get install -y libcairo2-dev libpango1.0-dev pkg-config texlive-latex-base texlive-fonts-recommended texlive-latex-extra dvisvgm` (Windows는 `pip install manim` + MiKTeX).
- 클라우드 세션에서 `srt` 빌드가 `install_layout` 오류로 실패하면: `pip install -U --ignore-installed setuptools wheel` 후 다시 설치.

## 시험 렌더 명령

클라우드 세션은 미리 깔린 헤드리스 크롬을 쓴다(PC에서는 환경변수 없이 실행하면 각 도구가 알아서 크롬을 찾거나 내려받는다).
```bash
export CHS=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
```
```bash
cd video_projects/_engines/remotion && REMOTION_BROWSER=$CHS npx remotion render src/index.ts CounterBars out/remotion_test.mp4
```
```bash
cd video_projects/_engines/hyperframes/econ-test && DO_NOT_TRACK=1 HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_BROWSER_PATH=$CHS npx hyperframes lint && DO_NOT_TRACK=1 HYPERFRAMES_BROWSER_PATH=$CHS npx hyperframes render -o renders/test.mp4
```
```bash
cd video_projects/_engines/manim && manim -qh compound_scene.py CompoundInterest -o compound_test.mp4
```

## neogul-edit 장면에 끼워 넣는 법 (스킬 수정 없음)

1. 클립은 **1920x1080, 30fps**, 장면 길이(초)에 맞춰 렌더한다. 길이를 맞추기 어려우면 마지막 프레임을 늘린다(neogul-edit은 짧은 영상을 반복 재생하므로):
   ```bash
   ffmpeg -i clip.mp4 -vf "tpad=stop_mode=clone:stop_duration=30" -an -c:v libx264 -crf 16 -pix_fmt yuv420p clip_hold.mp4
   ```
2. project.json 장면:
   ```json
   {"type": "slide", "start_line": 42, "image": "assets/engines/clip_hold.mp4", "image_box": [0, 0, 1920, 1080]}
   ```
   제목·섹션을 비우면 클립이 화면 전체를 덮고, 그 위에 neogul-edit 하단 자막(R-T1)이 얹힌다.
3. 클립 안의 글자·그래프는 **y 880 위쪽**에 둔다(아래쪽은 자막 자리). 배경은 규칙집 색(다크 #181614 / 크림 #F4F0E8), 폰트는 Pretendard.
4. 효과음·음량은 neogul-edit이 처리하므로 클립은 **무음(-an)** 으로 넣는다.

## 추가 도구 설치 (2026-11)

| 도구 | 스킬 | 클라우드(리눅스) | PC(Windows) |
|---|---|---|---|
| FFmpeg | `ffmpeg-edit` | 기본 설치됨(6.1) | `winget install Gyan.FFmpeg` |
| faster-whisper | `whisper-subtitle` | `pip install faster-whisper` | 같음 (GPU면 `--device cuda --compute float16`) |
| PySceneDetect | `scene-split` | `pip install "scenedetect[opencv-headless]"` | 같음 |
| Real-ESRGAN | `upscale-esrgan` | `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` 후 `pip install spandrel` (가중치는 첫 실행 때 자동) | CUDA판 torch 설치 후 `--device cuda` |
| Blender | `blender-3d` | `apt-get install -y blender` (4.0, 노이즈 제거기 없음) | blender.org 설치판(`--gpu --denoise 1`) |
| ComfyUI | `comfyui-image` | 설치하지 않음(그래픽카드·모델 필요) | ComfyUI 데스크톱/포터블 + SDXL 체크포인트, 127.0.0.1:8188 |

- apt로 Blender·LaTeX를 설치한 뒤 pip 빌드가 `install_layout` 오류로 깨지면: `pip install -U --ignore-installed setuptools wheel`.
