// 신규 채널 기획: 콘텐츠 영역 평가와 첫 영상 후보 10개
// 점수는 1~5. '검색 수요'는 키워드 도구 없이 매긴 추정치이므로 네이버 데이터랩·Google 트렌드로 확인해야 한다.
// 역방향 지표(경쟁도·제작 난이도·저작권 위험·정확성 위험)는 점수가 높을수록 '유리(위험·부담이 낮음)'로 환산했다.

export interface AreaEval {
  area: string;
  scores: {
    demand: number; // 검색 수요 (추정)
    timeliness: number; // 시의성
    competitionEase: number; // 경쟁도 (5 = 경쟁 낮음)
    productionEase: number; // 제작 난이도 (5 = 쉬움)
    dataAccess: number; // 데이터 접근성
    copyrightSafety: number; // 저작권 위험 (5 = 안전)
    accuracySafety: number; // 금융정보 정확성 위험 (5 = 오류 위험 낮음)
  };
  officialSources: string[];
  note: string;
}

export const CRITERIA_LABELS: Record<keyof AreaEval["scores"], string> = {
  demand: "검색 수요(추정)",
  timeliness: "시의성",
  competitionEase: "경쟁 여유",
  productionEase: "제작 용이성",
  dataAccess: "데이터 접근성",
  copyrightSafety: "저작권 안전",
  accuracySafety: "정확성 안전",
};

export const AREAS: AreaEval[] = [
  {
    area: "금리와 채권",
    scores: { demand: 4, timeliness: 4, competitionEase: 3, productionEase: 4, dataAccess: 5, copyrightSafety: 5, accuracySafety: 4 },
    officialSources: ["한국은행 기준금리·ECOS", "은행연합회 COFIX 공시", "금융투자협회 채권정보센터"],
    note: "공식 통계가 풍부하고 차트 중심(C형)으로 만들기 쉬움. 개인 대출과 연결하면 수요가 넓어짐.",
  },
  {
    area: "부동산과 주택시장",
    scores: { demand: 5, timeliness: 4, competitionEase: 2, productionEase: 3, dataAccess: 4, copyrightSafety: 4, accuracySafety: 3 },
    officialSources: ["국토교통부 실거래가 공개시스템", "한국부동산원 R-ONE", "KOSIS 주택 통계"],
    note: "수요는 가장 크지만 경쟁 채널이 많고 지역별 일반화 오류 위험이 큼.",
  },
  {
    area: "국내 주식과 미국 주식",
    scores: { demand: 5, timeliness: 5, competitionEase: 1, productionEase: 3, dataAccess: 4, copyrightSafety: 3, accuracySafety: 2 },
    officialSources: ["한국거래소 정보데이터시스템", "DART 전자공시", "미 SEC EDGAR"],
    note: "종목 언급은 투자 권유로 오인될 위험. 실시간 시세 의존도가 높아 첫 영상으로는 부적합.",
  },
  {
    area: "가계 자산과 금융상품",
    scores: { demand: 4, timeliness: 3, competitionEase: 3, productionEase: 4, dataAccess: 4, copyrightSafety: 5, accuracySafety: 4 },
    officialSources: ["금융감독원 금융상품 한눈에", "통계청 가계금융복지조사", "예금보험공사"],
    note: "상품 구조 설명은 시간이 지나도 유효(에버그린). 특정 상품 추천은 피해야 함.",
  },
  {
    area: "기업과 산업의 흥망성쇠",
    scores: { demand: 4, timeliness: 2, competitionEase: 3, productionEase: 2, dataAccess: 3, copyrightSafety: 3, accuracySafety: 4 },
    officialSources: ["DART 사업보고서", "기업 공식 IR 자료", "통계청 산업 통계"],
    note: "스토리텔링 수요가 높지만 사진·로고 사용 저작권, 애니메이션 제작 비용이 큼.",
  },
  {
    area: "경제정책이 개인 자산에 미치는 영향",
    scores: { demand: 4, timeliness: 4, competitionEase: 3, productionEase: 4, dataAccess: 4, copyrightSafety: 5, accuracySafety: 3 },
    officialSources: ["기획재정부 보도자료", "금융위원회 보도자료", "국가법령정보센터"],
    note: "정책 발표 직후 수요가 큼. 시행 전 내용과 확정 내용을 구분해야 함.",
  },
];

export function areaTotal(a: AreaEval): number {
  const s = a.scores;
  return s.demand + s.timeliness + s.competitionEase + s.productionEase + s.dataAccess + s.copyrightSafety + s.accuracySafety;
}

export interface TopicCandidate {
  id: number;
  area: string;
  titles: [string, string, string];
  audience: string;
  question: string;
  differentiation: string;
  sources: string[];
  structure: string[]; // 6~10분 구성
  difficulty: "하" | "중" | "상";
  visuals: string[];
  thumbnails: [string, string, string];
  shorts: [string, string];
  rationale: string;
  uncertainty: string;
  needsLiveData: boolean;
}

export const TOPICS: TopicCandidate[] = [
  {
    id: 1,
    area: "금리와 채권",
    titles: [
      "금리 내렸는데 내 대출이자는 왜 그대로일까? 3단계로 정리",
      "기준금리가 내 대출이자에 도착하기까지 걸리는 시간",
      "0.25%p 인하, 3억 대출이면 1년에 얼마 줄까?",
    ],
    audience: "변동금리 주택담보대출·신용대출을 보유한 30~40대",
    question: "기준금리 변경이 내 대출 금리에 언제, 어떤 경로로, 얼마나 반영되는가?",
    differentiation: "뉴스 해설이 아니라 '내 대출 약정서에서 확인할 3가지'로 끝나는 실용형 구조",
    sources: ["한국은행 통화정책방향 결정문", "은행연합회 COFIX 공시", "금감원 금융상품 한눈에", "은행법 제30조의2(금리인하요구권)"],
    structure: ["0:00 도입: 뉴스와 내 이자의 시차", "0:30 결론 먼저: 3단계 경로", "1:20 1단계 조달금리", "2:40 2단계 COFIX·금융채", "4:00 3단계 변동주기", "5:20 예시 계산", "6:40 가산·우대금리와 금리인하요구권", "7:40 체크리스트·마무리"],
    difficulty: "하",
    visuals: ["3단계 흐름도", "COFIX 구조 도식", "변동주기 타임라인", "이자 계산 표"],
    thumbnails: ["금리 내렸는데 내 이자는 그대로?", "기준금리 → 내 대출, 3단계", "0.25%p = 1년에 얼마?"],
    shorts: ["0.25%p 인하, 3억 대출 이자는 얼마나 줄까 (계산 1분)", "대출 약정서에서 꼭 볼 한 줄: 금리변동주기"],
    rationale: "공식 자료로 모든 주장을 검증 가능하고, 실시간 수치 없이도 구조 설명이 성립(에버그린). 차트·도식만으로 제작 가능(C·A형).",
    uncertainty: "최신 기준금리·COFIX 수치는 제작 시점에 공식 사이트에서 확인 후 기입해야 함. 개별 은행 상품마다 산정 방식 차이 존재.",
    needsLiveData: false,
  },
  {
    id: 2,
    area: "가계 자산과 금융상품",
    titles: ["예금자보호 한도, 정확히 무엇이 보호될까?", "은행이 망하면 내 예금은? 보호되는 것과 아닌 것", "적금·ISA·펀드, 예금자보호 되는 것만 골라보기"],
    audience: "예적금 비중이 높은 사회초년생·50대",
    question: "예금자보호제도는 어떤 상품을 얼마까지, 어떤 기준으로 보호하는가?",
    differentiation: "상품별 보호 여부를 표 하나로 정리",
    sources: ["예금보험공사 보호금융상품 안내", "예금자보호법"],
    structure: ["도입: 뱅크런 뉴스", "보호 한도와 계산 단위", "보호 상품 vs 비보호 상품 표", "흔한 오해 3가지", "체크리스트"],
    difficulty: "하",
    visuals: ["상품 분류표", "금융회사별 합산 예시 도식"],
    thumbnails: ["내 돈, 진짜 보호될까?", "보호 O / 보호 X", "은행이 망하면?"],
    shorts: ["예금자보호 안 되는 상품 3가지", "보호 한도는 은행마다 따로일까?"],
    rationale: "법·제도 기반이라 검증이 쉽고 오류 위험이 낮음.",
    uncertainty: "보호 한도 변경 등 제도 개정 시점을 반드시 확인해야 함.",
    needsLiveData: false,
  },
  {
    id: 3,
    area: "금리와 채권",
    titles: ["채권 가격은 왜 금리와 반대로 움직일까?", "금리가 내리면 채권으로 돈 버는 원리", "채권 ETF 사기 전 알아야 할 '듀레이션' 한 가지"],
    audience: "채권 투자를 처음 고민하는 개인 투자자",
    question: "금리와 채권 가격의 반대 관계는 어떤 계산에서 나오는가?",
    differentiation: "수식 없이 '쿠폰 비교' 비유와 단순 계산으로 설명",
    sources: ["금융투자협회 채권정보센터", "한국은행 경제용어사전"],
    structure: ["도입", "채권의 구조", "금리 변화 시 가격 계산 예시", "듀레이션 개념", "위험 요인"],
    difficulty: "중",
    visuals: ["시소 도식", "가격 계산 표", "듀레이션 막대"],
    thumbnails: ["금리↓ 채권↑ 왜?", "채권, 이것만 알면 된다", "듀레이션이 뭐길래"],
    shorts: ["채권 가격 공식 30초", "듀레이션 한 줄 정리"],
    rationale: "에버그린 개념 설명. 특정 상품 추천 없이 원리 중심.",
    uncertainty: "투자 권유로 오인되지 않도록 상품명 언급 자제 필요.",
    needsLiveData: false,
  },
  {
    id: 4,
    area: "경제정책이 개인 자산에 미치는 영향",
    titles: ["DSR이 뭐길래 대출 한도가 줄어들까?", "같은 연봉인데 대출 한도가 다른 이유: DSR", "스트레스 DSR, 내 한도에 미치는 영향"],
    audience: "내 집 마련을 준비하는 30대",
    question: "DSR 규제는 대출 한도를 어떤 계산으로 제한하는가?",
    differentiation: "연봉별 한도 계산 예시표",
    sources: ["금융위원회 가계부채 관리방안 보도자료", "은행연합회"],
    structure: ["도입", "DSR 정의", "계산 예시", "스트레스 DSR", "정리"],
    difficulty: "중",
    visuals: ["계산 흐름도", "연봉별 한도 표"],
    thumbnails: ["내 대출 한도가 줄어든 이유", "DSR 계산 1분", "연봉 5천, 한도는?"],
    shorts: ["DSR 40%의 의미", "스트레스 DSR 한 줄 정리"],
    rationale: "수요가 크고 공식 자료로 검증 가능.",
    uncertainty: "규제 단계·적용 시점이 자주 바뀌므로 최신 보도자료 확인 필수(실시간성 중간).",
    needsLiveData: true,
  },
  {
    id: 5,
    area: "가계 자산과 금융상품",
    titles: ["연금저축 vs IRP, 세액공제 차이 한 번에", "연말정산 전에 알아야 할 연금계좌 세액공제", "같은 돈을 넣어도 환급액이 다른 이유"],
    audience: "연말정산을 앞둔 직장인",
    question: "연금저축과 IRP의 세액공제 한도·비율은 어떻게 다른가?",
    differentiation: "소득 구간별 환급 예시 계산",
    sources: ["국세청 연말정산 안내", "금감원 통합연금포털"],
    structure: ["도입", "두 계좌 차이", "공제 한도 계산", "중도 인출 시 불이익", "체크리스트"],
    difficulty: "하",
    visuals: ["비교표", "환급 계산 표"],
    thumbnails: ["연금저축 vs IRP", "환급 더 받는 순서", "세액공제 한도 정리"],
    shorts: ["IRP 중도 인출하면?", "세액공제율 1분 정리"],
    rationale: "시즌성(연말) 수요가 크고 제도 기반이라 검증이 쉬움.",
    uncertainty: "세법 개정 여부를 해당 연도 기준으로 확인해야 함.",
    needsLiveData: false,
  },
  {
    id: 6,
    area: "부동산과 주택시장",
    titles: ["전세가율이 높으면 왜 위험할까?", "깡통전세를 숫자로 미리 알아보는 법", "전세 계약 전 확인할 공공 데이터 3가지"],
    audience: "전세 계약을 앞둔 2030 세입자",
    question: "전세가율·선순위 채권으로 보증금 위험을 어떻게 가늠하는가?",
    differentiation: "공공 데이터 조회 화면 녹화(스크린캐스트) 중심",
    sources: ["국토교통부 실거래가 공개시스템", "HUG 전세보증 안내", "대법원 인터넷등기소"],
    structure: ["도입", "전세가율 정의", "등기부 확인 포인트", "보증보험", "체크리스트"],
    difficulty: "중",
    visuals: ["스크린캐스트", "위험 신호 체크표"],
    thumbnails: ["이 숫자 넘으면 위험", "전세 계약 전 3분", "깡통전세 체크"],
    shorts: ["전세가율 계산 30초", "등기부에서 볼 한 줄"],
    rationale: "실용성 높고 C형(스크린캐스트)으로 제작 쉬움.",
    uncertainty: "법률 자문으로 오인되지 않도록 일반 정보임을 명시해야 함.",
    needsLiveData: false,
  },
  {
    id: 7,
    area: "기업과 산업의 흥망성쇠",
    titles: ["필름 회사는 왜 디지털에서 갈렸을까", "같은 위기, 다른 결말: 두 기업의 선택", "1등 기업이 무너지는 3가지 패턴"],
    audience: "기업 스토리를 좋아하는 일반 시청자",
    question: "기술 전환기에 기업의 결말을 가른 의사결정은 무엇이었나?",
    differentiation: "공시·연차보고서 수치로 스토리 근거 제시",
    sources: ["기업 연차보고서", "SEC EDGAR", "언론 보도(인용 범위 내)"],
    structure: ["도입", "전성기", "전환 신호", "선택과 결과", "교훈"],
    difficulty: "상",
    visuals: ["매출 추이 차트", "타임라인", "모션그래픽"],
    thumbnails: ["1등이 무너진 이유", "같은 위기 다른 결말", "이 선택이 갈랐다"],
    shorts: ["한 장면으로 보는 몰락", "숫자로 보는 전성기"],
    rationale: "상위 3개 벤치마킹 채널(애니메이션형)과 가장 유사한 포맷.",
    uncertainty: "로고·사진 사용권, 애니메이션 제작 시간 부담. 첫 영상으로는 난이도 높음.",
    needsLiveData: false,
  },
  {
    id: 8,
    area: "국내 주식과 미국 주식",
    titles: ["환율이 오르면 미국 주식 수익률은 어떻게 될까?", "달러로 산 주식, 원화로 계산하면 다르다", "환차익·환차손 계산 1번에 이해하기"],
    audience: "미국 주식 투자 입문자",
    question: "환율 변화가 원화 기준 수익률을 어떻게 바꾸는가?",
    differentiation: "종목 없이 가상의 예시로 환효과만 분리 설명",
    sources: ["한국은행 ECOS 환율 통계", "금감원 해외주식 투자 유의사항"],
    structure: ["도입", "두 개의 수익률", "계산 예시", "환헤지 상품 개념", "정리"],
    difficulty: "하",
    visuals: ["계산 표", "환율 추이 차트"],
    thumbnails: ["주가는 올랐는데 손해?", "환율의 함정", "달러 수익률 ≠ 원화 수익률"],
    shorts: ["환차손 계산 30초", "환헤지 한 줄"],
    rationale: "종목 추천 없이 원리 설명 가능, 검증 쉬움.",
    uncertainty: "최근 환율 수치를 쓸 경우 기준일 표기 필요.",
    needsLiveData: false,
  },
  {
    id: 9,
    area: "경제정책이 개인 자산에 미치는 영향",
    titles: ["물가 2%는 내 장바구니에선 몇 %일까?", "소비자물가지수, 체감 물가와 다른 이유", "물가지수는 어떻게 계산될까"],
    audience: "생활비가 늘어난 체감과 통계 차이가 궁금한 시청자",
    question: "CPI는 어떻게 계산되며 왜 개인 체감과 다를 수 있는가?",
    differentiation: "가중치 구조를 '내 소비 바구니'와 비교",
    sources: ["통계청 소비자물가동향", "KOSIS"],
    structure: ["도입", "CPI 계산 방식", "가중치", "체감 물가와 차이", "정리"],
    difficulty: "중",
    visuals: ["가중치 파이차트", "품목별 상승률 차트"],
    thumbnails: ["물가 2%의 진실", "내 물가는 왜 더 높을까", "물가지수 해부"],
    shorts: ["CPI 가중치 1위는?", "체감 물가가 다른 이유"],
    rationale: "공식 통계 기반, 일상과 지표 연결 구조에 적합.",
    uncertainty: "최신 월 수치는 발표 일정 확인 필요.",
    needsLiveData: true,
  },
  {
    id: 10,
    area: "부동산과 주택시장",
    titles: ["청약 가점 84점은 어떻게 계산될까?", "청약 가점, 내 점수 1분 계산", "무주택 기간이 점수에 주는 영향"],
    audience: "청약을 준비하는 무주택자",
    question: "청약 가점은 어떤 항목으로 계산되는가?",
    differentiation: "가상 인물 3명의 가점 계산 비교",
    sources: ["청약홈(한국부동산원)", "주택공급에 관한 규칙"],
    structure: ["도입", "가점 항목", "계산 예시", "자주 하는 실수", "정리"],
    difficulty: "하",
    visuals: ["가점 표", "계산 애니메이션"],
    thumbnails: ["내 청약 점수는?", "84점 계산법", "무주택 기간의 힘"],
    shorts: ["가점 항목 3개", "부양가족 점수 계산"],
    rationale: "계산형 콘텐츠로 검증 쉬움, 반복 수요 존재.",
    uncertainty: "제도 개정 여부 확인 필요.",
    needsLiveData: false,
  },
];

export const FINAL_TOPIC_ID = 1;

export const FINAL_REASON = [
  "모든 핵심 주장을 한국은행·은행연합회·금융감독원·국가법령정보센터 자료로 검증할 수 있음",
  "최신 수치가 없어도 구조 설명이 성립하는 에버그린 주제 — 수치는 제작 당일 공식 사이트에서 확인해 3곳에만 기입",
  "벤치마킹 분석에서 관측된 '경제지표 → 내 생활' 연결 구조와 숫자형 제목을 그대로 원리로 적용 가능 (원문 복제 없음)",
  "도식·차트·자막만으로 제작 가능한 A/C형이라 초보자 1인 제작 난이도 '하'",
  "특정 상품·종목 추천이 없어 투자 권유 오인 위험이 낮음",
];
