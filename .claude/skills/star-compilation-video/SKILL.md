---
name: "star-compilation-video"
description: "아이돌/연예인 한 명의 성공 스토리(과거→현재)를 타인 유튜브 영상을 짧게(3~9초) 짜깁기해서 만드는 스토리 영상. 더빙 거의 없이 날짜+한 줄 자막 캡션으로 흐름을 끌고, Statement(NEFFEX) BGM을 3~4배 크게 깐다. '짜깁기 영상', '원이처럼 ○○도 만들어줘', '멤버 짜깁기 스토리' 요청 시 사용. (긴 내레이션 다큐형은 star-story-video)"
---

# 스타 짜깁기 스토리 영상

첫 완성작: 리센느 원이 「거제소녀원이_짜깁기_Statement.mp4」(4분 31초, 클립 41개) — 사용자 승인 스타일. 예시 EDL: references/woni_edl.json.

## 1. 소스 찾기
- 키워드: 유튜브 검색창 자동완성(`https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&hl=ko&q=<그룹> <이름>` 를 REPL fetch, 또는 사용자가 준 목록) 상위 10개.
- 키워드마다 REPL `youtube.search('<그룹> ' + 키워드)` → 메타데이터(게시일·길이·조회수)로 관련 영상 5개(중복 제외, 다른 아이돌 무관 영상 제외).
- 토크/예능 영상은 `getTranscript(id, {includeTimestamp:true})`에서 핵심 대사 시각을 찾는다. 직캠/무대/쇼츠는 30~40% 지점.

## 2. EDL 작성 (<proj>/edl.json)
- 구성: 콜드오픈(현재 정점 2~3클립) → 검은 카드 "그런데 / 불과 ○년 전…" → 섹션 카드 `{"sec": "2024 · 아무도 모르는 데뷔"}` 4~6개를 시간순(데뷔/무명 → 전환점 → 화제 → 1위 → 현재) → 마지막 검은 카드(제목 + 한 줄 여운).
- 클립 `{"id": 영상ID, "s": 시작초, "d": 3~9, "a": 1(대사 살림)|0(무대·직캠은 0: 노래 음원 Content ID 회피), "cap": ["2025.09", "한 줄 자막"], "src": "채널명"}`. 로컬 파일은 `"local": 절대경로`.
- 캡션: 날짜는 노랑, 문장은 짧게. 명대사는 "\"…\""로 인용. 사실(날짜·조회수·순위)은 메타데이터나 기사로 확인된 것만.
- 카드 `{"card": [큰 글, 작은 글], "d": 초, "voice": "원이 lines 폴더에 있는 기존 TTS 문장"(선택)}`. 새 TTS는 만들지 않는다(더빙 최소).
- 클립 35~45개, 결과 4~6분.

## 3. 렌더
`scripts/compile.py <proj>` 를 CRLF .bat(chcp 65001, PYTHONIOENCODING=utf-8)로 만들어 explorer.exe 로 실행, `compile_out.txt`의 `EXIT` 폴링. 하는 일: yt-dlp 구간 다운로드(dl/ 캐시) → 클립마다 1.06배 줌·세로 영상은 흐린 배경, 하단 캡션 띠, 우상단 "출처: 채널" → 재인코딩 concat → 원본 대사 + Statement(`MUSIC_GAIN` 기본 2.7, 대사 때만 살짝 덕킹) → -15~-16 LUFS.
검수: `ffmpeg -i out/final.mp4 -vf "fps=1/5,scale=320:-2,tile=8x7"` 시트로 검은 화면·캡션 확인. 결과를 Downloads에 `<제목>_짜깁기_Statement.mp4`로 복사.

## 주의
- 클립은 10초 미만, 자막·줌으로 재구성, 출처 표기. 그래도 수익화·Content ID는 보장 못 한다고 알린다. 업로드는 하지 않는다.
- 원본 영상에 박힌 자막과 캡션이 겹치는 곳은 감수(필요하면 클립 교체).
