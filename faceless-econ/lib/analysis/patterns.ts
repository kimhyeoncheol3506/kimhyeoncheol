// 상위 채널 콘텐츠 패턴 추출
// - '관측': API 데이터·제목 텍스트에서 직접 계산한 값
// - '가설': 관측값을 해석한 설명 (상관관계일 뿐 인과가 아님, 대안 가설을 함께 제시)
// - '검증되지 않음': 영상 화면·대본을 확인해야 답할 수 있으나 사용자 확인 입력이 없는 항목

import type { VideoScore } from "../scoring/viral";
import type { VideoAnnotation, VideoRecord } from "../types";
import { analyzeTitle } from "./title";

export type Confidence3 = "낮음" | "중간" | "높음";

export interface Evidence {
  videoId: string;
  title: string;
  url: string;
  value: string;
}

export interface Finding {
  question: string;
  kind: "관측" | "가설" | "검증되지 않음";
  answer: string;
  details?: string[];
  alternatives?: string[];
  n: number;
  confidence: Confidence3;
  evidence: Evidence[];
}

export function confidenceFor(n: number, kind: Finding["kind"]): Confidence3 {
  if (kind === "검증되지 않음") return "낮음";
  const base: Confidence3 = n >= 30 ? "높음" : n >= 10 ? "중간" : "낮음";
  if (kind === "가설" && base === "높음") return "중간";
  return base;
}

const INDICATORS = /(금리|기준금리|환율|물가|CPI|GDP|국채|채권|유가|실업|고용|무역|경상수지|통화|인플레|연준|Fed|코스피|지수)/i;
const DAILY = /(지갑|대출|월급|집값|전세|월세|이자|장바구니|생활비|내 돈|우리|가계|노후|연금|적금|예금|카드|청약)/;

interface Row {
  v: VideoRecord;
  s: VideoScore;
}

function ev(r: Row, value: string): Evidence {
  return { videoId: r.v.id, title: r.v.title, url: r.v.url, value };
}

function medianOf(a: number[]): number | null {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

function share(rows: Row[], pred: (r: Row) => boolean): number {
  return rows.length ? rows.filter(pred).length / rows.length : 0;
}

const p = (x: number) => `${(x * 100).toFixed(0)}%`;

export function splitTopBottom(rows: Row[]): { top: Row[]; bottom: Row[] } {
  const scored = rows.filter((r) => r.s.viralScore != null).sort((a, b) => b.s.viralScore! - a.s.viralScore!);
  const half = Math.floor(scored.length / 2);
  return { top: scored.slice(0, half), bottom: scored.slice(scored.length - half) };
}

export function extractPatterns(
  videos: VideoRecord[],
  scores: Map<string, VideoScore>,
  annotations: Record<string, VideoAnnotation>,
): Finding[] {
  const rows: Row[] = videos.map((v) => ({ v, s: scores.get(v.id)! })).filter((r) => r.s);
  const longRows = rows.filter((r) => r.v.format === "long");
  const { top, bottom } = splitTopBottom(longRows);
  const nScored = top.length + bottom.length;
  const out: Finding[] = [];

  // 1. 성과 좋은 주제 (키워드 상승도)
  {
    const count = (rs: Row[]) => {
      const m = new Map<string, number>();
      for (const r of rs) for (const k of new Set(r.v.keywords)) m.set(k, (m.get(k) ?? 0) + 1);
      return m;
    };
    const ct = count(top);
    const cb = count(bottom);
    const lifts = [...ct.entries()]
      .filter(([, c]) => c >= 2)
      .map(([k, c]) => ({ k, c, lift: (c / Math.max(1, top.length)) / ((cb.get(k) ?? 0) / Math.max(1, bottom.length) + 0.05) }))
      .sort((a, b) => b.lift - a.lift)
      .slice(0, 5);
    out.push({
      question: "최근 성과가 좋은 주제는 무엇인가?",
      kind: "관측",
      answer: lifts.length
        ? `상위 절반 영상에 더 자주 등장한 제목 키워드: ${lifts.map((l) => `'${l.k}'(${l.c}회)`).join(", ")}`
        : "상위·하위 영상을 구분할 만큼 반복되는 키워드가 없습니다.",
      details: ["롱폼 영상을 바이럴 점수 기준 상위 절반·하위 절반으로 나눠 제목 키워드 출현 빈도를 비교했습니다."],
      alternatives: ["해당 주제 자체보다 게시 시점의 뉴스 이슈(시의성)가 성과에 영향을 줬을 수 있습니다.", "표본이 작으면 우연한 쏠림일 수 있습니다."],
      n: nScored,
      confidence: confidenceFor(nScored, "관측"),
      evidence: top.filter((r) => lifts.some((l) => r.v.keywords.includes(l.k))).slice(0, 5).map((r) => ev(r, `바이럴 ${r.s.viralScore!.toFixed(1)}`)),
    });
  }

  // 2. 제목 구조
  {
    const ta = (r: Row) => analyzeTitle(r.v.title.replace("[데모] ", ""));
    const types = ["질문형", "경고형", "비교형", "반전형", "숫자형"] as const;
    const details = types.map((t) => `${t}: 상위 ${p(share(top, (r) => ta(r).types.includes(t)))} / 하위 ${p(share(bottom, (r) => ta(r).types.includes(t)))}`);
    const lenTop = medianOf(top.map((r) => ta(r).length));
    const lenBot = medianOf(bottom.map((r) => ta(r).length));
    details.push(`제목 길이 중앙값: 상위 ${lenTop ?? "-"}자 / 하위 ${lenBot ?? "-"}자`);
    const best = types
      .map((t) => ({ t, d: share(top, (r) => ta(r).types.includes(t)) - share(bottom, (r) => ta(r).types.includes(t)) }))
      .sort((a, b) => b.d - a.d)[0];
    out.push({
      question: "어떤 제목 구조가 반복되는가?",
      kind: "관측",
      answer: best && best.d > 0.1 ? `상위 영상에서 '${best.t}' 제목이 하위 영상보다 ${p(best.d)}p 더 많이 쓰였습니다.` : "상위·하위 영상 사이에 뚜렷한 제목 유형 차이가 관측되지 않았습니다.",
      details,
      alternatives: ["제목 유형보다 썸네일·주제·노출 시점의 영향이 클 수 있습니다 (제목 단독 효과는 분리되지 않음)."],
      n: nScored,
      confidence: confidenceFor(nScored, "관측"),
      evidence: top.slice(0, 3).map((r) => ev(r, ta(r).types.join("·"))),
    });
  }

  // 3. 경제지표 ↔ 일상
  {
    const both = (r: Row) => INDICATORS.test(r.v.title) && DAILY.test(r.v.title);
    out.push({
      question: "경제지표와 일상생활을 어떻게 연결하는가?",
      kind: "가설",
      answer: `제목에 경제지표 단어와 생활 단어가 함께 들어간 비율: 상위 ${p(share(top, both))} / 하위 ${p(share(bottom, both))}. 지표를 '내 대출·월급·집값' 같은 개인 결과로 번역하는 제목이 관측됩니다.`,
      details: ["제목 텍스트만 본 결과입니다. 영상 본문에서 실제로 어떻게 연결하는지는 영상 확인 후 '영상 정밀 분석'에 입력해야 합니다."],
      alternatives: ["생활 단어가 들어간 제목이 더 넓은 시청층에 노출된 결과일 수 있습니다.", "같은 채널 내 주제 선택 차이가 원인일 수 있습니다."],
      n: nScored,
      confidence: confidenceFor(nScored, "가설"),
      evidence: top.filter(both).slice(0, 3).map((r) => ev(r, "지표+생활 단어")),
    });
  }

  // 4·5. 영상 내부 구조 — 사용자 확인 입력 필요
  const ann = rows.map((r) => annotations[r.v.id]).filter((a): a is VideoAnnotation => !!a);
  const structVerified = ann.filter((a) => a.structure.verified);
  out.push({
    question: "제목에서 약속한 답을 영상이 어떤 순서로 제공하는가?",
    kind: structVerified.length ? "관측" : "검증되지 않음",
    answer: structVerified.length
      ? `직접 확인한 ${structVerified.length}개 영상: 첫 핵심 정보 등장 시점 중앙값 ${medianOf(structVerified.map((a) => a.structure.firstInfoSec).filter((x): x is number => x != null)) ?? "-"}초`
      : "실제 영상·대본을 확인한 입력이 없어 판단하지 않습니다. 영상 정밀 분석 화면에서 도입부·흐름을 직접 확인해 입력하세요.",
    details: structVerified.slice(0, 5).map((a) => `${a.videoId}: ${a.structure.flow || "흐름 미입력"}`),
    n: structVerified.length,
    confidence: confidenceFor(structVerified.length, structVerified.length ? "관측" : "검증되지 않음"),
    evidence: [],
  });
  const visVerified = ann.filter((a) => a.visual.verified);
  out.push({
    question: "자료 화면과 내레이션을 어떻게 조합하는가?",
    kind: visVerified.length ? "관측" : "검증되지 않음",
    answer: visVerified.length
      ? `직접 확인한 ${visVerified.length}개 영상의 시각 방식: ${[...new Set(visVerified.map((a) => a.visual.style).filter(Boolean))].join(", ") || "미입력"}`
      : "영상 프레임·자막을 확인한 입력이 없습니다. 채널 분류(A/B/C)는 간접 근거에 의한 추정일 뿐입니다.",
    n: visVerified.length,
    confidence: confidenceFor(visVerified.length, visVerified.length ? "관측" : "검증되지 않음"),
    evidence: [],
  });

  // 6. 길이
  {
    const buckets = [
      { label: "6분 미만", lo: 0, hi: 360 },
      { label: "6~10분", lo: 360, hi: 600 },
      { label: "10~15분", lo: 600, hi: 900 },
      { label: "15~20분", lo: 900, hi: 1200 },
      { label: "20분 이상", lo: 1200, hi: Infinity },
    ];
    const stats = buckets.map((b) => {
      const rs = longRows.filter((r) => r.v.durationSec != null && r.v.durationSec >= b.lo && r.v.durationSec < b.hi && r.s.viralScore != null);
      return { label: b.label, n: rs.length, med: medianOf(rs.map((r) => r.s.viralScore!)) };
    });
    const best = stats.filter((s) => s.n >= 3).sort((a, b) => (b.med ?? 0) - (a.med ?? 0))[0];
    out.push({
      question: "영상 길이는 어느 범위에서 성과가 좋은가?",
      kind: "관측",
      answer: best ? `영상이 3개 이상인 구간 중 '${best.label}'의 바이럴 점수 중앙값이 가장 높습니다 (${best.med!.toFixed(1)}, n=${best.n}).` : "구간별 표본이 3개 미만이라 판정 보류합니다.",
      details: stats.map((s) => `${s.label}: n=${s.n}, 중앙값 ${s.med?.toFixed(1) ?? "-"}`),
      alternatives: ["길이는 주제 복잡도와 함께 움직이므로 길이 자체의 효과로 볼 수 없습니다.", "백분위 점수는 그룹 안 상대 순위라 채널 간 규모 차이가 섞여 있습니다."],
      n: stats.reduce((a, s) => a + s.n, 0),
      confidence: confidenceFor(stats.reduce((a, s) => a + s.n, 0), "관측"),
      evidence: [],
    });
  }

  // 7. 롱폼 vs 쇼츠
  {
    const shorts = rows.filter((r) => r.v.format === "shorts");
    const vph = (rs: Row[]) => medianOf(rs.map((r) => r.s.metrics.velocity.raw).filter((x): x is number => x != null));
    const sub = (rs: Row[]) => medianOf(rs.map((r) => r.s.metrics.subRatio.raw).filter((x): x is number => x != null));
    out.push({
      question: "롱폼과 쇼츠의 역할이 어떻게 다른가?",
      kind: "관측",
      answer: `롱폼 ${longRows.length}개, 쇼츠 ${shorts.length}개. 시간당 조회수 중앙값 롱폼 ${vph(longRows)?.toFixed(0) ?? "-"} / 쇼츠 ${vph(shorts)?.toFixed(0) ?? "-"}, 구독자 대비 조회수 중앙값 롱폼 ${sub(longRows)?.toFixed(3) ?? "-"} / 쇼츠 ${sub(shorts)?.toFixed(3) ?? "-"}.`,
      details: ["쇼츠 조회수 집계 방식은 롱폼과 달라 두 형식의 수치를 직접 비교하지 않고 형식별로 따로 순위를 냅니다.", "역할 해석(쇼츠=유입, 롱폼=신뢰·체류)은 가설이며 구독 전환 데이터는 공개 API로 수집할 수 없습니다."],
      n: rows.length,
      confidence: confidenceFor(rows.length, "관측"),
      evidence: [],
    });
  }

  // 8·9. 재현 가능 요소 / 모방 금지 요소
  out.push({
    question: "초보 제작자가 적은 비용으로 재현할 수 있는 요소는 무엇인가?",
    kind: "가설",
    answer: "공식 통계 차트 + 내레이션 + 핵심 수치 자막 조합(A·C형). 제목에서 숫자·질문으로 약속하고 도입 30초 안에 답의 방향을 먼저 보여주는 구조.",
    details: ["차트는 한국은행 ECOS·KOSIS 등 공개 데이터로 직접 제작 가능", "애니메이션(B형)은 템플릿 기반 모션그래픽으로 축소 재현 가능하지만 제작 시간이 큼"],
    alternatives: ["상위 채널의 성과는 누적 구독자·브랜드 신뢰 효과일 수 있어 신규 채널에서 같은 결과가 나온다는 보장이 없습니다."],
    n: nScored,
    confidence: "낮음",
    evidence: [],
  });
  out.push({
    question: "단순 모방하면 안 되는 요소는 무엇인가?",
    kind: "가설",
    answer: "타 채널의 대본 문장·고유 캐릭터·썸네일 디자인·고유한 말투와 시리즈명은 복제하지 않습니다. 근거 없는 폭락·급등 단정 제목도 따라 하지 않습니다.",
    details: ["저작권·상표 위험", "금융 정보 오인 위험 (투자 권유로 해석될 수 있는 표현)", "구조(문제→근거→의미→행동)만 원리로 차용"],
    n: 0,
    confidence: "중간",
    evidence: [],
  });
  return out;
}

export interface ChannelProfile {
  channelId: string;
  n: number;
  longCount: number;
  shortsCount: number;
  uploadsPerWeek: number;
  medianDurationMin: number | null;
  medianTitleLen: number | null;
  numberTitleShare: number;
  questionShare: number;
  topKeywords: string[];
  topVsBottom: { metric: string; top: string; bottom: string }[];
}

export function channelProfile(channelId: string, videos: VideoRecord[], scores: Map<string, VideoScore>, periodDays: number): ChannelProfile {
  const rows: Row[] = videos.filter((v) => v.channelId === channelId).map((v) => ({ v, s: scores.get(v.id)! })).filter((r) => r.s);
  const long = rows.filter((r) => r.v.format === "long");
  const kw = new Map<string, number>();
  for (const r of rows) for (const k of r.v.keywords) kw.set(k, (kw.get(k) ?? 0) + 1);
  const ranked = long.filter((r) => r.s.viralScore != null).sort((a, b) => b.s.viralScore! - a.s.viralScore!);
  const top = ranked.slice(0, 3);
  const bot = ranked.length >= 6 ? ranked.slice(-3) : [];
  const fmt = (rs: Row[], f: (r: Row) => number | null, d = 1) => {
    const m = medianOf(rs.map(f).filter((x): x is number => x != null && Number.isFinite(x)));
    return m == null ? "-" : m.toFixed(d);
  };
  return {
    channelId,
    n: rows.length,
    longCount: long.length,
    shortsCount: rows.filter((r) => r.v.format === "shorts").length,
    uploadsPerWeek: (rows.length / periodDays) * 7,
    medianDurationMin: medianOf(long.map((r) => (r.v.durationSec ?? 0) / 60).filter((x) => x > 0)),
    medianTitleLen: medianOf(rows.map((r) => analyzeTitle(r.v.title).length)),
    numberTitleShare: share(rows, (r) => analyzeTitle(r.v.title).hasNumber),
    questionShare: share(rows, (r) => analyzeTitle(r.v.title).types.includes("질문형")),
    topKeywords: [...kw.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([k]) => k),
    topVsBottom: bot.length
      ? [
          { metric: "바이럴 점수 중앙값", top: fmt(top, (r) => r.s.viralScore), bottom: fmt(bot, (r) => r.s.viralScore) },
          { metric: "영상 길이(분)", top: fmt(top, (r) => (r.v.durationSec ?? 0) / 60), bottom: fmt(bot, (r) => (r.v.durationSec ?? 0) / 60) },
          { metric: "제목 길이(자)", top: fmt(top, (r) => analyzeTitle(r.v.title).length, 0), bottom: fmt(bot, (r) => analyzeTitle(r.v.title).length, 0) },
          { metric: "제목 숫자 사용", top: p(share(top, (r) => analyzeTitle(r.v.title).hasNumber)), bottom: p(share(bot, (r) => analyzeTitle(r.v.title).hasNumber)) },
          { metric: "좋아요율(%)", top: fmt(top, (r) => (r.s.metrics.likeRate.raw ?? NaN) * 100, 2), bottom: fmt(bot, (r) => (r.s.metrics.likeRate.raw ?? NaN) * 100, 2) },
        ]
      : [],
  };
}
