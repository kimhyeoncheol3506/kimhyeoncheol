"""현재 project.json 기준으로 '정확히 그 대사의 음성'이 있고 클립이 없는 장면 ID (쉼표 구분)"""
import json, os, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio")
from studio.keys import raw_name
D = sys.argv[1]
p = json.load(open(os.path.join(D, "project.json"), encoding="utf-8"))
ids = [s["id"] for s in p["scenes"] if os.path.exists(os.path.join(D, "audio", raw_name(s))) and not os.path.exists(os.path.join(D, "clips", s["id"] + ".mp4"))]
print(",".join(ids))
