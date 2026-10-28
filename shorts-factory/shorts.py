#!/usr/bin/env python3
"""쇼핑 쇼츠 자동 제작기

  python shorts.py                       # 질문에 답하면서 만들기 (처음이면 이걸로)
  python shorts.py run --product "무선 미니 고데기" --target "20대 여성" --benefits 가격,편리함,디자인 \
                       --price 19900 --orig-price 39000 --brand "글로우랩"
  python shorts.py feedback "조회수가 안 나왔어, 후킹이 약해"   # 후킹 강화 후 전체 재생성
  python shorts.py clean 녹취.txt         # 말더듬/반복/멈춤 제거한 교정 대본
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.pipeline import OUTPUT, run_pipeline  # noqa: E402
from engine.rules import load_rules, save_hooks_section, strengthen_hooks  # noqa: E402
from engine.script import clean_text  # noqa: E402


def parse_raw_script(path):
    """녹취 파일: 'intro: 멘트' 처럼 구간명: 으로 시작하는 줄. 구간명 없으면 무시."""
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip() in ("hook", "intro", "feature", "price", "cta"):
                out[k.strip()] = (out.get(k.strip(), "") + " " + v).strip()
    return out


def cmd_run(a):
    inp = {
        "product": a.product, "target": a.target,
        "benefits": [b.strip() for b in a.benefits.split(",") if b.strip()],
        "price": a.price, "orig_price": a.orig_price, "brand": a.brand, "short": a.short,
        "media": a.media, "voice": a.voice, "hook": a.hook, "render": not a.no_render,
        "raw_script": parse_raw_script(a.raw_script) if a.raw_script else None,
    }
    run_pipeline(inp)


def cmd_feedback(a):
    rules = load_rules()
    last_path = OUTPUT / "last_run.json"
    if not last_path.exists():
        sys.exit("아직 만든 영상이 없습니다. 먼저 run 을 실행하세요.")
    last = json.loads(last_path.read_text(encoding="utf-8"))
    text = a.text
    if not any(k in text for k in rules["feedback"]["hook_weak_keywords"]):
        print("후킹 관련 피드백이 아니라서 rules.yaml 은 그대로 두고 다시 생성합니다.")
    else:
        changes = strengthen_hooks(rules, text, last["hook"].get("type"))
        save_hooks_section(rules["hooks"])
        print("rules.yaml 후킹 섹션을 강화했습니다:")
        for c in changes:
            print("  -", c)
    inp = last["input"]
    inp["hook"] = "auto"
    run_pipeline(inp)


def cmd_clean(a):
    rules = load_rules()
    cleaned, log = clean_text(Path(a.file).read_text(encoding="utf-8"), rules)
    print(cleaned)
    for l in log:
        print("  -", l, file=sys.stderr)


def interactive():
    print("=== 쇼핑 쇼츠 자동 제작기 === (그냥 Enter = 예시값)")
    ask = lambda q, d: input(f"{q} [{d}]: ").strip() or d
    product = ask("제품명", "무선 미니 고데기")
    target = ask("타겟", "20대 여성")
    benefits = ask("핵심 혜택 3개(쉼표)", "가격,편리함,디자인")
    price = ask("판매가(숫자, 없으면 0)", "19900")
    orig = ask("정가(숫자, 없으면 0)", "39000")
    brand = ask("브랜드명", product)
    media = ask("촬영 사진/영상 폴더(없으면 Enter)", "")

    def choose(hooks):
        print("\n후킹 후보 (점수순):")
        for h in hooks:
            print(f"  {h['rank']:>2}. [{h['score']}] {h['type_ko']:<7} {h['text']}")
        s = input("사용할 번호 (Enter = 자동 최고점): ").strip()
        return s if s.isdigit() and 1 <= int(s) <= len(hooks) else "1"

    run_pipeline({"product": product, "target": target,
                  "benefits": [b.strip() for b in benefits.split(",")],
                  "price": int(price) or None, "orig_price": int(orig) or None, "brand": brand,
                  "short": None, "media": media or None, "voice": None, "hook": "auto", "render": True,
                  "raw_script": None}, choose=choose)


def main():
    if len(sys.argv) == 1:
        return interactive()
    p = argparse.ArgumentParser(description="쇼핑 쇼츠 자동 제작기")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="영상 만들기")
    r.add_argument("--product", required=True, help="제품명")
    r.add_argument("--target", required=True, help="타겟 (예: 20대 여성)")
    r.add_argument("--benefits", required=True, help="핵심 혜택 3개, 쉼표로 (예: 가격,편리함,디자인)")
    r.add_argument("--price", type=int, help="판매가 (숫자)")
    r.add_argument("--orig-price", type=int, help="정가 (숫자)")
    r.add_argument("--brand", help="브랜드명 (아웃트로 로고 대신 표시)")
    r.add_argument("--short", help="제품 짧은 이름 (후킹에 사용, 기본: 제품명 마지막 단어)")
    r.add_argument("--media", help="촬영 사진/영상 폴더 (hook_/intro_/feature_/price_/cta_ 로 시작하면 해당 구간에 배치)")
    r.add_argument("--voice", help="내레이션 음성 파일 (있으면 실제 공백 0.2초 기준으로 컷)")
    r.add_argument("--hook", default="auto", help="auto(최고점) 또는 순위 번호")
    r.add_argument("--raw-script", help="녹취 원고 파일 ('intro: 멘트' 형식) → 교정해서 사용")
    r.add_argument("--no-render", action="store_true", help="mp4 렌더링 없이 명세/커맨드만")
    r.set_defaults(func=cmd_run)
    f = sub.add_parser("feedback", help="피드백 반영 후 다시 만들기")
    f.add_argument("text")
    f.set_defaults(func=cmd_feedback)
    c = sub.add_parser("clean", help="녹취 교정")
    c.add_argument("file")
    c.set_defaults(func=cmd_clean)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
