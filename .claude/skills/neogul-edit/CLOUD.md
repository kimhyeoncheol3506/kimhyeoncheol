# neogul-edit — Claude Code 클라우드(Linux)에서의 차이

SKILL.md 가 원본(Aside). 이 문서는 클라우드에서 다른 점만 적는다.

## 공통 설치 (세션마다 한 번, 있으면 생략)
```bash
which ffmpeg ffprobe || (apt-get update && apt-get install -y ffmpeg)
apt-get install -y fonts-noto-cjk   # 한글 폰트가 깨질 때만
```
- `python` 대신 `python3`, 경로 구분은 `/`. `.bat`/`.ps1`/`explorer.exe`/`Start-Sleep`/`chcp 65001` 은 쓰지 않고 셸에서 바로 실행한다(오래 걸리면 백그라운드 실행 후 로그 확인).
- 스크립트가 PATH의 ffmpeg를 못 찾으면 `which ffmpeg` 로 위치를 확인한다(스크립트의 WinGet 탐색은 리눅스에서 그냥 건너뜀).
- `scripts/neogul_edit.py` 는 표준 라이브러리+ffmpeg 만 쓰므로 그대로 `python3 scripts/neogul_edit.py ...` 로 실행된다.

## 음성 (여의도여자 = PC 전용)
- 여의도여자는 PC의 Voicebox(`127.0.0.1:17493`)에서만 된다. 클라우드에는 없으므로 대체 TTS를 쓴다:
  `python3 -m pip install edge-tts` → `edge-tts --voice ko-KR-SunHiNeural --rate=+8% -f script.txt --write-media voice.mp3 --write-subtitles voice.vtt` (남성은 `ko-KR-InJoonNeural`).
  edge-tts가 막히면 `gTTS`, 그것도 안 되면 무음+자막으로 만든다.
- 결과 보고(마지막 결과표)에 **"음성: 대체 TTS(여의도여자 아님) — PC에서 다시 더빙 필요"** 라고 반드시 알린다.
- 최종본을 여의도여자 목소리로 원하면 PC Remote Control 세션에서 같은 스킬을 돌리라고 안내한다.
- `voice` 명령은 `--voice 여의도여자` 를 빼면 Windows TTS(Heami)를 쓰는데 리눅스에는 없다. 클라우드에서는 위 edge-tts로 **문장별 wav**(대본 한 줄 = 파일 하나, `01.wav, 02.wav …`)를 만든 뒤 `voice script.txt --out-dir <폴더> --wav-dir <문장별음성폴더>` 로 voice.wav·voice.srt 를 만든다.

## 너굴분석(참고 영상 받기)
- SKILL.md 의 ytultra.com + REPL fetch 방식은 Aside 전용이다. 클라우드에서는 `yt-dlp -f 18 <URL>` 을 먼저 시도한다.

## 유튜브 다운로드
- `python3 -m pip install -U yt-dlp` 후 `yt-dlp` 사용. 클라우드는 데이터센터 IP라 "Sign in to confirm you're not a bot" / 403 / 자막 없음으로 막히기 쉽다.
- 막히면 재시도로 버티지 말고 멈춘 뒤, **"유튜브 다운로드는 PC Remote Control 세션에서 해 주세요"** 라고 안내한다(필요한 URL·구간 목록은 표로 남긴다). 쿠키·로그인 정보는 받지 않는다.

## 결과물
- 결과 폴더는 `C:\Users\Admin\Desktop\...`/Downloads 대신 저장소 안 작업 폴더(`output/`)에 둔다. 100MB 넘는 mp4는 커밋 금지 → `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart out.mp4` 로 45MB 이하로 줄여 커밋.
- 업로드는 하지 않는다(사용자가 명령할 때만, 그리고 업로드는 PC).

---

# 이 브랜치(claude/exciting-curie-w62fz4)에서 쓰던 개선점 — 보존

## 클라우드 음성: 실제로 쓴 방법
- 이 컨테이너에서는 edge-tts가 프록시(WebSocket) 때문에 막혔다. 대신 **Supertonic-3(목소리 F3)**로 문장별 wav를 만들고, **faster-whisper(medium, int8)**로 받아써 대본과 비교해 일치율 0.85 미만 문장은 다시 생성했다.
- 도구: `video_projects/월재스/_tools/tts_local.py gen|check <작업폴더>`, 정렬·project.json은 `build.py`, 렌더는 `render_all.py`. 대본을 고친 뒤 기존 음성 재사용은 `remap.py`.
- 결과 보고에는 "음성: 대체 TTS(여의도여자 아님)"를 적는다(위 원칙과 같음).

## 장면별 도구 선택 (추가 엔진)

위의 실행 순서·말투(규칙집 9장)·음성(여의도여자)·검수(미리보기 → 최종 렌더, -16 LUFS) 규칙은 그대로 둔다. 아래는 **슬라이드 한 장으로는 부족한 장면**의 클립을 어느 도구로 만들지 정한 것이다. 만든 클립은 `video_projects/_engines/README.md` 방식대로 `slide` 장면의 `image`(mp4, `image_box: [0,0,1920,1080]`)로 넣는다. neogul_edit.py 자체는 고치지 않는다.

| 장면 성격 | 1순위 도구 | 대안 | 메모 |
|---|---|---|---|
| 기본 인포그래픽(카드·막대·큰 숫자·목록) | **neogul-edit 슬라이드** (R-L5) | — | 지금처럼. 대부분의 장면은 여기서 끝낸다 |
| 숫자 카운트업, 막대·선 그래프가 자라는 애니메이션, 데이터 대시보드 | **Remotion** (`_engines/remotion`) | HyperFrames | `remotion-video` 스킬 참고. 회사 규모가 커지면 Remotion 라이선스 확인 |
| 키네틱 타이포(문장이 튀어나오는 강조), 뉴스 헤드라인 모션, 전환 효과, 오버레이 | **HyperFrames** (`_engines/hyperframes`) | Remotion | `hyperframes`·`hyperframes-registry` 스킬(블록 약 450개: 전환·타이틀·차트·지도) |
| 공식·수식, 함수 그래프, 기하·확률 설명(복리, 신용창조 급수, 폰지 기하급수 등) | **Manim** (`_engines/manim`) | — | 한글은 `Text(font="Pretendard")`, 수식은 `MathTex`. 최종은 `-qh`(1080p) |
| 컷 리듬·샷 구성(오프닝 훅, 챕터 전환, 아웃트로의 카메라 무브·리빌) | **video-shotcraft 샷 레시피** (`references/shots/` 124장) | HyperFrames 블록 | 레시피의 *리듬·타이밍*만 빌리고 제품 홍보 전용 흐름(Ink Press 템플릿, 모드 선택 질문)은 경제2 영상에 쓰지 않는다 |
| 효과음 고르기·맞추기 | neogul-edit 자동 효과음(R-S1) | video-shotcraft `sound-design.md` | 새 효과음을 쓰면 출처·라이선스를 설명란에 남긴다 |
| 3D 오브젝트·입체 장면(돌아가는 ₩ 코인, 3D 막대, 금고) | **Blender** (`blender-3d` 스킬) | Remotion | 최종 1080p는 PC GPU. 수치 비교는 3D로 하지 않는다 |
| B-roll 장면 그림·챕터 표지·썸네일 배경(퍼블릭 도메인 그림이 없을 때) | **ComfyUI** (`comfyui-image` 스킬, PC 전용) | 제목 카드(대체) | 영어 프롬프트, 실존 인물·로고·숫자 금지, 'AI 생성 이미지' 표기 |
| 작거나 흐린 그림·사진 키우기 | **Real-ESRGAN** (`upscale-esrgan` 스킬) | — | 긴 변 1280px 미만이면 B-roll·썸네일 전에 키운다 |

### 제작 단계별 공통 도구 (2026-11 추가)
| 단계 | 도구(스킬) | 할 일 |
|---|---|---|
| 참고 영상 분석(너굴분석) | `scene-split`(PySceneDetect) + neogul-edit `analyze` | 컷 목록·분당 컷·장면 길이. 어두운 슬라이드형 영상은 `--threshold 8` |
| 참고 영상·자막 받기(분석 준비) | `yt-dlp` | 정보·자막·저화질 영상을 받아 분석·받아쓰기에만 쓴다. 받은 영상·음성을 우리 영상에 넣지 않는다. 클라우드는 YouTube 봇 확인에 자주 막힘 → PC에서 `--cookies-from-browser chrome` |
| 내레이션 발음 검수 | `whisper-subtitle`(faster-whisper) | 대본과 받아쓰기 대조, 일치율 0.85 미만 문장 다시 생성 |
| 렌더 뒤 손질·전달본 | `ffmpeg-edit` | 파트 이어 붙이기, 720p, 쇼츠 세로, 음량 -16 LUFS 확인 |
| 렌더 검수 | `ffmpeg-edit`의 프레임 시트 + `scene-split` 통계 | 글자 넘침·검은 화면 확인, 8초 넘게 그대로인 장면(R-P2) 확인 |

엔진 클립 공통 규칙:
- 1920x1080, 30fps, 무음. 색은 규칙집 팔레트(R-L2, R-L6), 폰트 Pretendard.
- 글자·그래프는 y 880 위쪽(아래는 하단 자막 자리, R-T1).
- 장면 길이에 맞춰 렌더하거나 `tpad=stop_mode=clone`으로 마지막 프레임을 늘린다(짧으면 반복 재생됨).
- R-P2(8초 넘게 화면 변화 없음 금지)는 엔진 클립에도 적용한다.
- 숫자·출처는 대본과 같은 근거만 쓰고, 단순화한 그래프는 화면에 '예시'라고 적는다.
- 미리보기 단계에서 엔진 클립이 들어간 장면 프레임을 반드시 뽑아 본다.
