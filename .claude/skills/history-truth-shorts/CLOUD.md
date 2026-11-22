# Claude Code 클라우드(리눅스)에서 실행할 때의 차이

PC가 꺼져 있어도 이 문서대로 하면 영상 제작 전체가 클라우드에서 끝난다.

## 설치 (세션마다 한 번, 이미 되어 있으면 생략)
```bash
cd .claude/skills/mystery-cartoon/kits/toon2d
python3 -m pip install -r requirements.txt edge-tts imageio-ffmpeg Pillow
python3 t2d.py doctor          # DOCTOR OK 가 나와야 함. skia 가 libEGL 을 못 찾으면: apt-get install -y libegl1 libgl1 libfontconfig1
```
- `python` 대신 `python3`. 경로는 `/` 구분.
- 엔진 경로: `.claude/skills/mystery-cartoon/kits/toon2d` (tools 스크립트는 자동으로 찾음, 다르면 `TOON2D_DIR` 환경변수).

## 음성 (Voicebox 없음)
- `python3 .claude/skills/history-truth-shorts/tools/cloud_voice.py <프로젝트> --voice ko-KR-SunHiNeural --rate +8% --target <음성목표초>`
- 남성 내레이션이 어울리면 `ko-KR-InJoonNeural`. 목소리가 PC 버전(여의도여자)과 다르다는 점을 결과 보고에 적는다.
- edge-tts 가 네트워크 차단 등으로 실패하면 gTTS 로 같은 흐름을 만들고, 그것도 안 되면 무음 자막형(`t2d.py silent`)으로 만들고 사용자에게 보고.

## 렌더
- CPU 코어 수 확인(`nproc`) 후 `--workers` = 코어 수, 명령 제한시간이 짧으면 `--budget 200` 으로 DONE 까지 반복.
- 160초 영상은 4800프레임 → 코어 4개 기준 대략 15~25분.

## 결과물
- 프로젝트 폴더: `history/<NN>_<제목>/` (script.txt, factsheet.md, storyboard.json, voice.wav, timings.json …). `.cache`, `chunks`, `stills` 는 커밋하지 않는다(.gitignore).
- 최종본: `output/<NN>_<제목>.mp4` 는 깃 100MB 제한 때문에 **45MB 이하로 재인코딩**해서 커밋:
  `ffmpeg -i final.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart output/NN_제목.mp4` (넘으면 crf 28)
- 썸네일 `output/<NN>_<제목>_thumb.jpg`, 업로드 TXT `output/<NN>_<제목>.txt`, 팩트 시트 `output/<NN>_<제목>_factsheet.md` 도 커밋 후 push.
- 업로드(유튜브)는 하지 않는다. 사용자가 명령할 때만.

## 클라우드 프록시 인증서 문제 (세션 브랜치에서 확인한 개선점, 2026-11-20)
클라우드에서 `cloud_voice.py` 를 그대로 돌리면 edge-tts 가 `CERTIFICATE_VERIFY_FAILED (self-signed certificate in certificate chain)` 로 실패한다.
edge-tts 가 certifi 인증서만 쓰기 때문이다(`edge_tts/communicate.py` 의 `_SSL_CTX`). `SSL_CERT_FILE` 환경변수만으로는 안 된다.
해결: `tools/cloud_voice.py` 의 `import edge_tts` 바로 아래에 다음 4줄을 넣고, 실행할 때 `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt` 를 붙인다.
```python
if os.environ.get("SSL_CERT_FILE") and os.path.exists(os.environ["SSL_CERT_FILE"]):
    import ssl, edge_tts.communicate as _ec
    _ec._SSL_CTX = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])
```
```bash
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 .claude/skills/history-truth-shorts/tools/cloud_voice.py <프로젝트> --voice ko-KR-InJoonNeural --rate +28% --target 158
```
- 실측(위화도 1편): 원본 218초 대본을 +8%로 합성하면 1.38배 압축이 필요해 너무 빨랐다. 대본을 15% 줄이고 edge-tts 자체 속도 +28%, 추가 atempo 1.12배로 맞추는 게 자연스러웠다(atempo 는 1.15 이하 권장).
- toon2d 메모: 지도·팻말 프레임은 엔진 최소 h 800 이 적용된다(더 작게 써도 800으로 잡힘). 장군 투구 귀덮개가 들고 있는 팻말을 가리므로, 결말 팻말은 옆 병사/선비가 들게 한다.
- 새 도구(2026-11-22 Aside 동기화) 클라우드 메모:
  - `tools/thumb_name.py`: 폰트 경로 `FD` 가 Windows(Aside tmp) 고정. 클라우드에서는 `.claude/skills/mystery-cartoon/kits/toon2d/toon2d/fonts` 를 쓰도록 실행 전 작업 복사본에서 FD 만 바꿔 쓴다(원본 SKILL/스크립트는 수정하지 않음).
  - `tools/bgm_mix.py`: `music/T_*.mp3`, `S_*.mp3` 음원이 팩에 없다(유튜브 오디오 보관함 음원, PC 보관). 클라우드에서는 사용자가 음원을 레포에 넣어 주거나 `BGM_DIR` 로 지정할 때만 쓰고, 없으면 BGM 없이 만든다고 보고. 음원을 내려받지 않는다.
