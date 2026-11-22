---
name: "neogul-edit"
description: "사용자가 \"너굴편집\" 또는 \"너굴경제 스타일로 편집해줘\"라고 하면 실행. 내레이션 음성/대본과 소스(이미지·영상)를 받아 너굴경제 편집 규칙집(인포그래픽 슬라이드, 하단 박스 자막, 빨간 박스 강조, B-roll 줌+분홍 플래시, 마스코트 컷인, 무음 압축, 효과음 자동 배치)대로 Python+ffmpeg로 롱폼 영상을 자동 편집해 mp4로 만든다. \"너굴분석\"이라고 하면 참고 영상의 컷 간격·무음·음량을 같은 방식으로 측정한다."
---

# 너굴편집

규칙: `references/규칙집.md` (R-코드). 근거: `references/편집분석집.md`. 수치: `scripts/rules.json`. 편집기: `scripts/neogul_edit.py` (표준 라이브러리만 사용, ffmpeg 필요. PATH에 없으면 WinGet 설치본을 자동으로 찾음).

## 실행 순서

1. **입력 확인** (ask_user_question으로 한 번에 묻기): 작업 폴더, 내레이션 형태(완성 음성+srt / 문장별 음성 파일+대본 / 대본만 있으면 Windows TTS 임시 음성), 마스코트·훅 이미지, B-roll 영상. 없는 것은 임시 자료로 진행해도 되는지 묻는다.
2. **음성과 자막 준비**
   - 대본만 있거나 문장별 음성 파일이 있으면: `python scripts/neogul_edit.py voice script.txt --out-dir <폴더> [--wav-dir <문장별음성폴더>] [--voice 여의도여자]` 를 실행하면 voice.wav와 voice.srt가 생긴다 (srt 줄 번호 = 대본 줄 번호).
   - 기본 목소리는 **여의도여자** (Voicebox, http://127.0.0.1:17493)이다. 서버가 꺼져 있으면 `explorer.exe "C:\Program Files\Voicebox\voicebox.exe"` 로 켜고 /profiles 응답을 기다린다(약 20초). 한 문장에 20~50초 걸리므로 셸은 yield_ms로 돌리고 진행 상황을 본다. `--voice`를 빼면 Windows TTS(Heami)로 임시 음성을 만든다.
   - 데모: `demo <폴더> --voice 여의도여자`
   - 강조 자막은 대본/srt 줄에 `**…**`, `!…`, `"…"` 로 표시한다 (R-T3, 영상당 5~10회).
3. **project.json 작성**: `python scripts/neogul_edit.py new <폴더>` 로 템플릿을 만든 뒤 규칙집 0장 뼈대대로 장면을 채운다. 장면마다 `start_line`을 대본 줄에 맞추고, 숫자가 나오는 문장은 `cards`/`bars`/`bignum` 슬라이드로 만들고, 말하는 순간에 맞춰 `highlights`/`pointers`의 `at`을 정한다 (R-P2: 8초 넘게 화면 변화가 없으면 안 됨). 형식은 규칙집 부록에 있다.
4. **미리보기**: `python scripts/neogul_edit.py render <폴더>/project.json --preview` 를 실행하면 960x540 preview.mp4가 나온다. 프레임 몇 장을 뽑아 직접 보고 글자 넘침, 박스 위치, 장면 타이밍을 고친다.
5. **최종 렌더**: `render <폴더>/project.json` 을 실행하면 1080p output.mp4가 나온다. 최종 음량 -16 LUFS인지 확인한다 (ffmpeg ebur128).
6. 결과 mp4를 artifacts에 복사하고 대표 프레임 시트를 보여준다.

## 너굴분석 (참고 영상 측정)

ytultra.com Video Downloader(무료)로 영상 URL을 넣어 링크를 받는다. itag=18(360p, 소리 포함)과 itag=136(720p, 영상만)이 있다. REPL `fetch`에 `&range=시작-끝`을 붙여 3MB씩 나눠 받은 뒤 셸에서 합친다. 그다음 `python scripts/neogul_edit.py analyze <영상.mp4>` 를 실행하면 analysis.json, report.md, 프레임 시트, 스펙트로그램이 나온다. 규칙집과 다른 점이 있으면 rules.json 수치를 고친다.

## 주의

- 너굴경제의 마스코트, 일러스트, 실사 클립을 그대로 쓰지 않는다. 사용자 본인의 캐릭터와 저작권 문제가 없는 자료만 쓴다. 따라 하는 것은 편집 문법뿐이다.
- 폰트는 scripts/fonts의 Pretendard(SIL OFL)를 쓴다. 렌더할 때 _build/fonts로 복사된다.
- 필터 경로는 _build 폴더 기준 상대경로로 만들어 Windows 콜론 문제를 피한다. 한글 텍스트는 셸 here-string을 거치지 말고 파일(project.json/srt)로 전달한다.
