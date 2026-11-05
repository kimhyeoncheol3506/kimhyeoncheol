# 개그 쇼츠 만들기 — Claude Code 작업 규칙

이 저장소는 Aside에서 쓰던 영상 스킬 3개를 그대로 옮긴 것이다. 사용자는 주로 폰에서 짧게 지시한다("장도연 짤 5편 더", "너굴편집", "이 유튜브 핵심 뽑아줘"). Aside와 똑같은 결과를 내는 것이 목표다.

## 스킬과 호출 문장

| 지시 | 스킬 | 위치 |
|---|---|---|
| "○○ 짤 N편", "와따마 스타일", "개그 짤" | wadda-shorts | `.claude/skills/wadda-shorts/` |
| "너굴편집", "너굴분석" | neogul-edit | `.claude/skills/neogul-edit/` |
| "fabric", "유튜브 핵심 뽑아줘", "영상 요약" | fabric | `.claude/skills/fabric/` |

지시를 받으면 해당 SKILL.md를 먼저 읽고 그 순서를 빠짐없이 따른다. 규칙집(R-코드)과 사용자 고정 규칙(아래)이 SKILL.md보다 우선이다.

## 사용자 고정 규칙 (wadda-shorts)

- 챕터 제목은 세미콜론을 앞에 붙인다: `;제이미맘`.
- 한 편은 약 2분30초(24초 챕터 6개)다. 장면은 게스트·MC가 크게 웃는 순간(자동자막 `[웃음]`/`[박수]` 밀집)을 고른다.
- 한 편마다 4개를 만든다: `이름 N.mp4`, `이름N.TXT`(제목/설명/해시태그/태그), `이름 N.jpg`(본인 얼굴이 가장 크게 나온 프레임), `쇼츠 일기장.txt` 항목(일시, 제목, 파일, 주제, 영상내용).
- 번호는 기존 파일 다음 번호부터 이어서 붙인다(장도연 6, 7 ...).
- 저장 위치: Windows PC에서 실행하면 `%USERPROFILE%\Downloads\어랏`. 클라우드 세션이면 저장소의 `output/어랏/`에 만들고, 영상(mp4)은 용량 때문에 커밋하지 않는다. TXT, jpg, 일기장만 커밋한다.
- 다 끝나면 알린다: PC에서는 PowerShell 토스트 알림을 보내고, 클라우드에서는 마지막 답변에 결과표를 쓴다.
- 답변은 한국어로 짧게. 결과는 표로 보여준다. 매번 저작권 위험(남의 방송 짜깁기)을 한 줄로 알린다.

## Aside 도구를 Claude Code에서 대신하는 방법

| Aside | Claude Code |
|---|---|
| `youtube.search` / `getTranscript` / `getComments` | `scripts/batch/find_sources.py`(yt-dlp 검색, json3 자동자막, 댓글) |
| ytultra.com 다운로드 | `yt-dlp --download-sections` (dl.py) |
| notification | PowerShell: `New-BurntToastNotification` 또는 `msg *` / 클라우드: 생략 |
| 프레임 직접 보기 | ffmpeg로 프레임 시트(jpg)를 만들어 Read로 열어 검수 |

## 환경 준비 (처음 한 번)

- 필요한 것: Python 3.11+, ffmpeg(6.1 이상), yt-dlp, `pip install "opencv-python-headless<5" numpy` (썸네일 얼굴 인식용).
- Windows: `winget install Gyan.FFmpeg yt-dlp.yt-dlp`.
- 클라우드(Linux): `pip install yt-dlp "opencv-python-headless<5" numpy` 그리고 `apt-get install -y ffmpeg`. 유튜브가 데이터센터 IP를 막으면(Sign in to confirm, 403) 다운로드가 안 된다. 그때는 "PC의 Claude Code에서 실행해야 한다"고 사용자에게 알린다. 다른 영상으로 몰래 대체하지 않는다.
- neogul-edit의 여의도여자 목소리(Voicebox, http://127.0.0.1:17493)는 사용자 PC에서만 된다. 클라우드에서는 음성 단계를 건너뛰고 그렇다고 알린다.
- fabric CLI가 없으면, SKILL.md의 "빠른 방법"처럼 자막을 받아 `patterns/<패턴>/system.md` 지시대로 직접 정리한다. 패턴은 `git clone https://github.com/danielmiessler/fabric` 의 `data/patterns`에 있다.

## 하지 말 것

- 자동자막이 깨진 구간을 지어낸 대사로 채우지 않는다. 그런 구간은 빼고 다음 후보를 쓴다.
- 썸네일에 다른 출연자(서장훈, 강호동 등)를 쓰지 않는다. 반드시 thumbs2.py의 본인 얼굴 대조를 거친다. 새 인물은 `scripts/refs/이름_*.jpg`에 본인 얼굴 사진 1~3장을 먼저 넣는다.
