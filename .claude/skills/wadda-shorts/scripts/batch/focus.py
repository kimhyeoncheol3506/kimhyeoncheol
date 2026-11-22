# 인물 집중도: 다운로드한 후보 클립마다 '그 사람이 화면에 나오는 비율'을 재서 segments.json에 focus로 기록
#   python focus.py [이름 ...]      (wadda-shorts\.venv 의 python으로 실행)
#   - 기준 얼굴: scripts/refs/이름_*.jpg 가 있으면 그것, 없으면 후보 클립 전체에서 가장 자주 나오는 얼굴
#     (다른 인물 refs와 같은 얼굴 묶음은 제외)
#   - focus = 1초마다 뽑은 프레임 중 본인 얼굴이 보이는 비율 (가장 큰 얼굴이 본인이면 1, 작게라도 보이면 0.5)
import cv2, glob, json, os, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(sys.argv[0])) if len(sys.argv) else os.getcwd()
B = os.getcwd()
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD, RD = os.path.join(SK, "models"), os.path.join(SK, "refs")
det = cv2.FaceDetectorYN.create(os.path.join(MD, "yunet.onnx"), "", (320, 320), 0.8, 0.3, 5000)
rec = cv2.FaceRecognizerSF.create(os.path.join(MD, "sface.onnx"), "")
S = json.load(open(os.path.join(B, "segments.json"), encoding="utf-8"))


def imread(p):
    return cv2.imdecode(np.fromfile(p, np.uint8), 1)


def faces(img):
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, f = det.detect(img)
    return [] if f is None else [x for x in f if x[-1] >= 0.8 and x[2] >= 40]


def emb(img, f):
    return rec.feature(rec.alignCrop(img, f))


def sim(a, b):
    return rec.match(a, b, cv2.FaceRecognizerSF_FR_COSINE)


def clip_path(c):
    return os.path.join(B, c.get("file") or "clips/%s_%d_%d.mp4" % (c["id"], int(c["in"]), int(c["out"])))


def frames(path, step=1.0):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30; n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(int(fps * 1.0), max(1, n - int(fps * 0.5)), max(1, int(fps * step))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read()
        if ok:
            yield fr
    cap.release()


def reference(person, segs):
    R = []
    for p in glob.glob(os.path.join(RD, person + "_*.jpg")):
        im = imread(p); fs = faces(im)
        if fs:
            R.append(emb(im, max(fs, key=lambda x: x[2] * x[3])))
    if R:
        print("  [%s] refs 사진 %d장 사용" % (person, len(R)))
        return R
    others = []
    for p in glob.glob(os.path.join(RD, "*.jpg")):
        n = os.path.basename(p).split("_")[0]
        if n != person:
            im = imread(p); fs = faces(im)
            if fs:
                others.append((n, emb(im, max(fs, key=lambda x: x[2] * x[3]))))
    E = []
    for c in segs:
        if os.path.exists(clip_path(c)):
            for fr in frames(clip_path(c), 3.0):
                for f in faces(fr):
                    if f[2] >= 70:
                        E.append(emb(fr, f))
    cl = []
    for e in E:
        for c in cl:
            if sim(e, c[0]) >= 0.42:
                c.append(e); break
        else:
            cl.append([e])
    cl.sort(key=len, reverse=True)
    for c in cl:
        who = [n for n, e in others if max(sim(x, e) for x in c[:5]) >= 0.42]
        if who:
            print("  [%s] %d회 얼굴은 %s 라서 제외" % (person, len(c), who[0])); continue
        print("  [%s] 자동 기준: 최다 얼굴 %d회 (얼굴 총 %d개)" % (person, len(c), len(E)))
        return c[:25]
    return []


for person, segs in S.items():
    if sys.argv[1:] and person not in sys.argv[1:]:
        continue
    R = reference(person, segs)
    for c in segs:
        p = clip_path(c)
        if not os.path.exists(p) or not R:
            c["focus"] = None; continue
        tot = sc = 0
        for fr in frames(p, 1.0):
            tot += 1
            fs = faces(fr)
            if not fs:
                continue
            ms = [(max(sim(emb(fr, f), r) for r in R), f[2] * f[3]) for f in fs]
            mine = [a for s_, a in ms if s_ >= 0.38]
            if mine:
                sc += 1.0 if max(mine) >= max(a for _, a in ms) else 0.5
        c["focus"] = round(sc / max(1, tot), 2)
    vals = [c["focus"] for c in segs if c.get("focus") is not None]
    print("%s: 집중도 측정 %d개, 0.4 이상 %d개" % (person, len(vals), sum(1 for v in vals if v >= 0.4)))
json.dump(S, open(os.path.join(B, "segments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
