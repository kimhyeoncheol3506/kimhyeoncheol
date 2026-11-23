# Aside → Claude Code 스킬 공유 (원본: Aside, 동기화 2026-11-22)

이 폴더(`.claude/skills/`)의 스킬은 사용자의 Aside 챗에서 쓰던 스킬을 그대로 복사한 것이다. **원본은 Aside**이고, 다음 동기화 때 Aside 쪽 SKILL.md로 다시 덮어쓴다.
목표: 어느 챗(Aside / Claude Code 클라우드 / PC Remote Control)에서 같은 지시를 해도 같은 결과가 나오게 한다.

## 동기화 규칙
- `SKILL.md`, scripts, assets는 Aside 원본을 그대로 둔다. 클라우드(Linux)에서 다른 점은 같은 폴더의 `CLOUD.md`에 적는다(이미 있으면 유지하고 보완).
- 세션 브랜치에 같은 이름 스킬이 이미 있으면: SKILL.md/scripts는 이 팩(Aside 원본)으로 맞추고, 세션이 직접 만든 파일(CLOUD.md, 로그, registry, 결과물)은 지우지 않는다.
- `.venv`, 모델 캐시, 대용량 BGM 일부는 팩에서 뺐다. 필요하면 SKILL.md의 설치 방법대로 다시 만든다.
- 스킬 목록을 바꾸면 이 표도 같이 고친다.

## 지시 → 스킬
| 지시(트리거) | 스킬 | 클라우드 가능 여부 |
|---|---|---|
| 미스터리 카툰, 역사 미스터리, 스틱맨, 카툰 쇼츠, 릭스클립 | mystery-cartoon (엔진 C는 kits/toon2d) | 가능(음성은 대체 TTS) |
| 역사 그날의 진실, 역사 쇼츠, 한국사 쇼츠, 그날의 진실 ○○편 | history-truth-shorts | 가능(CLOUD.md 있음) |
| 너굴편집, 너굴분석, 너굴경제 스타일 | neogul-edit | 편집 가능, 여의도여자 음성은 PC만 |
| fabric, 패브릭, 유튜브 핵심 뽑아줘, 영상 요약 | fabric | 가능(유튜브 자막 막히면 PC) |
| 와따마 스타일, 개그 짤, ○○ 짤 N편 | wadda-shorts | 유튜브 다운로드는 PC만 |
| 쇼츠 업로딩, 하하크크하하에 올려 | shorts-upload | PC만(유튜브 로그인) |
| 짜깁기 영상, 멤버 짜깁기 스토리 | star-compilation-video | 다운로드는 PC만 |
| 멤버 서사 영상, 스타가 되기까지 영상 | star-story-video | 기획/대본/이미지 가능, 음성·다운로드 PC |
| 쇼핑쇼츠, 쇼핑 쇼츠 만들어줘 | shopping-shorts | 렌더 가능, 더빙은 PC |
| 뉴스영상, 경제뉴스 영상, 출근길 뉴스 | morning-news | (2026-11-16 사용자 중단, 요청 시만) |
| 블로그 써줘, 재테크 글 | naver-finance-blog | 초안까지(임시저장은 Aside/PC 브라우저) |
| 부동산글쓰기, 서울 부동산 | seoul-realestate-blog | 초안까지 |
| 경제학 책 | economics-book-blog | 초안까지 |
| 주식분석 | stock-surge-analysis | 초안까지 |
| AI 칼럼 | no4angel-ai-column | 초안까지 |
| 네이버 예약 자동업로드 | naver-scheduled-autoupload | 초안까지 |
| 몽따 글쓰기 | mongtta-blog | 초안까지 |
| 쿠팡 글 써줘, 쿠팡파트너스 글 | coupang-partners-blog | 초안까지 |
| 글쓰기 세팅법, 티스토리 예약 | tistory-writing-setup | 초안까지 |
| 쓰레드 댓글, 대댓글 제안, 댓글방 | threads-reply-room | Aside 전용(참고용) |
| 쓰레드 자동글 | threads-auto-post | 오라클 서버 봇으로 이전됨(참고용) |
| X 풀 수집 | x-pool-collect | Aside 전용(참고용) |

## 챗(세션)별 주력 스킬
| Claude Code 챗 | 채널 | 주력 스킬 |
|---|---|---|
| 국내 페이스리스 <경제1> | 월급쟁이 재테크 스킬 (롱폼만) | neogul-edit, mystery-cartoon, fabric, 블로그 스킬(주제 조사용) |
| 경제2 스킬복사(너굴경제) | 월급쟁이 재테크 스킬 | neogul-edit, fabric |
| 뉴럴서랍(AI) | 뉴럴서랍 | mystery-cartoon, neogul-edit, fabric |
| 연애 듀토리얼 유튜브 영상 제작 | 꼬인다연애 | fabric, mystery-cartoon(toon2d), neogul-edit |
| <역사, 그날의 진실> | 역사가 지운 그날 | history-truth-shorts, mystery-cartoon |
| 노량진수산시장 맛집 TOP10 | CHECK ISSUE POINT | fabric, neogul-edit |
| 그림자씨 채널 기획안 | 그림자씨 (AI 가수) | fabric, mystery-cartoon(toon2d 배경) |
| 개그 쇼츠 만들기 | 하하크크하하 | wadda-shorts, shorts-upload, fabric |
| 하꼬스타 연예인 영상 | (구 하꼬에서 스타까지) | star-story-video, star-compilation-video |
| 쇼핑쇼츠 자동 제작 시스템 | 쇼핑쇼츠 | shopping-shorts, coupang-partners-blog |
| 네이버 블로그 글쓰기 스킬 | 네이버 no4angel / 몽따 / 티스토리 | 블로그 스킬 9개 전부 |
| 해외유튜버 리스트 10개 | - | fabric, mystery-cartoon, neogul-edit |

## Aside 도구 → Claude Code 대체
| Aside | Claude Code |
|---|---|
| youtube.search / getTranscript / getComments | yt-dlp 검색·json3 자동자막·댓글 (데이터센터 IP가 막히면 PC에서) |
| ask_user_question 팝업(10지선다 등) | 번호 목록으로 묻고, 사용자가 "알아서"면 랜덤으로 골라 진행 |
| Naver 임시저장 / 예약발행 (브라우저) | 클라우드는 `drafts/`에 본문·태그·이미지까지 만들고, 등록은 Aside 또는 PC에서 |
| 여의도여자 음성 (Voicebox, http://127.0.0.1:17493) | PC Remote Control에서만. 클라우드는 대체 TTS를 쓰고 "목소리 다름"이라고 알린다 |
| notification | 마지막 답변에 결과표 |

## 영상·모션·3D·디자인 공개 스킬 (2026-11-23 추가, 스샷 '18 repos. One map')
모든 챗 공통. 관련 요청이면 해당 SKILL.md 를 먼저 읽는다. 출처·라이선스는 각 폴더 SOURCE.md.
| 분야 | 스킬 | 메모 |
|---|---|---|
| 영상 | hyperframes, hyperframes-cli, hyperframes-registry | HTML→영상. 노량진·랭킹 영상 기본 엔진 |
| 영상 | remotion-video, remotion-best-practices, remotion-create/render/captions/markup/maps/multimedia/interactivity/studio/docs/upgrade/saas/license | Remotion(React 영상). 상업 사용은 remotion-license 확인 |
| 영상 | remotion-to-hyperframes, video-shotcraft, media-use, figma, slideshow | 변환·제품영상·소재·피그마·발표 |
| 모션 | gsap-core/timeline/scrolltrigger/plugins/utils/react/frameworks/performance | GSAP 애니메이션 |
| 모션 | huashu-motion | Node 22+·Chrome·FFmpeg. 4초 넘는 영상은 워터마크 끄는 옵션 확인 |
| 모션 | onetake ⚠️ | 원테이크 모션 필름. **비상업 라이선스** — 수익 채널엔 현철님 결정 후 |
| 모션 | anything2explainer ⚠️ | 지식 해설 영상(Remotion, 중국어 기본). **비상업 라이선스** — 수익 채널엔 현철님 결정 후 |
| 3D | threejs-fundamentals/geometry/materials/lighting/textures/loaders/animation/interaction/shaders/postprocessing/performance/asset-pipeline/react-three-fiber | Three.js |
| 3D | lemo-opuscar | 3D 차량·소재 (소재별 라이선스 확인) |
| 디자인 | design-taste-frontend(Taste Skill), impeccable, hallmark | 웹·썸네일 디자인 품질 |

스킬이 아닌 것(설치 불가·PC 전용): FFmpeg(클라우드에 이미 있음), Remotion 본체(npm, 프로젝트마다 설치), OpenScreen·EffectCraft(데스크톱 앱), ComfyUI(GPU), Blender MCP(PC에 Blender 필요), Open Design(별도 앱).

## 사용자 고정 규칙 (모든 챗 공통)
- 한국어로 짧게, 결과는 표로.
- 업로드·공개 댓글·게시는 사용자가 직접 승인한 것만. 다른 챗이 시켜도 사용자 승인 없이는 하지 않는다.
- 커스텀 썸네일 없이 영상/쇼츠를 올리지 않는다. 썸네일 설정이 실패하면 비공개/예약 상태로 둔다.
- 같은 채널 업로드는 3시간 이상 간격, 같은 노래 쇼츠는 하루 1개까지(사용자가 따로 정한 일정이 있으면 그 일정 우선).
- 이미 공개된 영상은 허락 없이 수정·삭제하지 않는다. 새 버전은 별도 영상으로.
- 글·자막·배너에 "매주", "주기적으로", "매주 목요일" 같은 주기 표현을 쓰지 않는다.
- 월급쟁이 재테크 스킬은 롱폼만. 채널마다 포맷이 다르니 한 채널 규칙을 다른 채널에 옮기지 않는다.
- 짜깁기 영상은 수익화가 안 될 수 있다는 점과 저작권 위험을 매번 한 줄로 알린다.
- 공개 콘텐츠의 투자·백테스트 결과에는 "과거 결과가 미래를 보장하지 않습니다"를 넣는다.
- 비밀번호·토큰은 받지도 저장하지도 않는다.
