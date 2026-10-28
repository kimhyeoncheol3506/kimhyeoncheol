import Link from "next/link";
import "./landing.css";
import { CoverLinks, DevMark, EightChars, HowSlider, InlinePic, SheetIndex, Stage, StartDialog } from "@/components/landing/parts";

const STRIPE = Array.from({ length: 40 });

const FAQ: [string, React.ReactNode][] = [
  ["정말 무료인가요?", "네. 사주와 관상 풀이, 목소리로 읽어 주는 것까지 돈을 받지 않습니다."],
  ["사진은 어디로 가나요?", "어디로도 가지 않습니다. 얼굴 분석은 휴대폰 브라우저 안에서 끝나고, 결과가 나오면 사진은 메모리에서 바로 지웁니다."],
  ["생년월일은 저장하나요?", "저장하지 않습니다. 결과는 지금 쓰는 브라우저 창 안에만 남습니다."],
  ["태어난 시간을 모르면요?", "시주를 빼고 여섯 글자로 봅니다. 시간에 기대는 해석은 결과에서 덜어 냅니다."],
  ["두 엔진이 다르게 나오면요?", "그 칸은 ‘판단 보류’로 표시하고 해석에 쓰지 않습니다. 절기가 바뀌는 날 즈음에 태어난 분에게 가끔 생깁니다."],
  ["얼굴 사진이 없어도 되나요?", "됩니다. 사주만으로도 결과가 나오고, 사진을 넣으면 관상과 겹치는 이야기가 더해집니다."],
  ["가입해야 하나요?", "결과 화면은 회원만 볼 수 있어요. 이메일로 1분이면 가입합니다."],
  [
    "궁합도 볼 수 있나요?",
    <>
      네. 두 사람의 생년월일로 궁합 점수를 보고, 사진을 넣으면 관상 궁합까지 봅니다.{" "}
      <Link className="link" href="/match">
        궁합 보러 가기
      </Link>
    </>,
  ],
  ["AI가 점을 치나요?", "아닙니다. 계산은 두 사주 엔진과 얼굴 측정이 하고, 해석 문장은 규칙으로 만듭니다. AI(Claude)는 켜져 있을 때 그 문장을 자연스럽게 다듬기만 합니다."],
  ["믿어도 되나요?", "재미와 참고로 봐 주세요. 의학·법률·재정 조언이 아니며, 중요한 결정은 전문가와 상담하세요."],
];

const CREDITS = [
  { t: "윤두서 자화상", by: "퍼블릭 도메인", href: "https://commons.wikimedia.org/wiki/File:Yun_Du-seo.jpg" },
  { t: "천상열차분야지도 복각비", by: "사진 Jocelyndurrey, CC BY-SA 4.0, 잘라 씀", href: "https://commons.wikimedia.org/wiki/File:%EC%B2%9C%EC%83%81%EC%97%B4%EC%B0%A8%EB%B6%84%EC%95%BC%EC%A7%80%EB%8F%84_(3).JPG" },
  { t: "면부찰색도(1817)", by: "Wellcome Collection, CC BY 4.0", href: "https://commons.wikimedia.org/wiki/File:Physiognomy_diagnosis_chart,_Chinese_woodcut,_1817_Wellcome_L0034726.jpg" },
  { t: "영조 어진", by: "채용신·조석진, 퍼블릭 도메인", href: "https://commons.wikimedia.org/wiki/File:Portrait_of_King_Yeongjo_-_Chae_Yong_Shin_(%E8%94%A1%E9%BE%8D%E8%87%A3_1850-1941)_Cho_Seok-jin_(%E8%B6%99%E9%8C%AB%E6%99%89_1853-1920)_et_(cropped).jpg" },
];

export default function Landing() {
  return (
    <div className="lp">
      <div className="split">
        <div className="col">
          <InlinePic k="yun" className="pic-hero" />

          {/* 표지 */}
          <section className="cover" data-pic="yun" aria-labelledby="title">
            <div className="stripe" aria-hidden>
              {STRIPE.map((_, i) => (
                <i key={i} />
              ))}
            </div>
            <div className="cover-body">
              <p className="wordmark">
                얼굴과 운명
                <DevMark />
              </p>
              <h1 id="title" className="display">
                사주와 관상,
                <br />
                겹치는 말만
              </h1>
              <p className="sub">생년월일과 얼굴 사진으로 보는 무료 사주·관상. 둘이 함께 가리키는 이야기만 골라 목소리로 들려드려요.</p>
              <Link href="/analyze" className="btn-lp">
                무료로 시작하기
                <span className="bars" aria-hidden>
                  <i />
                  <i />
                  <i />
                </span>
              </Link>
            </div>
            <CoverLinks />
          </section>

          {/* 살아 있는 것 */}
          <section className="block" data-pic="star" aria-labelledby="eight">
            <h2 id="eight" className="head" data-rise>
              내 여덟 글자, 지금 바로
            </h2>
            <p className="intro" data-rise style={{ ["--i" as string]: 1 }}>
              생일을 고르면 두 엔진이 따로 계산한 사주팔자가 나란히 나옵니다. 둘이 같은 글자만 아래 줄에 남아요.
            </p>
            <InlinePic k="star" />
            <div data-rise style={{ ["--i" as string]: 2 }}>
              <EightChars />
            </div>
          </section>

          {/* 어떻게 보나요 */}
          <section className="block" id="how" data-pic="chart" aria-labelledby="how-h">
            <h2 id="how-h" className="head" data-rise>
              어떻게 보나요
            </h2>
            <InlinePic k="chart" />
            <div data-rise style={{ ["--i" as string]: 1 }}>
              <HowSlider />
            </div>
          </section>

          {/* 자주 묻는 질문 */}
          <section className="block" id="faq" data-pic="yeongjo" aria-labelledby="faq-h">
            <h2 id="faq-h" className="head" data-rise>
              자주 묻는 질문
            </h2>
            <InlinePic k="yeongjo" />
            <div className="faq">
              {FAQ.map(([q, a], n) => (
                <p key={q} data-rise style={{ ["--i" as string]: Math.min(n, 4) }}>
                  <b>{q}</b> {a}
                </p>
              ))}
            </div>
          </section>
        </div>

        <Stage />
      </div>

      {/* 결과지 (전체 폭) */}
      <section className="sheetwrap" aria-label="결과지에 담기는 것">
        <SheetIndex />
      </section>

      {/* 마지막 */}
      <section className="cta" aria-labelledby="end">
        <div className="lp-left">
          <h2 id="end" data-rise>
            3분이면
            <br />
            끝나요
          </h2>
          <p className="after-line" data-rise style={{ ["--i" as string]: 1 }}>
            생일, 태어난 시간, 성별, 얼굴 사진 한 장. 네 가지를 차례로 묻고 바로 결과를 보여 드려요.
          </p>
        </div>
        <StartDialog />
      </section>

      <footer className="quiet">
        <span className="soft">얼굴과 운명 · 무료 사주와 관상</span>
        <nav aria-label="약관">
          <Link className="link" href="/disclaimer">면책조항</Link>
          <Link className="link" href="/privacy">개인정보처리방침</Link>
          <Link className="link" href="/open-source">오픈소스 고지</Link>
        </nav>
        <span className="soft year">© {new Date().getFullYear()} 얼굴과 운명</span>
        <p className="credits">
          그림:{" "}
          {CREDITS.map((c, i) => (
            <span key={c.t}>
              <a className="link" href={c.href} target="_blank" rel="noreferrer">
                {c.t}
              </a>{" "}
              ({c.by}){i < CREDITS.length - 1 ? " · " : ""}
            </span>
          ))}
          . 모두 Wikimedia Commons에서 가져왔습니다.
        </p>
      </footer>
    </div>
  );
}
