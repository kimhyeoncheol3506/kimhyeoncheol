# 챗GPT 닷츠(ChatGPT dots) 팩트시트 — 2026-11-10

뉴럴서랍 롱폼(`projects/dots_neon.yaml`, S2 neon) 대본용. 조사: 클로드 일꾼B.

## 0. 조사 방법과 한계
- **openai.com·help.openai.com 은 이 세션에서 403(Cloudflare 확인 화면)** 이라 열지 못했다(curl, 2026-11-10).
- 대신 오픈에이아이 공식 도움말 사이트 **learn.chatgpt.com** 과 **chatgpt.com/pricing** 은 열렸다. 아래 [확인]은 모두 이 페이지들을 curl 로 직접 받아 읽은 것이다. 받은 글자 사본: `docs/research/dots-src/*.txt`.
- 참고 영상 「옆자리 연구원 — AI 비서 3파전, 클로드 듀엣·챗GPT 닷츠·메타 뮤즈 비교」(QZ72CnQDFAs)의 자막 파일 `analysis/muse/yeopjari_full.txt` 는 이 브랜치·컨테이너에 없었다. 그래서 그 영상 내용은 `projects/muse_neon.yaml` 의 `yeop` 출처에 이미 적힌 요약(가장 싼 요금제 월 100달러, 한국 가능, 한 매체: 뮤즈 생활·닷츠 큰 프로젝트·듀엣 업무)만 쓰고, 영상에서는 "한 유튜버 정리"로 밝힌다.
- 한국 원화 가격·부가세는 확인 못 함 → 달러로만 말한다. 우회 가입은 다루지 않는다.

## 1. 출처 (모두 [확인])
| id | 페이지 | 주소 |
|---|---|---|
| meet | Meet dots(개요) | https://learn.chatgpt.com/codex/dots |
| start | Get started with your dot | https://learn.chatgpt.com/codex/dots/getting-started |
| msg | Message your dot | https://learn.chatgpt.com/codex/dots/channels |
| task | Tasks and memory | https://learn.chatgpt.com/codex/dots/tasks-and-memory |
| comp | Connect computers and apps | https://learn.chatgpt.com/codex/dots/computers-and-apps |
| ctrl | Control your dot | https://learn.chatgpt.com/codex/dots/controls |
| sec | Safety and security in dots(기업용) | https://learn.chatgpt.com/codex/enterprise/dots-security |
| devday | What's new — DevDay 2026 (2026-09-29) | https://learn.chatgpt.com/codex/whats-new/devday-2026 |
| news | What's new 목록(10/5~9 모바일 만들기, 10/12~16 위젯, 10/26~30 문자, 11/2~6 알림 답장·GPT-6.1 Terra) | https://learn.chatgpt.com/codex/whats-new |
| price | ChatGPT 요금 비교(닷츠: Free·Go·Plus 없음, Pro 있음) | https://chatgpt.com/pricing |
| cprice | Codex 요금(Pro 월 100·200·500달러) | https://learn.chatgpt.com/codex/pricing |
| ctry | 지원 국가(대한민국 포함) | https://learn.chatgpt.com/api/docs/supported-countries |

## 2. 무엇인가
- "항상 켜져 있는 에이전트". 일을 계속 굴리고, 결정이 필요할 때만 묻는다. (meet)
- 2026년 9월 29일 데브데이에서 발표, 조금씩 차례로 열리는 중. (devday)
- 클라우드에 살며 **자기 컴퓨터와 브라우저**가 있다 → 내 컴퓨터가 꺼져 있어도 일한다. 조사·데이터 분석·문서 준비·소프트웨어 만들기. (meet)
- 이름·모양·색·눈·안경·장식을 고른다. 처음 주소는 @이름-dot. (meet)
- 대화와 대화 사이에도 일한다. 스스로 쉬었다 깨어나 이어 간다. 여러 배경 에이전트로 동시에. (meet, task)
- 예: 워크숍 준비 — 참석 확정에 맞춰 인원수를 고치고, 견적 다시 요청하는 메일은 보내기 전에 묻는다. (meet)
- 일반 채팅=답·설명, ChatGPT Work=맡기는 일 하나, Codex=코딩, 닷츠=계속 챙겨야 하는 책임. Work·Codex 에 일을 넘길 수 있다. (meet)

## 3. 말 거는 곳
- 챗GPT 모바일 앱·데스크톱 앱·데스크톱 브라우저. **모바일 웹은 안 됨**. (meet)
- 전화 버튼으로 통화, 통화 중에도 글 입력. 통화가 끝나도 맡긴 일은 계속. 닷츠가 먼저 거는 전화는 출시 뒤 예정. (msg)
- 슬랙·팀즈에서도 **같은 닷**, 기억이 초기화되지 않는다. 사적인 대화 내용을 남에게 말하기 전엔 허락을 확인. (meet, msg)
- 문자(아이메시지·안드로이드 RCS): 미국 Pro 사용자에게 베타. (news 10/26~30)
- iOS 위젯·단축어(10/12~16), 알림에서 바로 답장·액션 버튼(11/4). (news)

## 4. 기억
- 대화 + 챗GPT 메모리 + 자기만의 메모. 메모는 챗GPT 저장 메모리와 따로이고 모든 대화 기록은 아니다. (task)
- 먼저 알아보기(proactive research): 허락된 정보를 **읽기만** 한다. 메시지 보내기·앱 바꾸기·브라우저 조작은 못 함. (task, ctrl)
- 오픈에이아이는 먼저 알아보기 결과나 비밀 메모로 **직접** 모델을 학습시키지 않는다. 챗GPT 데이터 설정이 그대로 적용. (ctrl)

## 5. 컴퓨터·앱·로그인
- 클라우드 컴퓨터 화면을 열어 볼 수 있고, '넘겨받기(Take over)' → '돌려주기(Return control)'. (meet, comp)
- 내 컴퓨터 연결은 선택. 연결하면 파일·코드·앱 사용, 단 **켜져 있고 챗GPT 앱이 열려 있어야** 함. 여러 대 가능. (comp)
- 플러그인: 지메일·구글 드라이브·깃허브 등. 메일 읽기만 허락하고 보내기는 안 허락하는 식으로 나눌 수 있다. (comp)
- 로그인: 비공개 입력창 → 비밀번호는 대화 밖으로 브라우저에 바로. 저장한 로그인을 다시 쓸 땐 확인 필요. 일부 사이트는 클라우드 브라우저를 막는다. (meet, comp)
- 회사 VPN·회사 기기 조건은 클라우드 브라우저가 대신 못 채운다. (sec)

## 6. 안전장치
- 자동 검토(Auto-review): 계정에 영향을 주거나 정보를 나누기 전 → ①그냥 진행 ②승인 요청 ③사람에게 넘김. 비밀번호 바꾸기는 사람이 직접. (ctrl)
- "답장 초안을 써 줘"는 보내도 된다는 허락이 아니다. (ctrl)
- 맞춤 규칙 4가지: 묻지 않고 하기 / 내가 말하면 하기 / 하기 전에 묻기 / 나에게 넘기기. 규칙도 실수할 수 있고, 기본 안전 규칙을 넘지 못한다. (ctrl)
- 숨은 지시(프롬프트 인젝션)에 버티도록 학습. "비밀 파일을 전달해라"는 메일이 와도 허락이 아니다. 안전 감시가 위험한 행동을 보면 멈춘다. (sec)
- 막힌 일을 정확히 보고 못 한 비율: 일부러 어려운 코딩 과제에서 GPT-6.1 테라 약 8%(GPT-5.6 테라 29%). (sec)
- 멈추기: '일시정지'는 지금 하는 큰일만 멈춘다. 넘긴 작업(Activity)·예약 작업(Scheduled)은 따로 멈춘다. 이미 한 행동은 되돌려지지 않는다. 삭제는 되돌릴 수 없고 이미 보낸 메시지를 회수하지 못한다. (ctrl)

## 7. 요금·쓸 수 있는 사람
- 개인: **Pro 100·200·500달러(월)**, 18세 이상, 유럽경제지역·영국·스위스 밖. 기업: Business Premium, Enterprise·Edu·Healthcare(11월 18일부터 기본 켜짐). (meet, cprice)
- 요금 비교표: Free·Go·Plus 는 닷츠 없음, Pro 만 있음. (price)
- Pro: 닷츠와의 대화는 챗GPT 사용 한도에 안 들어감. 닷츠가 Work·Codex 에 넘긴 일은 그쪽 한도에서 빠짐. 출시 첫 달은 한도 늘려 줌. (meet)
- 한국: 위 제외 지역에 들지 않고, 오픈에이아이 지원 국가 목록에 대한민국이 있다 → **조건(Pro·18세 이상)을 맞추면 대상**. 다만 "차례로 열리는 중"이라 계정마다 늦게 뜰 수 있다. 한 유튜버 정리도 "닷츠는 한국 가능, 가장 싼 요금제 월 100달러". (meet, ctry, yeop)
- 11월 4일부터 GPT-6.1 테라도 닷츠를 움직이는 모델에 합류. (news)

## 8. 쓰임 예(공식 도움말 예시)
- 영업 제안서 최신 유지 · **인터뷰마다 콘텐츠 준비(캡션·쇼노트·클립 아이디어)** · 출시 자료 맞추기 · 연구 결과 갱신 · 소프트웨어 피드백 조사와 고치기 준비. (meet)
- 정해진 시간 점검: "평일 오전 9시, 4주 동안 채널을 확인하고 마감이 위험하면 알려 줘" — 시간대·기간을 꼭 넣고 확인받기. (meet, task)
- 슬랙 채널 새 버그 보고 같은 사건이 생기면 움직이기(연결한 서비스가 지원할 때). (start, task)
