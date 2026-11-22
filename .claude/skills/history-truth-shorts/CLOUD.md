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
