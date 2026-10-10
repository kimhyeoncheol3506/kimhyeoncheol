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
