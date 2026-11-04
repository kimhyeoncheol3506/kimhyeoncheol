# 수집 요청: 어사이드(Aside) 참고 영상 5개 (PC의 Aside 담당)

클라우드 세션에서는 유튜브가 '봇 확인'으로 자막과 스토리보드를 막는다(2026-11-04, 우회하지 않음). 현철님 PC의 Aside 브라우저에서 아래 5개를 받아 `analysis/aside/<영상ID>/`에 넣어 주세요. 받아 오면 클라우드 세션이 분석해서 `projects/aside_neon.yaml` 대본을 보강합니다.

| ID | 채널 | 제목 | 길이 |
|---|---|---|---|
| PqNZ9vLhjDc | 온라인 사업 전략, 온크트리 | AI 브라우저 어사이드(Aside) 7분 완전정복, 챗GPT·클로드랑 같이 쓰세요. | 7:58 |
| uSc7BdOrYxY | 홍아린 AI | AI 브라우저 어사이드 사용법 총정리! 블로그 자동화, 경쟁사 분석, 고객 문의 정리까지 | 11:39 |
| 5EZx-4Op9Po | Jay Choi · 인디해커 라이프 | Aside 핵심 가이드: 한국인 3명이 만든 AI 브라우저, 직접 써보고 솔직하게 정리했습니다 | 12:30 |
| vTUgHm4X_qI | 오늘 쓰는 AI | 요즘 다들 갈아타는 AI 브라우저 어사이드(Aside) 윈도우 설치부터 업무 자동화까지 | 13:42 |
| NdCjNzbrSeY | AI 돈버는 기술, 마브사끼 | [무료 자료 배포] 댓글 자동으로 달고 자료 수집, 엑셀 정리까지! AI 브라우저 어사이드가 다 합니다 | 18:22 |

영상마다 받을 것
1. 한국어 자막(타임스탬프 포함): `<ID>.ko.vtt` 또는 `.srt`
2. 설명란 전체(챕터 포함): `description.txt`
3. 스토리보드나 5초 간격 장면 사진(선택): `sb/`

PC에서 yt-dlp를 쓴다면 아래처럼 받으면 됩니다(영상 본편은 받지 않음).
```
yt-dlp --skip-download --write-info-json --write-auto-subs --sub-langs ko -o "analysis/aside/%(id)s/%(id)s.%(ext)s" https://youtu.be/<ID>
```
