// 제목 자동 분석 (규칙 기반). 결과는 '제목 텍스트에서 관측된 사실'이며,
// 제목과 실제 내용의 일치 여부는 영상을 확인해야 하므로 여기서 판정하지 않는다.

export type TitleType = "질문형" | "경고형" | "비교형" | "반전형" | "숫자형" | "설명형";
export type TitleFrame = "손실 회피" | "호기심" | "긴급성" | "미래 예측" | "이득 약속" | "권위·근거";

export interface TitleAnalysis {
  length: number; // 공백 포함 글자 수
  lengthNoSpace: number;
  hasNumber: boolean;
  numbers: string[];
  frontKeywords: string[]; // 앞 12자 안에 등장한 핵심 키워드
  types: TitleType[];
  frames: TitleFrame[];
  hasBracket: boolean; // [ ] 【 】 등 말머리
  hasEmojiOrSymbol: boolean;
}

const STOP = new Set([
  "그리고", "하지만", "그래서", "이유", "진짜", "지금", "정말", "결국", "이제", "모든", "가장", "있는", "없는",
  "하는", "되는", "이런", "그런", "합니다", "입니다", "나요", "까요", "the", "and", "for",
  "알고", "보니", "있었다", "생기는", "생긴", "모르면", "이거", "뭐길래", "보는", "위한", "쉽게", "정리", "요약",
  "shorts", "short", "데모",
]);

const PATTERNS: { type: TitleType; re: RegExp }[] = [
  { type: "질문형", re: /\?|？|(일까|을까|ㄹ까|나요|는가|인가|할까|될까|왜\s|어떻게|무엇|뭘까|누가)/ },
  { type: "경고형", re: /(경고|주의|조심|절대|위험|큰일|폭탄|함정|망하|피하세요|하지\s?마|사라진|붕괴|폭락|위기)/ },
  { type: "비교형", re: /(vs|VS|대\s|보다|차이|비교|어디가|뭐가 더|승자|이기는)/ },
  { type: "반전형", re: /(사실은|알고 보니|반전|오히려|착각|오해|아니었|의외|진실|숨겨진|몰랐던)/ },
];

const FRAMES: { frame: TitleFrame; re: RegExp }[] = [
  { frame: "손실 회피", re: /(손해|손실|잃|날리|폭락|하락|망하|위험|빚|이자 폭탄|함정|피하|놓치)/ },
  { frame: "호기심", re: /(이유|비밀|진실|몰랐던|숨겨진|왜|정체|비결|알고 보니|사실은)/ },
  { frame: "긴급성", re: /(지금|당장|곧|마지막|서둘러|이번 주|오늘|내일|임박|긴급|속보)/ },
  { frame: "미래 예측", re: /(전망|예측|앞으로|내년|\d{4}년|미래|올까|될까|시나리오|온다)/ },
  { frame: "이득 약속", re: /(버는|벌어|수익|아끼|절약|혜택|무료|돈 되는|부자|오르는)/ },
  { frame: "권위·근거", re: /(한국은행|통계|데이터|보고서|연구|발표|공식|정부|금융위|금감원|IMF|연준|Fed)/i },
];

export function extractKeywords(title: string, limit = 6): string[] {
  const cleaned = title
    .replace(/#\S+/g, " ")
    .replace(/[\[\]【】()（）「」『』<>|#"'“”‘’!?？！.,:;~…·\-–—]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const words = cleaned
    .split(" ")
    .map((w) => w.replace(/(은|는|이|가|을|를|의|에|에서|으로|로|와|과|도|만|까지|부터)$/u, ""))
    .filter((w) => w.length >= 2 && !STOP.has(w) && !/^\d+$/.test(w));
  const seen = new Set<string>();
  const out: string[] = [];
  for (const w of words) {
    if (seen.has(w)) continue;
    seen.add(w);
    out.push(w);
    if (out.length >= limit) break;
  }
  return out;
}

export function analyzeTitle(title: string): TitleAnalysis {
  const numbers = title.match(/\d+(?:[.,]\d+)*\s?(?:%|퍼센트|억|만|조|원|배|년|개|가지|위|분|일)?/g) ?? [];
  const types: TitleType[] = [];
  for (const p of PATTERNS) if (p.re.test(title)) types.push(p.type);
  if (numbers.length > 0) types.push("숫자형");
  if (types.length === 0) types.push("설명형");
  const frames: TitleFrame[] = [];
  for (const f of FRAMES) if (f.re.test(title)) frames.push(f.frame);
  const front = title.slice(0, 12);
  const kws = extractKeywords(title, 10);
  return {
    length: [...title].length,
    lengthNoSpace: [...title.replace(/\s/g, "")].length,
    hasNumber: numbers.length > 0,
    numbers: numbers.map((n) => n.trim()),
    frontKeywords: kws.filter((k) => front.includes(k)).slice(0, 3),
    types,
    frames,
    hasBracket: /[\[【「『]/.test(title),
    hasEmojiOrSymbol: /[\u{1F300}-\u{1FAFF}☀-➿]/u.test(title),
  };
}
