---
name: ko-tts-pronounce
description: Voicebox(여의도여자·여의도남자·마포남자) 한국어 더빙 전에 대본의 숫자·돈·%·날짜·시각·단위·영어 약어·회사명·어려운 한글 발음을 '읽는 대로' 바꾼다. "발음 사전", "더빙 발음 고쳐줘", TTS 대본 만들 때 사용.
---

# 한국어 TTS 발음 사전

Voicebox(API v0.5.0)에는 발음 사전 기능이 없다. 그래서 대본을 `/generate`에 넣기 직전에 `ko_tts.normalize()`로 바꾼다.

- 사전: `pronounce_dict.json` (words에 `"원문": "발음"` 한 줄 추가하면 바로 적용)
- 변환기: `python ko_tts.py "문장"` / `--file 대본.txt` / `--test`(samples.txt → 발음샘플.md)
- 사전에 없는 영어 단어는 실행 끝에 경고로 나온다 → words에 추가.
- 자막에는 원문, 음성에만 변환문을 쓴다(한글 발음 교정은 '마신는'처럼 소리 나는 대로라 자막에 쓰면 안 된다).
- 파이썬은 `%USERPROFILE%\.claude\skills\wadda-shorts\.venv\Scripts\python.exe`.

- 목소리 3종 공통: 발음 사전은 목소리와 상관없이 모두 거친다. oices.py에 목소리별 instruct·엔진, 여의도남자가 없으면 마포남자로 대체하는 규칙이 있다.
- 목소리 고르기: 환경변수 TTS_VOICE=마포남자 (역사 쇼츠·미스터리 카툰·스타 스토리·출근길 뉴스). 너굴편집은 --voice 마포남자.
