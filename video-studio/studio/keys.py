"""장면 음성 캐시 파일 이름 (Voicebox·클라우드 엔진 공통). 대사·목소리·톤이 같으면 같은 파일을 재사용한다."""
import hashlib


def raw_name(scene: dict) -> str:
    voice = scene.get("voice", "여의도남자")
    key = hashlib.sha1(f"{voice}|{scene.get('instruct')}|{scene['text']}".encode()).hexdigest()[:12]
    return f"{scene['id']}_{key}.wav"
