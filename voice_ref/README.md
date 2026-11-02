# 아나운서 운율 기준 (여의도여자 개선용)

여의도여자(Voicebox, Qwen3 Sohee)가 기계처럼 들리는 원인을 ElevenLabs 한국어 아나운서 음성과 **숫자로 비교**해 고친다.
목소리 자체를 복제하지 않는다. 쉼·끊어 읽기·억양·속도 같은 **읽는 방식**만 옮긴다.

| 파일 | 내용 |
|---|---|
| `calibration_ko.txt` | 비교용 대본 10문장: 파일럿 문장, 숫자, 연음·경음화·겹받침 낱말 |
| `prev_*.txt/.json` (mp3 는 저장소에 안 올림) | ElevenLabs 한국어 여성 아나운서 미리듣기 3개(Emily 금융뉴스, 이선영 아나운서, Jini)와 측정값. 대본이 서로 달라 **임시 기준** |
| `ref_*.mp3` (예정) | 같은 `calibration_ko.txt`를 ElevenLabs 로 읽힌 기준. 무료 생성이 막혀 아직 못 만듦 |

## 지금 반영된 것 (2026-11-02, 미리듣기 3개 실측 기준)
- 아나운서는 쉼표가 없어도 연결어미(-고 -며 -면서도 -져) 뒤와 길게 시작하는 주제어(~는) 뒤에서 0.3~0.8초 쉰다.
  - `facetube/textnorm.py phrase_breaks`가 그 자리에 쉼표를 넣어 여의도여자에게 읽힌다. 화면 자막은 그대로다.
- 쉼 길이를 쉼표급 0.32초, 문장급 0.6초로 맞춘다(`facetube/voice.py retime_pauses`).
- 장면 대사를 한 번에 읽혀 문장 사이 억양이 이어지게 한다. 문장마다 따로 만들면 매번 처음 톤으로 돌아가 기계처럼 들린다.
- 지시문(instruct)에 측정된 특징을 넣었다: 문장 끝 내려 닫기, 숫자 또박또박, 높낮이 살리기.
- 측정된 목표치
  - 음역 9~13반음
  - 평서문 끝 1~6.5반음 내림
  - 속도 5.3~6.3음절/초

## 현철님 PC에서 할 일 (Voicebox 필요)
```bash
python tools/prosody_ref.py ab voice_ref/calibration_ko.txt --ref voice_ref/prev_emily.json
# → voice_ref/ours_before.wav / ours_after.wav 를 들어 보고 ab_report.md 숫자 비교
```
틀리게 읽는 낱말이 있으면 `pron_dict.yaml`에 `낱말: 소리나는대로` 로 적는다(예정).
