---
name: "star-story-video"
description: "연예인/아이돌 멤버 한 명의 '무명 시절 고충 → 변화 → 스타'까지를 15분 내외 감동 서사 영상으로 만든다(하꼬에서 스타까지 채널용). 유튜브에서 '<그룹> <멤버>' 롱폼·쇼츠 20~30개 스크린샷 시트를 챗에 공유 → 자막·댓글·기사로 재학습 → 기획/대본 → AI 재연 이미지·짧은 출처 클립 → 여의도여자 TTS(Whisper 검수) → BGM·자막 싱크 렌더 → 최근 1주 트렌드 썸네일(큼직한 Black Han Sans) → 업로드 텍스트. '리센느 원이 영상', '미나미 영상 만들어줘', '멤버 서사 영상', '스타가 되기까지 영상' 요청 시 사용."
---

# 스타 서사 영상 (star-story-video)

PC 전용(Voicebox·ffmpeg·yt-dlp). 결과는 Downloads와 세션 artifacts에 저장. 첫 완성작: 리센느 원이 「거제 소녀 원이」(14~15분).

## 0. 준비
- 프로젝트 폴더: `<세션 tmp>\<멤버영문>\` (예: `woni`, `minami`). 하위 `img src bgm thumb out lines`.
- `python scripts/tools.py base-img <proj>` 로 기본 AI 재연 이미지 50장 복사(assets/img). 이미지 이름 목록은 assets/img 파일명.
- 파이썬은 `C:\Users\Admin\.aside\runtime\bin\python.cmd`, PATH 앞에 ffmpeg 폴더(tools.py의 FF) 추가. 한국어 문자열 편집은 PowerShell 대신 파이썬 스크립트로.
- Voicebox(127.0.0.1:17493, 프로필 여의도여자)가 켜져 있어야 한다. 한 번에 하나의 TTS만 돌린다(여러 멤버면 순차 큐).

## 1. 리서치 + 스크린샷 (사용자에게 먼저 보여줌)
1. REPL `youtube.search`로 '<그룹> <멤버>', '<멤버> 쇼츠/무명/눈물/데뷔' 등 6개 쿼리 → 메타데이터(길이·조회수·날짜)로 서사 관련 롱폼 20개 + 쇼츠 10개 고름(브라우저 검색결과 Shorts 탭에서 /shorts/ 링크 수집).
2. 각 영상 watch/shorts 페이지를 열고 영상을 35% 지점으로 이동·음소거·정지 후 스크린샷(광고면 8초 뒤 재시도). 롱폼 crop `960:700:16:62`, 쇼츠 crop `508:904:518:64`(뷰포트 1400x1000) → 번호 붙여 롱폼 10개씩 2장, 쇼츠 5x2 1장 시트로 만들어 최종 답변에 이미지로 첨부.
3. 핵심 영상 10~12개 `getTranscript`(서사·다큐·인터뷰 클립 우선), 상위 댓글 `getComments`(좋아요 수 포함, 댓글 카드용), WebSearch로 기사 확인.
4. 사실 규칙: 날짜·숫자·인용은 기사나 본인 발언 영상으로 확인된 것만. 팬 제작 애니/서사 채널의 각색(예: 지하 연습실)은 쓰지 않거나 기사로 재확인. 확인 안 된 좋아요 수·인용은 빼기. 논란은 다루지 않거나 사실만 짧게.

## 2. 기획/대본 (script.txt DSL)
구성(15분 ≈ 내레이션 100줄·4,000자 + 카드): 0 콜드오픈(현재 정점 장면 → "그런데 ○년 전" 대비 → 타이틀) / 1 출신·꿈 / 2 데뷔 전 시련 / 3 무명기 고충(가장 길게, 눈물 포인트) / 4 전환점의 사람들 / 5 반등 / 6 정점(1위 등) / 7 지금 + 여운. 각 챕터 1.5~2.5분.
- `## n|챕터명|부제`, `> 내레이션`(한 줄=한 TTS=한 자막), `[img 이름 (bw)]`, `[clip 키]`, `[black 큰글|작은글]`, `[quote 문장|누가, 출처]`, `[pause 초]`, `[rank 키]`, `[promise 키]`, `[cmt 댓글|좋아요|유튜브 댓글]`(연속 3개까지 한 화면), `[dday 큰|작은]`, `[title]`, `[end]`.
- quote/promise 뒤 `[pause 2.0]`, 그다음 내레이션이 오면 반드시 `[img ...]`를 먼저 둔다(안 그러면 카드 위에 자막이 깔림). `[title]` 뒤 `[pause 3]`.
- 나이는 "스무 살"처럼 한글로(숫자+살은 오독). 다른 숫자는 tts.py가 읽기 변환.
- 음악만 흐르는 구간 4~5개: 감정 포인트 직후 `[img 이름]` + `[pause 4~6]` (챕터1 끝, 무명기 클라이맥스 뒤, 1위 순간 뒤, 엔딩 직전). 말 없이 화면과 BGM으로 의미를 전달하는 자리.
- 렌더 전 `python scripts/render.py <proj> --dry` 로 길이 확인(목표 14~16분). 모자라면 댓글 카드/인용 추가.

## 3. 소재
- 새 AI 재연 이미지 8~10장: `imagegen.generate` 병렬, 프롬프트 끝에 "얼굴 안 보이게(뒷모습/실루엣), 글자·로고 없음, 다큐 필름톤". 실존 인물 얼굴 생성 금지. 결과 경로를 genpaths.json에 저장 → `tools.py prep-img <proj> genpaths.json` (원본은 artifacts에서 tmp로 이동).
- 실제 클립 5~9개(각 5~7초, 무음, 화면에 출처 표기, 전체의 5% 이하): 타임스탬프 자막으로 장면 찾기 → `tools.py dl`을 담은 .bat을 explorer.exe로 실행해 구간 다운로드 → `tools.py sheet`로 프레임 확인 → clips.json `{"키": {"file": "src/xx.mp4"(또는 절대경로), "ss":, "to":, "label": "채널 · 영상명 (날짜)", "after": "클립 뒤 이어질 이미지"}}`.
- BGM: assets/bgm(YouTube 오디오 보관함, 저작자 표시 불필요) 복사 후 `tools.py bgm <proj>`. music.json 예 `[[0,"snowfall.wav",1.0],[2,"mydearone.wav",1.0],[5,"ripples.wav",1.0],[6,"takingflight.wav",1.0]]` (차분 → 슬픔 → 희망 → 클라이맥스). 새 곡은 Studio 오디오 보관함(채널 하꼬에서 스타까지) 분위기 필터 → 행 hover → '오프라인 저장'.
- config.json: title/subtitle/tagline, ranks(차트·숫자 애니 카드), promises(좌우 대비 명언), pool(챕터별 이미지 순환 목록), credits(출처 목록), boom_prefixes, rank_gold. 예시는 references/woni_config.json.

## 4. 음성 → 렌더
1. `python scripts/tts.py <proj>`를 .bat(chcp 65001, PYTHONIOENCODING=utf-8, PATH에 ffmpeg)으로 만들어 `explorer.exe`로 실행, 로그 폴링(Start-Sleep ≤ 590). 한 줄 40~80초, 100줄 ≈ 1.5~2시간. Whisper 비교 점수 0.88 미만이면 시드 바꿔 재생성(이름 오인식 때문에 0.8대는 정상). 대본 수정 후 다시 실행하면 바뀐 줄만 생성(해시 캐시).
2. `python scripts/render.py <proj> --only 0`로 콜드오픈 시험 렌더 → 프레임 시트 확인 → 전체 렌더(.bat + explorer.exe, 15분 영상 ≈ 20~40분). 자막은 내레이션 줄 타이밍에 자동 싱크, -16 LUFS. BGM 밸런스(사용자 기준): 음악은 크게(config `music_gain` 0.78), 말할 때만 부드럽게 눌림(`duck_ratio` 4, release 1.4초) → 말이 없는 카드·클립·음악 구간에선 음악이 다시 차오름. 내레이션이 음악보다 지나치게 크게 튀지 않게.
3. out/final.mp4 프레임 시트로 검수(자막 겹침, 빈 화면, 클립 출처 표기).

## 5. 썸네일 + 업로드 텍스트
- 최근 1주 트렌드: '<그룹> <멤버>' 검색을 업로드일 7일 이내로 보고(직캠·시상식·컴백·화제 기사) 주제를 고름. 오른쪽은 그 주의 4K 직캠/얼빡캠에서 웃는 얼굴 프레임(로고 영역은 crop으로 제외), 왼쪽은 무명기 AI 재연 이미지 흑백.
- 스타일은 '리센느 신화' 첫 썸네일과 동일: Black Han Sans 큼직한 흰 제목+검은 테두리, 하단 흰 글 → 노란 글, 노란 화살표. `thumb/thumb.json` 작성 후 `tools.py thumb <proj>` (A/B 두 안).
- 업로드 텍스트(제목/설명란/해시태그/태그)를 txt로: 챕터 타임스탬프(out/chapters.txt), 출처, "AI 재연 이미지", "배경음 YouTube 오디오 보관함" 고지.
- 결과물: `<제목>_풀영상.mp4`, 썸네일 A/B, 업로드텍스트.txt를 Downloads와 artifacts에 복사. 편집 영상은 수익화가 보장되지 않고 방송사 클립은 짧게만 쓴다는 점을 매번 알린다.
