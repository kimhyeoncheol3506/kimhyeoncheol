# 썸네일 v2: 기준 얼굴(refs/이름_*.jpg)과 같은 사람인 얼굴 중 '가장 크게' 나온 순간을 썸네일로 저장
#   사용: python thumbs2.py [--check] ["김원훈 1" ...]
import cv2, glob, os, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(HERE, "models"); RD = os.path.join(HERE, "refs")
OUT = os.path.join(os.path.expanduser("~"), "Downloads", "어랏")
BAND_Y, BAND_H = 360, 520
det = cv2.FaceDetectorYN.create(os.path.join(MD, "yunet.onnx"), "", (320, 320), 0.8, 0.3, 5000)
rec = cv2.FaceRecognizerSF.create(os.path.join(MD, "sface.onnx"), "")


def imread(p):
    return cv2.imdecode(np.fromfile(p, np.uint8), 1)


def faces(img):
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, f = det.detect(img)
    return [] if f is None else list(f)


def emb(img, f):
    return rec.feature(rec.alignCrop(img, f))


def refs_of(person):
    E = []
    for p in glob.glob(os.path.join(RD, person + "_*.jpg")):
        im = imread(p)
        fs = faces(im)
        if fs:
            f = max(fs, key=lambda x: x[2] * x[3])
            E.append(emb(im, f))
    return E


if "--check" in sys.argv:   # 기준 얼굴 크롭 저장해서 눈으로 확인
    for p in glob.glob(os.path.join(RD, "*.jpg")):
        im = imread(p); fs = faces(im)
        if fs:
            x, y, w, h = [int(v) for v in max(fs, key=lambda x: x[2] * x[3])[:4]]
            cv2.imencode(".jpg", im[max(0, y):y + h, max(0, x):x + w])[1].tofile(p.replace(".jpg", ".face.png").replace(RD, os.path.join(RD, "..", "refs_check")))
    sys.exit()

def dominant(person):
    """refs 사진이 없을 때: 그 인물 영상들에서 가장 자주 나오는 얼굴 = 본인 (자동 기준)"""
    embs = []
    for f in sorted(glob.glob(os.path.join(OUT, person + " *.mp4"))):
        cap = cv2.VideoCapture(f); fps = cap.get(cv2.CAP_PROP_FPS) or 30; n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for i in range(int(fps), n, int(fps * 2)):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read()
            if not ok:
                continue
            band = fr[BAND_Y:BAND_Y + BAND_H]
            for fc in faces(band):
                if fc[2] >= 80 and fc[-1] >= 0.85:
                    embs.append(emb(band, fc))
        cap.release()
    clusters = []
    for e in embs:
        for c in clusters:
            if rec.match(e, c[0], cv2.FaceRecognizerSF_FR_COSINE) >= 0.42:
                c.append(e); break
        else:
            clusters.append([e])
    clusters.sort(key=len, reverse=True)
    # 다른 인물 기준 얼굴(refs의 다른 이름)과 같은 사람인 묶음은 제외 (예: 엄지윤 영상의 김원훈)
    others = []
    for rp in glob.glob(os.path.join(RD, "*.jpg")):
        if os.path.basename(rp).split("_")[0] == person:
            continue
        im = imread(rp); fs = faces(im)
        if fs:
            others.append((os.path.basename(rp).split("_")[0], emb(im, max(fs, key=lambda x: x[2] * x[3]))))
    kept = []
    for c in clusters:
        who = [n for n, e in others if max(rec.match(x, e, cv2.FaceRecognizerSF_FR_COSINE) for x in c[:5]) >= 0.42]
        if who:
            print("  [%s] %d회 나온 얼굴은 %s 로 판단해 제외" % (person, len(c), who[0]))
            continue
        kept.append(c)
    clusters = kept
    if not clusters:
        return []
    print("  [%s] 자동 기준: 얼굴 %d개 중 최다 인물 %d회 (2위 %d회)" % (person, len(embs), len(clusters[0]), len(clusters[1]) if len(clusters) > 1 else 0))
    return clusters[0][:25]


only = [a for a in sys.argv[1:] if not a.startswith("--")]
AUTO = "--auto" in sys.argv
MINSIM = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--min=")), 0.36))   # 본인 판정 최소 유사도
REF = {}
for f in sorted(glob.glob(os.path.join(OUT, "*.mp4"))):
    name = os.path.splitext(os.path.basename(f))[0]
    if only and name not in only:
        continue
    person = name.split()[0]
    if person not in REF:
        REF[person] = (dominant(person) if AUTO else []) or refs_of(person) or dominant(person)
    R = REF[person]
    cap = cv2.VideoCapture(f)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    best, fallback = (0, None, 0, 0), (0, None, 0, 0)
    for i in range(int(fps), n - int(fps), int(fps * 0.4)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if not ok:
            continue
        band = fr[BAND_Y:BAND_Y + BAND_H]
        for fc in faces(band):
            x, y, w, h = fc[:4]
            if w < 90 or fc[-1] < 0.85:
                continue
            g = cv2.cvtColor(band[int(max(0, y)):int(y + h), int(max(0, x)):int(x + w)], cv2.COLOR_BGR2GRAY)
            if g.size == 0 or cv2.Laplacian(g, cv2.CV_64F).var() < 50:
                continue
            sim = max([rec.match(emb(band, fc), r, cv2.FaceRecognizerSF_FR_COSINE) for r in R] or [0])
            area = w * h * (0.85 if (y < 5 or y + h > BAND_H - 5) else 1.0)
            if sim >= MINSIM and area > best[0]:
                best = (area, fr.copy(), i / fps, sim)
            if area > fallback[0]:
                fallback = (area, fr.copy(), i / fps, sim)
    cap.release()
    use, tag = (best, "본인 확인") if best[1] is not None else (fallback, "본인 미확인-가장 큰 얼굴")
    if use[1] is None:
        print(name, "얼굴 없음"); continue
    cv2.imencode(".jpg", use[1], [cv2.IMWRITE_JPEG_QUALITY, 93])[1].tofile(os.path.join(OUT, name + ".jpg"))
    print("%s.jpg  %.1f초, 유사도 %.2f, %s" % (name, use[2], use[3], tag), flush=True)
