"""여의도남자·여의도여자 발음 점검(타입캐스트 권장 '자주 쓰는 용어 20개 먼저 들어 보기'를 자동으로).

PC 에서 Voicebox 를 켠 뒤:
  python tools/pron_audit.py                 # 두 목소리 모두, 점검 문장 전부
  python tools/pron_audit.py --voice 여의도여자 --limit 10
결과: output/pron_audit/<날짜>/report.md + 문장별 wav. 틀린 낱말은 학습 기록(rules/pron_watch.jsonl)에 쌓이고
2번 이상 틀린 낱말은 바로 발음 사전(rules/pron_learned.json)에 들어간다.
"""
import argparse
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# 경제 채널에서 자주 나오고 TTS 가 잘 틀리는 말을 한 문장에 두세 개씩 묶었다(발음사전 각 갈래 + 숫자·약어)
SENTENCES = [
    "한국은행이 기준금리를 연 3.00%로 동결했습니다.",
    "올해 영업이익과 당기순이익이 모두 사상 최대를 기록했습니다.",
    "금융위원회는 가계부채 관리를 더 강화하겠다고 밝혔습니다.",
    "코스피가 하루 만에 7.57% 폭락했고, 코스닥도 급락했습니다.",
    "실업률과 고용률, 출산율이 동시에 나빠지고 있습니다.",
    "삼성전자와 SK하이닉스가 코스피 영업이익의 71.9%를 차지합니다.",
    "GDP 대비 가계부채 비율은 81.1%로 10년 만에 가장 낮습니다.",
    "외국인 투자자의 순매도가 2008년 금융위기 수준에 근접했습니다.",
    "서울 아파트 분양가는 3.3㎡당 6천만 원을 넘었습니다.",
    "생산량이 줄면서 판단력이 흐려지는 공권력 논란도 이어졌습니다.",
    "관리비와 인건비가 오르면서 원래 계획보다 연락이 늦어졌습니다.",
    "국민연금의 수익률은 시장 평가와 달리 꽤 높았습니다.",
    "HBM 가격 협상과 LTA 계약이 3Q 실적을 좌우합니다.",
    "Fed가 25bp 금리를 올리면 원/달러 환율이 흔들립니다.",
    "시가총액 상위 종목의 종가와 호가가 크게 벌어졌습니다.",
    "합리적인 협력이 독립적인 심리를 이길 수 있을까요?",
    "S&P500과 나스닥은 YoY 12% 상승했습니다.",
    "결정은 갈등을 줄이는 쪽으로 할게요.",
    "유가 급등으로 물가와 주가가 동시에 흔들립니다.",
    "문의는 010-1234-5678로 해 주세요.",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", choices=["여의도여자", "여의도남자", "both"], default="both")
    ap.add_argument("--limit", type=int, default=len(SENTENCES))
    a = ap.parse_args()
    import soundfile as sf
    from facetube.voice import Voice, SR
    from facetube import pron_learn
    from facetube.textnorm import to_speech

    voices = ["여의도여자", "여의도남자"] if a.voice == "both" else [a.voice]
    out = ROOT / "output" / "pron_audit" / datetime.date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    lines = ["# 발음 점검", "", "| 목소리 | # | 대본 | 들린 말 | CER | 시도 | 틀린 낱말 |", "|---|---|---|---|---|---|---|"]
    fails = 0
    for v in voices:
        voice = Voice(backend="voicebox", voice=v)
        for i, s in enumerate(SENTENCES[:a.limit], 1):
            x, info = voice.say(s)
            sf.write(out / f"{v}_{i:02d}.wav", x, SR)
            bad = [w["word"] for w in pron_learn.misread_words(to_speech(s), info["asr"])]
            fails += bool(info["cer"] and info["cer"] > voice.cer_retry)
            lines.append(f"| {v} | {i} | {s} | {info['asr']} | {info['cer']} | {info['tries']} | {', '.join(bad) or '-'} |")
            print(lines[-1])
    added, manual = pron_learn.update()
    lines += ["", f"기준(CER {voice.cer_retry}) 넘은 문장: {fails}개",
              f"사전에 새로 넣은 낱말: {', '.join(added) or '없음'}",
              f"직접 고쳐야 할 낱말: {', '.join(manual) or '없음'}"]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n보고서: {out / 'report.md'}")


if __name__ == "__main__":
    main()
