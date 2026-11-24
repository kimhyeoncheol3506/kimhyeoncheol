---
name: sfx-library
description: 실제 녹음 효과음·배경음악 라이브러리(라이선스 증빙 포함, 오프라인). neogul-edit의 합성 효과음(impact·whoosh·pop·click·ding)을 실제 녹음으로 바꾸는 프리셋(basic·money·tension), 돈·종이·UI·휙·코믹 효과음 검색, 설명 영상용 배경음악, 설명란 출처 문구 자동 생성. '효과음', '배경음악', 'BGM', '소리 바꿔', '효과음 업그레이드', '음악 출처' 요청에 사용.
---

# sfx-library — 효과음·배경음악 라이브러리

출처: [stickman-video-director](https://github.com/kaomei/stickman-video-director) (MIT, commit 1028782)의 `b-audio-library` 중 **경제 설명 영상에 맞는 부분만** 골라 넣었다. 녹음 파일은 원본 그대로이고, 각 파일의 라이선스는 저장소 코드 라이선스와 별개로 따라간다.

| 종류 | 개수 | 라이선스 |
|---|---|---|
| 효과음(충격·UI 피드백·UI 전환·휙·지우기·돈·동전·종이·카메라·전화·스위치·발소리·코믹) + 짧은 음악 스팅 | 452 | 거의 전부 CC0(저작자 표시 불필요). 일부 CC BY 3.0 → `credits`가 알려 줌 |
| 배경음악 6곡: Cipher·Getting it Done(정보), Easy Lemon(따뜻·내레이션용), Investigations(미스터리), Decisions(긴장), Local Forecast - Elevator(가벼움) | 6 | CC BY 4.0, Kevin MacLeod — **설명란에 출처 필수** |

용량 약 49MB. 목록은 `catalog.json`, 라이선스 원문은 `licenses/`, 취득 증빙은 `evidence/`.

## 명령 (`python3 .claude/skills/sfx-library/scripts/sfxlib.py ...`, ffmpeg만 필요)

```bash
python3 scripts/sfxlib.py preset basic <출력폴더>     # neogul-edit 효과음 5종 wav + sfx_files.json + CREDITS.txt
python3 scripts/sfxlib.py search coin                  # 키워드 검색(영문 태그: money, paper, whoosh, click, impact …)
python3 scripts/sfxlib.py list --kind music
python3 scripts/sfxlib.py export bgm-easy-lemon,kenney-rpg-handle-coins <폴더>   # 파일 + 라이선스 + CREDITS.md
python3 scripts/sfxlib.py credits bgm-easy-lemon       # 설명란용 출처 문구
```

## neogul-edit에 끼우기 (편집기 코드는 고치지 않는다)

neogul-edit은 `project.json`의 `"sfx_files"`로 효과음 5종을 바꿔 끼울 수 있다(규칙집 R-S2). `preset`이 만든 `sfx_files.json` 내용을 그대로 넣으면 된다. 프리셋은 최고 레벨을 맞춰 두어서 `rules.json`의 효과음 볼륨과 -16 LUFS 마스터링이 그대로 통한다(테스트: 아이슬란드 편 70초 구간, 통합 -16.1 LUFS 유지).

| 프리셋 | 언제 | impact(훅) | whoosh(B-roll) | pop(강조) | click(구독) | ding(큰 숫자) |
|---|---|---|---|---|---|---|
| `basic` | 기본 설명 영상 | 부드럽고 묵직한 충격 | 짧은 휙 | 톡(drop) | 딸깍 | 확인음 |
| `money` | 예금·월급·환율 편 | 〃 | 〃 | 〃 | 〃 | **동전 소리** |
| `tension` | 위기·폭락·뱅크런 편 | **펀치 충격** | 조금 긴 휙 | 〃 | 〃 | **낮은 종소리** |

배경음악은 neogul-edit의 `"bgm"` 키에 파일 경로를 넣는다(기본은 인트로·아웃트로에만 깔림, `bgm_volume` 0.06). 쓴 곡의 `credits` 문구를 설명란에 꼭 붙인다.

## 소리 연출 원칙 (원본 sound-system에서 우리 영상에 맞게 추린 것)

1. **소리는 화면의 사건에 붙인다.** 빨간 박스가 뜨는 순간, 숫자가 찍히는 순간, 장면이 바뀌는 순간. 사건 없는 곳에 소리를 넣지 않는다.
2. **모든 컷에 휙 소리를 넣지 않는다.** 일반 컷·확대에는 소리가 필요 없다. 훅·B-roll 진입처럼 의미 있는 전환에만.
3. **목소리가 주인공.** 음악은 목소리 아래, 효과음은 짧게. 말이 안 들리면 효과음·음악을 줄이지, 목소리를 빠르게 하거나 다시 만들지 않는다.
4. **같은 소리를 빠르게 반복하지 않는다.** 연달아 나오는 강조는 한두 번만 소리를 주거나 다른 번호 소리를 쓴다.
5. **코믹 효과음(boing·squeak)은 마스코트 장면 등 웃는 순간 한 번만.** 위기·손실 이야기에는 쓰지 않는다.
6. **슬픈 음악을 모든 장면에 깔지 않는다.** 감정은 대본이 만든다.
7. **출처는 소리와 함께 다닌다.** CC BY 파일(음악 전부, 일부 효과음)을 쓰면 `credits` 문구를 설명란에 넣고, 자르고·페이드한 사실도 적는다(문구에 포함됨).
8. 라이브러리에 없는 소리가 꼭 필요하면 저작권이 확인된 소스만 쓰고, 이 폴더 규칙대로 라이선스를 함께 보관한다.

## 주의

- 녹음 파일을 이 폴더에서 수정하지 않는다(가공본은 프로젝트 폴더에 만든다).
- 라이브러리 원본의 나머지(약 250MB: 동물·날씨·부엌·문소리, 음악 25곡 등)와 스틱맨 애니메이션 엔진은 넣지 않았다. 필요하면 위 저장소에서 같은 방식으로 골라 추가한다.
