# projects/media/

Pavo AI, Digen AI, Pollo 등 **외부 사이트에서 만든 영상·이미지**를 넣는 곳. 프로젝트별로 `media/<이름>/` 폴더를 만들어 쓴다.

- 어떤 파일이 필요한지: `python tools/list_media_requests.py projects/<이름>.yaml` (프롬프트·비율·길이 포함)
- 파일이 20MB 를 넘으면 저장소 대신 구글 드라이브에 두고 알려 주세요.
- 만든 사이트·모델·날짜는 YAML 의 `media:` 에 적는다(빌드가 점검). 자세한 내용은 `docs/외부도구.md`.
