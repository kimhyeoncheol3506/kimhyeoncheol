---
name: "fabric"
description: "사용자가 \"fabric\", \"패브릭\", \"유튜브 핵심 뽑아줘\", \"영상 요약\"이라고 하거나 유튜브 링크를 주며 핵심/요약/인사이트를 원할 때 실행. danielmiessler/fabric 프롬프트 모음(패턴 265개: extract_wisdom, summarize, extract_insights 등)을 써서 유튜브 영상·글·텍스트에서 핵심만 한국어로 뽑는다."
---

# Fabric (프롬프트 모음집)

이 PC에는 Fabric CLI(winget `danielmiessler.Fabric`), yt-dlp, 패턴 265개(`%USERPROFILE%\.config\fabric\patterns`)가 설치돼 있다. 설정 파일 `.config\fabric\.env`의 기본 모델은 로컬 Ollama `qwen3:8b`다(API 키 필요 없음).

## 빠른 방법 (기본): Aside가 직접 패턴 적용

1. 자막을 가져온다: REPL에서 `youtube.getTranscript(url, {lang:'ko'})`를 쓴다. 한국어 자막이 없으면 기본 자막을 쓴다.
2. 패턴을 고른다 (아래 표). 패턴 원문은 `C:\Users\Admin\.config\fabric\patterns\<패턴>\system.md`에서 read_file로 읽는다.
3. 패턴의 IDENTITY/STEPS/OUTPUT 지시대로 Aside가 직접 결과를 만든다. 결과는 한국어로, 패턴의 섹션 구조를 그대로 지킨다.
4. 결과는 채팅에 마크다운으로 보여 주고, 사용자가 원하면 artifacts에 .md로 저장한다.

| 용도 | 패턴 |
|---|---|
| 유튜브 핵심 전부 (기본) | `extract_wisdom` (요약, 아이디어, 인사이트, 인용, 습관, 사실, 추천) |
| 짧은 요약 | `summarize`, `create_5_sentence_summary` |
| 인사이트만 | `extract_insights` |
| 영상 속 추천/할 일 | `extract_recommendations` |
| 강의·튜토리얼 정리 | `create_summary`, `extract_instructions` |
| 주장 검증 | `analyze_claims` |
| 영상 아이디어 | `create_video_chapters`, `extract_ideas` |

패턴 이름을 모르면 `Get-ChildItem C:\Users\Admin\.config\fabric\patterns -Directory`로 목록을 보고 이름으로 고른다.

## CLI 방법 (사용자가 원하거나 대량 처리할 때)

```powershell
$env:TEMP="<쓰기 가능한 폴더>"; $env:TMP=$env:TEMP   # Aside 셸에서는 필수 (기본 TEMP에선 "no VTT files found")
fabric -y "<유튜브 URL>" -p extract_wisdom -g=ko -o 결과.md
fabric -y "<URL>" --transcript -g=ko        # 자막만
fabric -l                                    # 패턴 목록
fabric -U                                    # 패턴 업데이트
```

- 로컬 qwen3:8b는 느리다(영상 1편에 수 분). 다른 모델을 쓰려면 `fabric --setup`에서 키를 넣거나 `-m <모델>`을 쓴다.
- YouTube rate limit 오류가 나면 `--yt-dlp-args="--sleep-requests 1"`를 붙인다.
- 사용자의 터미널(PowerShell)에서도 같은 명령이 그대로 된다.
