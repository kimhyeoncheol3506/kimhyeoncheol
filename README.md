# facetube — 얼굴없는 유튜브 자동 편집기

동그라미 캐릭터, 음성 더빙, 강조 자막, 자료화면(출처 표기), 효과음과 배경음을 자동으로 넣고,
완성본의 **오타, 음성 불일치, 소리 끊김, 화면 멈춤, 개인정보**까지 검사해서 mp4로 뽑아줍니다.

```bash
bash setup.sh                                    # 최초 1회
python make_video.py projects/pilot_coffee.yaml  # → output/pilot_coffee/final.mp4
```

| 파일 | 역할 |
|---|---|
| `docs/편집규칙집.md` | 편집 규칙(사람용) |
| `style.yaml` | 같은 규칙(기계용). 수치를 바꾸면 결과가 바뀜 |
| `projects/*.yaml` | 영상 대본(장면, 대사, 자료, 출처) |
| `make_video.py` | 대본 → 더빙 → 렌더 → 믹스 → 검수 |
| `analyze_reference.py` | 참고영상 실측(컷 간격, 자막 위치·크기·색, 음량) → `style.yaml` 반영 |
| `facetube/` | 엔진(캐릭터, 장면, 음성, 오디오, 검수) |
| `.claude/skills/faceless-video` | Claude Code 스킬. "○○ 주제로 영상 만들어줘" 한 문장으로 기획부터 검수까지 |

출력 폴더에는 `final.mp4`, `subtitles.srt`(유튜브 자막용), `qc_report.md`(검수 보고서), `contact_sheet.png`(장면 미리보기)가 생깁니다.

폰트는 Pretendard, Black Han Sans, Jua이고 모두 SIL OFL이라 상업적으로 써도 됩니다. 효과음과 배경음은 코드로 직접 합성하므로 저작권 문제가 없습니다.

## 쇼츠 공장 (세로 1080×1920, 40~50초)
`python shorts/make_short.py projects/demo_short_coffee.yaml` → `output/<이름>/` 에 `final.mp4`, `subtitles.srt`, `description.md`(출처 포함 설명란), `qc_report.md`, `contact_sheet.png`.
"공장이 지키는 원칙" 6가지(오늘 소재 · 40~50초 역할 구조 · 아래 18% 비움 · 목소리에 맞춘 13자 자막 · 내 관점 · 출처 없는 숫자 금지)를 코드가 점검한다. 자세한 내용은 `docs/편집규칙집.md` 13장.
- `shorts/scene.html` + `shorts/render_lib.py`: HTML 한 장에 `window.render(t, dur)` 순수함수를 두고 크로미움으로 프레임을 찍는다(스마트대디 모션 카드 방식). 장면 종류 hook / number / list / reveal. 렌더마다 아래 18% 를 픽셀로 검사한다.
- `facetube/captions.py`: 13자 조각 나누기 + 음성인식 시각으로 자막 시각 맞추기.

## 외부 생성 사이트 연결 (Pavo AI, Digen AI 등)
영상·이미지를 외부 사이트에서 만들어 장면 카드에 넣는다(`type: clip` / `scene.kind: clip`). `python tools/list_media_requests.py projects/<이름>.yaml` 로 사이트에서 만들어 올 **소재 요청서(프롬프트 포함)**를 뽑고, 파일을 `projects/media/` 에 넣고 제작하면 AI 배지·출처·설명란·약관 경고가 자동 처리된다. 자세한 내용은 `docs/외부도구.md`.
