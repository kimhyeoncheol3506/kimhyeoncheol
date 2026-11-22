---
name: "mystery-cartoon"
description: "역사·미스터리 카툰 쇼츠(릭스클립/Ricks Clips 스타일)를 코드로 만든다. 3가지 엔진: A 3D 콩머리 카툰(three.js), B 3D 스틱맨+단어자막(Remotion), C 2D 패럴랙스 카툰(toon2d, 가장 빠름). '미스터리 카툰', '역사 미스터리 영상', '스틱맨 영상', '카툰 쇼츠', '릭스클립 스타일' 요청 시 사용. 한국어 대본+여의도여자 음성+한글 자막 지원."
---

# 미스터리 카툰 쇼츠 (A/B/C 3엔진)

출처: ReachMora cartoon-short-kit(A), Jacksons AI 마스터 프롬프트(A의 흰머리 스틱맨 변형), ProvenTube Stick3D-Pack v4(B), mr miro toon2d-shorts 1.1.1(C). 모두 MIT/무료. 키트는 `kits/` 에 한국어 패치된 상태로 있다. 작업은 항상 세션 tmp에 복사해서 한다(스킬 폴더는 읽기 전용 취급).

## 공통 흐름
1. 주제: 아이디어 10개를 팝업(ask_user_question)으로. 사용자가 "알아서"면 랜덤 결정. 실화면 웹검색으로 사실 확인, 정설/논란/전설 구분(예: "에펠탑 두 번 판 남자"의 두 번째 판매는 신화, 실제론 미수).
2. 대본: 훅(역설을 사실처럼) → 배경 → 확대 → 반전, 마지막 문장이 반전. 한국어 약 6~7음절/초. 문장 단위로 줄바꿈.
3. 음성: `kits/make_voice.py` 의 SCRIPTS 를 바꿔 실행(Voicebox 켜기: `explorer.exe "C:\Program Files\Voicebox\voicebox.exe"`, 프로필 여의도여자, 문장당 약 30~45초). 결과: `voice.wav`, `script.txt`, `timings.json`(단어 시작/끝, 음절 비례 추정이라 ±0.1~0.2초 오차). 오래 걸리면 explorer.exe로 띄운 CRLF .bat 으로 백그라운드 실행.
4. 엔진 선택(아래) → 스틸 시트 확인 후 수정 → 풀 렌더 → `artifacts/` 에 mp4 + 1fps 콘택트 시트로 눈 검사(ffprobe 해상도·길이·오디오, 멈춤/검은 화면).
5. 업로드는 사용자 명령이 있을 때만.

## 엔진 비교 (이 PC 실측, 2026-11-20)
| 타입 | 엔진 | 출력 | 렌더 속도 | 강점 | 약점 |
|---|---|---|---|---|---|
| C 2D 카툰 | `kits/toon2d` (파이썬 skia) | 1080x1920 | 15초 영상 22초 | 가장 빠름, 완성도 안정, 세트 11종·캐릭터 12종 내장, 자막 자동 | 세트에 없는 장소는 직접 그려야 함 |
| B 3D 스틱맨 | `kits/stick3d` (Remotion+three) | 720x1280 | 15초 영상 약 1분 | 연출 자유도 최고, 소품/숫자 연출, 단어 자막 | 장면마다 TSX 코딩 필요 |
| A 3D 콩머리 | `kits/cartoon3d` (three.js+Playwright) | 1080x1920 | 프레임당 약 1.2초(12초=7분) | 잉크선 3D 세계, 영화 같은 카메라, 음악·효과음 합성 | 기존 에셋은 로마뿐, 새 세계는 코딩 부담 큼, 빈 장면이 밋밋해지기 쉬움 |
기본 추천: 빠른 양산은 C, 퀄리티 1편은 B, 고대 로마/서양 고전 소재는 A.

## C: toon2d (kits/toon2d)
- venv 파이썬(skia-python, numpy, imageio-ffmpeg, Pillow). `PYTHONUTF8=1`, PYTHONHOME 제거. 한국어 패치 적용됨: 자막 폰트 Pretendard ExtraBold, `words.norm` 이 한글 유지.
- `python t2d.py words P --from timings.json` → `plan P` → `stills P` → `render P --workers 6 --budget 500`(DONE까지 반복) → `join P` → `check P`.
- storyboard.json 문법은 `docs/LIBRARY.md`, `docs/STYLE.md`, 예시 `examples/celeste_storyboard.json`. `"lowercase": false`. sign:텍스트에 한글 가능.
- 한국사 팩(2026-11-21): 한국 의상 캐릭터 11종(jking, official, scholar, general, soldier ...)과 한국 세트 10종(palace_hall, river_camp, sea_battle, map_table ...)이 엔진에 들어 있다(`toon2d/korea_in.py`, `korea_out.py`, character.py). 사용법·배치 요령은 `../history-truth-shorts/SKILL.md` 5절.
- 자막(70% 높이)이 얼굴을 가리면 그 key 의 frame 을 `[cx, cy, h]` 로 바꿔 인물을 위로.

## B: Stick3D (kits/stick3d)
- `engine/` 에서 `npm install` 후 사용(node_modules 미포함). PATH 앞에 `C:\Program Files\nodejs`. 렌더는 `--gl=angle`(이 PC GPU OK).
- 규칙: `MASTER-PROMPT.md`, `rules/*.md`. 새 영상은 `engine/src/videos/<Name>.tsx` (참고: `Voynich.tsx` 한국어 예시, `NvidiaV4.tsx`), `Root.tsx` 에 등록(durationInFrames = ceil(음성초*30)).
- 입력 준비는 `prep_b.py` 패턴(timings.json → public/words.json·script.json, voice.wav, Pretendard 폰트, `tools/mix_sfx.py` 로 효과음 4개 정도). 스틸은 `scripts/stills_win.mjs`(원본 stills.mjs 는 리눅스 경로 하드코딩).
- `npx remotion render <Id> out.mp4 --gl=angle --concurrency=4` (run_b.bat 참고), 마지막에 loudnorm -14 LUFS.

## A: 3D 콩머리 (kits/cartoon3d)
- 엔진 파일 `web/`(three r160, toon.js 빌드됨). `npm i playwright` 후 `CHROME=C:\Users\Admin\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe` 로 `node render.mjs frames "0-N"` (render.mjs 에 executablePath 패치됨). 풀 렌더는 run_render.bat 처럼 explorer.exe 로.
- 새 이야기 = `web/story.js` 재작성(SHOTS, camAt, lightFor, worldAt, actorsAt, fxAt). 현재 story.js 는 로마 제9군단 샘플, `story_soldier_example.js` 는 원본 예시. 캐릭터 의상은 `roman.js` OUTFITS. 수정 후 `toon.js = toonbase.js + roman.js` 재결합.
- Jacksons 변형(흰 원형 머리, 검은 막대 팔다리, 코 없음, 신발 없음)은 roman.js 그리기를 바꿔서 적용.
- 소리: `audio.py`(DUR, 큐 테이블 수정, voice.wav 사용) → mix_raw.wav. 자막은 `caps_example.ass` 형식(ASS, Pretendard, pos 540,1344, 팝 120ms)으로 ffmpeg 번인. 마무리 loudnorm -14 LUFS, H.264 CRF 17.
- 함정: 모든 샷에 인물·소품을 두기(빈 들판/안개만 있으면 밋밋), 카드는 항상 정면이라 걸어가는 뒷모습 불가.

## 수익화·저작권 메모
- 전부 직접 생성한 그림·음성·효과음이라 저작권 위험 낮음. 음악은 사용자가 준 라이선스 음원만.
- 같은 캐릭터·구도로 찍어내면 유튜브 '반복·양산형 콘텐츠'로 수익화 거절 위험 → 영상마다 세트·조명·연출 변경, 채널 고유 캐릭터/스타일 시트 만들기.
- 공개 콘텐츠의 역사 사실은 출처 확인 필수.
