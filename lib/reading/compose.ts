// 사주(두 엔진 합의) + 관상 결과로 '우리 의견'을 만든다. (API 키가 없어도 동작하는 규칙 기반 해석)
import { BRANCHES, BRANCH_ELEMENT, CONTROLS, ELEMENTS, STEM_ELEMENT, type Element } from "../saju/constants";
import type { SajuConsensus } from "../saju/types";
import type { FeatureScores, FeatureReading } from "../face/physiognomy";
import { faceThemes } from "../face/physiognomy";
import { THEMES, THEME_KEYS, sajuThemes, type ThemeKey } from "./themes";
import type { CommonTheme, Reading, Section, SectionItem } from "./types";

export const DAY_MASTER: Record<string, string> = {
  甲: "당신은 곧게 뻗는 큰 나무 같은 사람입니다. 바르고 곧은 성품에 위로 성장하려는 욕구가 강합니다.",
  乙: "당신은 덩굴과 꽃 같은 사람입니다. 부드럽지만 질기고, 어떤 환경에도 적응하는 생명력이 있습니다.",
  丙: "당신은 하늘의 태양 같은 사람입니다. 밝고 화끈하며 주변을 환하게 비추는 존재감이 있습니다.",
  丁: "당신은 촛불과 등불 같은 사람입니다. 따뜻하고 섬세하며, 한 곳을 오래 밝히는 집중력이 있습니다.",
  戊: "당신은 큰 산 같은 사람입니다. 묵직하고 믿음직하며, 사람들이 기댈 수 있는 중심이 됩니다.",
  己: "당신은 기름진 논밭 같은 사람입니다. 포용력이 있고 사람과 일을 길러 내는 능력이 있습니다.",
  庚: "당신은 단단한 바위와 무쇠 같은 사람입니다. 결단력과 의리가 있고, 맺고 끊음이 분명합니다.",
  辛: "당신은 빛나는 보석 같은 사람입니다. 예리한 감각과 자존심, 완벽을 추구하는 기질이 있습니다.",
  壬: "당신은 큰 바다와 강 같은 사람입니다. 스케일이 크고 지혜로우며, 막히면 돌아가는 유연함이 있습니다.",
  癸: "당신은 비와 이슬 같은 사람입니다. 조용하지만 깊이 스며드는 힘, 뛰어난 직관과 기획력이 있습니다.",
};

const HEADLINE: Record<ThemeKey, string> = {
  leadership: "앞에 서야 빛나는 사람",
  wealth: "흐름을 읽고 재물을 모으는 사람",
  expression: "말과 표현으로 세상을 움직이는 사람",
  sensitivity: "남들이 못 보는 것을 보는 사람",
  stability: "시간이 지날수록 단단해지는 사람",
  intellect: "깊이 생각하고 멀리 보는 사람",
  sociability: "사람이 곧 복인 사람",
  willpower: "끝까지 가는 사람",
  independence: "스스로 길을 만드는 사람",
};

const YEAR_TEXT: Record<string, string> = {
  비견: "나와 비슷한 사람들이 모여드는 해입니다. 독립과 자기 주도의 기회가 오지만, 동업과 보증은 신중하세요.",
  겁재: "경쟁이 뜨거워지는 해입니다. 과감한 도전이 성과로 이어질 수 있지만, 돈이 새어 나가지 않게 지갑을 단단히 하세요.",
  식신: "재능이 꽃피고 생활이 넉넉해지는 해입니다. 새로운 취미나 창작을 시작하기 좋습니다.",
  상관: "표현하고 바꾸고 싶은 마음이 커지는 해입니다. 이직·전환의 기회가 있지만 말실수와 윗사람과의 마찰을 조심하세요.",
  편재: "큰 돈의 흐름이 보이는 해입니다. 사업·투자 기회가 오지만 무리한 확장은 피하세요.",
  정재: "꾸준한 수입과 안정이 찾아오는 해입니다. 저축과 자산 정리에 좋은 시기입니다.",
  편관: "책임과 압박이 커지는 시험대의 해입니다. 버텨 내면 한 단계 올라서지만, 과로와 건강 관리가 우선입니다.",
  정관: "인정과 명예가 따르는 해입니다. 승진·합격·계약·결혼처럼 공식적인 좋은 일이 생기기 쉽습니다.",
  편인: "공부와 자기 성찰의 해입니다. 자격증·전문성에 투자하기 좋지만, 생각만 많아지지 않게 실행을 챙기세요.",
  정인: "귀인의 도움과 문서운이 따르는 해입니다. 배움과 계약, 집과 관련된 일에 좋은 흐름입니다.",
};

const DAEUN_TEXT: Record<string, string> = {
  비견: "자립의 10년", 겁재: "경쟁과 도전의 10년", 식신: "재능과 여유의 10년", 상관: "변화와 표현의 10년",
  편재: "기회와 확장의 10년", 정재: "축적과 안정의 10년", 편관: "시련 속 성장의 10년", 정관: "명예와 인정의 10년",
  편인: "탐구와 전환의 10년", 정인: "배움과 귀인의 10년",
};

const HEALTH: Record<Element, string> = {
  목: "간·눈·근육과 관절",
  화: "심장·혈압·혈액순환",
  토: "위장과 소화 기능",
  금: "폐·호흡기·피부",
  수: "신장·방광, 몸의 냉기",
};

const BOOST: Record<Element, string> = {
  목: "초록색 소품, 아침 산책, 식물 기르기",
  화: "따뜻한 색감, 햇볕 쬐기, 땀 흘리는 운동",
  토: "베이지·노란 계열, 규칙적인 식사, 흙을 밟는 시간",
  금: "흰색·메탈 소품, 공간 정리정돈, 호흡 운동",
  수: "검정·남색 계열, 물 자주 마시기, 충분한 수면",
};

const FEATURE_PART: Record<keyof FeatureScores, string> = {
  forehead: "이마", eyes: "눈", eyeGap: "눈 사이", eyeTilt: "눈꼬리", nose: "코", mouth: "입", lips: "입술",
  smile: "입꼬리", jaw: "턱", cheek: "광대", chin: "턱끝", upper: "상정", middle: "중정", lower: "하관",
};
const THEME_FEATURES: Record<ThemeKey, (keyof FeatureScores)[]> = {
  intellect: ["forehead"],
  sensitivity: ["eyes"],
  expression: ["mouth", "eyes", "lips"],
  sociability: ["eyeGap", "smile", "lips"],
  wealth: ["nose"],
  leadership: ["cheek", "eyeTilt"],
  willpower: ["jaw", "chin", "nose"],
  stability: ["jaw", "lower"],
  independence: ["cheek", "eyeTilt"],
};


// ── 확장 콘텐츠 표 ──────────────────────────────────────────
const ELEMENT_TRAIT: Record<Element, { name: string; many: string; few: string; person: string }> = {
  목: {
    name: "나무",
    many: "나무 기운이 강해 성장 욕구와 추진력이 크고, 새로 시작하는 일에 강합니다. 다만 고집이 세질 수 있어 한 박자 쉬어 가는 연습이 필요합니다.",
    few: "나무 기운이 약해 새로 시작하는 데 시간이 걸리는 편입니다. 아침 산책이나 식물 기르기처럼 꾸준히 자라는 습관이 기운을 채워 줍니다.",
    person: "새로운 걸 시작하길 좋아하고 곧은 성격의 사람",
  },
  화: {
    name: "불",
    many: "불 기운이 강해 밝고 열정적이며, 사람들 앞에서 빛납니다. 다만 쉽게 달아올랐다 식을 수 있어 꾸준함을 의식적으로 챙기세요.",
    few: "불 기운이 약해 감정 표현이 조심스러운 편입니다. 햇볕을 쬐고 땀 흘리는 운동을 하면 활력이 살아납니다.",
    person: "밝고 표현이 솔직한 사람",
  },
  토: {
    name: "흙",
    many: "흙 기운이 강해 믿음직하고 중심을 잘 잡습니다. 다만 변화를 미루기 쉬우니 가끔은 익숙한 곳에서 벗어나 보세요.",
    few: "흙 기운이 약해 생활 리듬이 흔들리기 쉽습니다. 일정한 시간에 먹고 자는 것만으로도 운이 안정됩니다.",
    person: "듬직하고 약속을 잘 지키는 사람",
  },
  금: {
    name: "쇠",
    many: "쇠 기운이 강해 결단력과 원칙이 분명합니다. 다만 말과 판단이 날카롭게 느껴질 수 있어 부드러운 표현을 곁들이면 좋습니다.",
    few: "쇠 기운이 약해 맺고 끊는 일을 어려워할 수 있습니다. 공간을 정리하고 우선순위를 적어 보는 습관이 도움이 됩니다.",
    person: "깔끔하고 맺고 끊음이 분명한 사람",
  },
  수: {
    name: "물",
    many: "물 기운이 강해 생각이 깊고 지혜롭습니다. 다만 걱정이 많아질 수 있으니 생각을 글로 적어 정리해 보세요.",
    few: "물 기운이 약해 쉬지 않고 달리기 쉽습니다. 충분한 수면과 물 자주 마시기가 가장 좋은 보약입니다.",
    person: "차분하고 생각이 깊은 사람",
  },
};

const LUCK: Record<Element, { color: string; direction: string; number: string; season: string; thing: string }> = {
  목: { color: "초록·청록", direction: "동쪽", number: "3, 8", season: "봄", thing: "화분, 나무 소품, 아침 산책" },
  화: { color: "빨강·주황", direction: "남쪽", number: "2, 7", season: "여름", thing: "햇볕, 캔들, 땀 흘리는 운동" },
  토: { color: "노랑·베이지", direction: "가운데(집과 일터의 중심)", number: "5, 10", season: "환절기", thing: "도자기, 규칙적인 식사, 흙길 걷기" },
  금: { color: "흰색·은색", direction: "서쪽", number: "4, 9", season: "가을", thing: "금속 액세서리, 정리정돈, 호흡 운동" },
  수: { color: "검정·남색", direction: "북쪽", number: "1, 6", season: "겨울", thing: "물 마시기, 수영, 충분한 수면" },
};

const LOVE_STYLE: Record<Element, string> = {
  목: "연애에서도 함께 성장하는 관계를 원합니다. 서로의 꿈을 응원해 주는 사람을 만날 때 가장 오래갑니다.",
  화: "마음이 가면 숨기지 못하는 직진형입니다. 표현이 큰 만큼 상대의 속도도 한 번 살펴 주세요.",
  토: "천천히 마음을 열지만 한 번 시작하면 끝까지 지키는 사람입니다. 안정감을 주는 상대와 잘 맞습니다.",
  금: "기준이 분명해 아무나 만나지 않습니다. 믿음이 쌓이면 누구보다 든든한 짝이 됩니다.",
  수: "상대의 마음을 깊이 헤아리는 배려형입니다. 혼자 서운함을 삼키지 말고 말로 꺼내는 연습이 필요합니다.",
};

const DAEUN_LONG: Record<string, string> = {
  비견: "스스로 서는 법을 배우는 시기입니다. 독립, 창업, 내 이름을 건 일이 잘 맞습니다.",
  겁재: "경쟁 속에서 크는 시기입니다. 과감한 도전이 통하지만 돈 관리는 보수적으로 하세요.",
  식신: "재능이 꽃피고 생활이 넉넉해지는 시기입니다. 좋아하는 일을 일로 만들기 좋습니다.",
  상관: "틀을 깨고 바꾸고 싶은 마음이 커지는 시기입니다. 표현력이 빛나지만 말조심이 필요합니다.",
  편재: "큰 기회와 돈의 흐름이 보이는 시기입니다. 사업과 투자의 기회가 오지만 확장은 단계적으로.",
  정재: "차곡차곡 쌓이는 시기입니다. 저축, 집, 안정적인 수입이 자리 잡습니다.",
  편관: "책임과 압박 속에서 단단해지는 시기입니다. 버티면 한 단계 위로 올라섭니다.",
  정관: "인정과 명예가 따르는 시기입니다. 승진, 자격, 결혼처럼 공식적인 좋은 일이 많습니다.",
  편인: "공부와 전환의 시기입니다. 새로운 분야를 익히거나 방향을 바꾸기 좋습니다.",
  정인: "귀인의 도움과 배움이 따르는 시기입니다. 문서, 계약, 자격과 관련된 일이 잘 풀립니다.",
};

const WORK_STYLE: Record<string, string> = {
  strong: "기운이 단단한 편이라 남의 지시보다 스스로 판단할 때 실력이 나옵니다. 재량이 큰 자리, 책임을 맡는 자리에서 성과가 큽니다.",
  weak: "주변의 도움과 좋은 환경에서 실력이 커지는 타입입니다. 혼자 다 하려 하기보다 좋은 팀과 선배를 곁에 두세요.",
  neutral: "기운이 고르게 균형을 이뤄 어느 자리에서든 적응이 빠릅니다. 꾸준함이 가장 큰 무기입니다.",
  undetermined: "상황에 따라 앞에 서기도, 뒤에서 받치기도 하는 유연한 타입입니다. 맡은 역할을 분명히 정하면 실력이 더 드러납니다.",
};


// ── 달별 상세 (돈 · 일 · 사람 · 몸 · 이달의 한 가지) ──────────────
const MONTH_DETAIL: Record<string, { theme: string; money: string; work: string; people: string; body: string; todo: string }> = {
  비견: {
    theme: "내 편이 모이는 달",
    money: "들어오는 만큼 나가기 쉽습니다. 모임·경조사비 예산을 미리 정해 두세요.",
    work: "혼자보다 팀으로 할 때 속도가 붙습니다. 역할 분담을 분명히 하세요.",
    people: "오랜 친구·동료와 다시 가까워집니다. 다만 돈이 얽힌 부탁은 정중히 거절하세요.",
    body: "기운은 좋은 편입니다. 함께하는 운동이 꾸준함을 만들어 줍니다.",
    todo: "미뤄 둔 연락 한 통 하기",
  },
  겁재: {
    theme: "승부가 붙는 달",
    money: "충동 지출과 돈 거래가 가장 큰 구멍입니다. 큰 결제는 하루 묵혀 두세요.",
    work: "경쟁자가 보이지만 정면 승부에서 얻는 것이 큽니다. 실력으로 보여 주세요.",
    people: "자존심 싸움이 생기기 쉽습니다. 이기는 것보다 남는 것을 생각하세요.",
    body: "과격한 운동이나 무리한 일정에서 다치기 쉽습니다. 준비 운동을 꼭 하세요.",
    todo: "카드 한 장 줄이고 지출 기록하기",
  },
  식신: {
    theme: "몸과 마음이 넉넉해지는 달",
    money: "작은 기쁨에 쓰는 돈은 아깝지 않지만, 먹고 마시는 지출이 늘기 쉽습니다.",
    work: "좋아하는 일에서 성과가 납니다. 재능을 보여 줄 작은 기회를 놓치지 마세요.",
    people: "편안한 사람이 곁에 머뭅니다. 함께 밥 먹는 자리에서 좋은 인연이 이어집니다.",
    body: "식욕이 늘어 체중이 붙기 쉽습니다. 저녁 과식만 조심하면 컨디션이 최상입니다.",
    todo: "새 취미 하나 시작하기",
  },
  상관: {
    theme: "아이디어가 터지는 달",
    money: "기발한 생각이 돈이 될 수 있습니다. 다만 홧김에 하는 소비는 피하세요.",
    work: "기획·발표·제안에 강합니다. 다만 윗사람의 방식을 정면으로 비판하지는 마세요.",
    people: "말이 날카로워지기 쉽습니다. 메시지는 보내기 전에 한 번 더 읽어 보세요.",
    body: "신경이 예민해져 잠이 얕아질 수 있습니다. 자기 전 화면 보는 시간을 줄이세요.",
    todo: "떠오른 아이디어를 메모장에 모아 두기",
  },
  편재: {
    theme: "기회와 돈이 움직이는 달",
    money: "뜻밖의 수입이나 거래 기회가 옵니다. 들어온 돈의 절반은 바로 따로 떼어 두세요.",
    work: "영업·거래·외부 활동이 잘 풀립니다. 발로 뛰는 만큼 결과가 따라옵니다.",
    people: "새로운 사람을 많이 만납니다. 첫인상이 좋은 사람일수록 약속은 문서로 남기세요.",
    body: "바쁘게 움직이다 끼니를 거르기 쉽습니다. 이동 중에도 물과 간식을 챙기세요.",
    todo: "부수입 아이디어 하나 실행해 보기",
  },
  정재: {
    theme: "차곡차곡 쌓이는 달",
    money: "꾸준히 해 온 일이 돈으로 돌아옵니다. 적금·저축을 시작하기 가장 좋은 때입니다.",
    work: "성실함이 평가받습니다. 정리·정산·마무리 작업에서 실력이 드러납니다.",
    people: "믿을 만한 사람과의 관계가 깊어집니다. 연인·배우자와 미래 계획을 이야기해 보세요.",
    body: "생활 리듬이 안정됩니다. 같은 시간에 자고 일어나는 습관을 굳히기 좋습니다.",
    todo: "자동이체로 저축 하나 걸어 두기",
  },
  편관: {
    theme: "책임이 무거워지는 달",
    money: "예상치 못한 지출이 생길 수 있습니다. 비상금을 건드리지 않게 미리 대비하세요.",
    work: "일이 몰리고 압박이 큽니다. 버티면 실력이 한 단계 올라가는 달입니다.",
    people: "윗사람·기관과의 일이 많아집니다. 감정보다 원칙으로 대응하세요.",
    body: "과로가 가장 큰 적입니다. 잠을 먼저 챙기고, 몸이 보내는 신호를 무시하지 마세요.",
    todo: "일정표에서 한 가지 빼기",
  },
  정관: {
    theme: "인정받는 달",
    money: "안정적인 수입 흐름이 이어집니다. 연봉·계약 조건을 이야기하기 좋은 때입니다.",
    work: "면접·승진·평가에 좋은 달입니다. 공식적인 자리에서 나를 드러내세요.",
    people: "신뢰가 쌓이는 달입니다. 소개팅·상견례처럼 격식 있는 만남도 잘 풀립니다.",
    body: "규칙적인 생활이 운을 받쳐 줍니다. 건강검진 날짜를 잡기 좋습니다.",
    todo: "이력서·포트폴리오 한 줄 업데이트하기",
  },
  편인: {
    theme: "생각이 깊어지는 달",
    money: "큰돈을 벌기보다 지키는 달입니다. 공부·자기계발에 쓰는 돈은 투자입니다.",
    work: "기획·연구·전환을 준비하기 좋습니다. 방향을 다시 잡는 시간으로 쓰세요.",
    people: "혼자 있고 싶어질 수 있습니다. 가까운 사람에게는 이유를 말해 두세요.",
    body: "생각이 많아 머리가 무거워집니다. 걷기와 가벼운 산책이 머리를 비워 줍니다.",
    todo: "배우고 싶던 것 한 가지 등록하기",
  },
  정인: {
    theme: "도움이 들어오는 달",
    money: "문서·계약과 관련된 이득이 있습니다. 서류는 꼼꼼히 읽고 서명하세요.",
    work: "선배·윗사람의 도움으로 일이 풀립니다. 혼자 끙끙대지 말고 먼저 물어보세요.",
    people: "어른·스승 같은 귀인이 나타납니다. 감사 인사를 표현하면 인연이 오래갑니다.",
    body: "마음이 편안해지는 달입니다. 충분히 쉬면서 다음 달을 준비하세요.",
    todo: "도움받은 사람에게 감사 인사 전하기",
  },
};

// ── 행운 포인트 상세 ──────────────
const LUCK_MORE: Record<Element, { colorUse: string; directionUse: string; day: string; time: string; food: string; place: string; hobby: string; zodiac: string; item: string }> = {
  목: { colorUse: "초록 계열 셔츠·폰 케이스·지갑", directionUse: "책상은 동쪽을 보게, 여행은 동쪽 지방으로", day: "목요일", time: "아침 5시~9시", food: "푸른 채소, 신맛 나는 과일, 나물", place: "숲길, 공원, 식물원", hobby: "등산, 원예, 독서 모임", zodiac: "호랑이띠, 토끼띠", item: "작은 화분, 나무 소품, 종이책" },
  화: { colorUse: "붉은 계열 소품·립 컬러·가방 포인트", directionUse: "책상은 남쪽을 보게, 여행은 남쪽 바닷가로", day: "화요일", time: "한낮 11시~오후 3시", food: "쓴맛 나는 차, 붉은 과일, 구운 요리", place: "햇살 좋은 카페, 전망대, 공연장", hobby: "댄스, 땀 흘리는 운동, 사진 찍기", zodiac: "뱀띠, 말띠", item: "캔들, 조명, 붉은 소품" },
  토: { colorUse: "베이지·노랑 계열 니트·가방·침구", directionUse: "집과 일터의 한가운데를 깨끗이, 여행은 내륙 지방으로", day: "토요일", time: "오후 1시~5시", food: "단호박, 고구마, 잡곡밥", place: "흙길, 도자기 공방, 시골 마을", hobby: "요리, 도예, 텃밭 가꾸기", zodiac: "소띠, 용띠, 양띠, 개띠", item: "도자기 그릇, 원목 쟁반, 향 주머니" },
  금: { colorUse: "흰색·은색 계열 셔츠·시계·액세서리", directionUse: "책상은 서쪽을 보게, 여행은 서해안으로", day: "금요일", time: "저녁 5시~9시", food: "배, 무, 매운맛 나는 음식", place: "정돈된 서점, 미술관, 바위산", hobby: "호흡 운동, 악기 연주, 정리정돈", zodiac: "원숭이띠, 닭띠", item: "금속 시계, 은반지, 깔끔한 펜" },
  수: { colorUse: "검정·남색 계열 코트·가방·신발", directionUse: "침대 머리는 북쪽으로, 여행은 강과 바다가 있는 곳으로", day: "수요일", time: "밤 9시~새벽 1시", food: "검은콩, 해조류, 짭짤한 국물 요리", place: "강변, 바닷가, 수영장, 조용한 도서관", hobby: "수영, 명상, 일기 쓰기", zodiac: "쥐띠, 돼지띠", item: "물병, 작은 어항, 푸른 유리 소품" },
};

// ── 기간별 운세 (이번 주 · 다음 주 · 이번 달 · 다음 달 · 올해 · 내년) ──────────────
const GOOD: Record<string, string> = {
  비견: "동료·친구와 힘을 합치는 일, 스스로 결정하는 일",
  겁재: "과감한 도전, 경쟁이 붙은 승부",
  식신: "새 취미, 창작, 맛있는 식사와 충분한 휴식",
  상관: "아이디어 제안, 발표, 새로운 시도",
  편재: "부수입·거래·영업, 뜻밖의 기회 잡기",
  정재: "저축과 정산, 꾸준히 해 온 일의 결실",
  편관: "어려운 과제 정면 돌파, 책임 있는 자리",
  정관: "면접·승진·계약 같은 공식적인 일",
  편인: "공부·자격증·계획 세우기",
  정인: "도움 요청, 서류·계약, 배움",
};
const BAD: Record<string, string> = {
  비견: "돈 빌려주기, 동업 제안 덜컥 수락하기",
  겁재: "충동 지출, 보증, 돈 거래",
  식신: "과식·과음, 해야 할 일 미루기",
  상관: "윗사람과의 말다툼, SNS·메신저 말실수",
  편재: "무리한 투자, 한 번에 크게 거는 결정",
  정재: "지나친 절약으로 기회를 놓치는 것",
  편관: "과로와 무리한 일정, 건강 소홀",
  정관: "규칙 위반, 서류·마감 실수",
  편인: "생각만 하고 미루기, 혼자 고립되기",
  정인: "남에게 기대기만 하기, 결정 미루기",
};
const SCORE: Record<string, number> = { 식신: 2, 정재: 2, 정관: 2, 정인: 2, 편재: 1, 비견: 0, 편인: 0, 상관: -1, 겁재: -1, 편관: -1 };
const WEEKDAY = ["일", "월", "화", "수", "목", "금", "토"];

type Day = SajuConsensus["days"][number];
const md = (iso: string) => `${Number(iso.slice(5, 7))}월 ${Number(iso.slice(8, 10))}일`;
const dayLabel = (d: Day) => `${md(d.date)}(${WEEKDAY.at(d.weekday)})`;
const dayScore = (d: Day) => (SCORE[d.tenGod] ?? 0) + (SCORE[d.branchTenGod] ?? 0) - (d.clash ? 4 : 0);

/** 여러 날(또는 달)의 기운 중 가장 많이 나온 것 */
function dominant(gods: string[]) {
  const c: Record<string, number> = {};
  for (const g of gods) c[g] = (c[g] ?? 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "비견";
}

function weekBlock(days: Day[]) {
  const main = dominant(days.flatMap((d) => [d.tenGod, d.branchTenGod]));
  const sorted = [...days].sort((a, b) => dayScore(b) - dayScore(a));
  const best = sorted[0];
  const worst = [...days].sort((a, b) => dayScore(a) - dayScore(b))[0];
  return { main, best, worst };
}

const stars = (n: number) => {
  const k = Math.max(1, Math.min(5, Math.round(n)));
  return "★".repeat(k) + "☆".repeat(5 - k);
};
const dot = (t: string) => (/[.!?다요]$/.test(t) ? t : `${t}.`);
/** 표 항목을 소리 내어 읽기·AI·PDF용 문장으로 바꾼다 */
const itemLine = (i: SectionItem) =>
  `${i.label} — ${i.title ? dot(i.title) + " " : ""}${i.rows.map((r) => `${r.k}: ${dot(r.v)}`).join(" ")}`;
const withItems = (id: string, title: string, lead: string, items: SectionItem[]): Section => ({
  id,
  eyebrow: "",
  title,
  body: [lead, ...items.map(itemLine)],
  items,
});

const DAY_TITLE: Record<string, string> = {
  비견: "내 편이 생기는 날", 겁재: "승부욕이 오르는 날", 식신: "여유롭고 즐거운 날", 상관: "말과 아이디어의 날",
  편재: "기회가 굴러오는 날", 정재: "차분히 쌓는 날", 편관: "부담이 큰 날", 정관: "인정받는 날",
  편인: "생각이 깊어지는 날", 정인: "도움받는 날",
};

function timeSections(saju: SajuConsensus): Section[] {
  const out: Section[] = [];
  const days = saju.days;
  if (days.length) {
    // 이번 주: 오늘 ~ 이번 주 일요일 (일요일이면 오늘 하루)
    const restOfWeek: Day[] = [];
    for (const d of days) {
      restOfWeek.push(d);
      if (d.weekday === 0) break;
    }
    const nextWeek = days.slice(restOfWeek.length, restOfWeek.length + 7);
    const w = weekBlock(restOfWeek);
    const clashDay = restOfWeek.find((d) => d.clash);
    const summary: SectionItem = {
      label: "이번 주 한눈에",
      badge: stars(3 + restOfWeek.reduce((a, d) => a + dayScore(d), 0) / restOfWeek.length / 2),
      title: MONTH_DETAIL[w.main]?.theme.replace("달", "주"),
      rows: [
        { k: "잘되는 일", v: GOOD[w.main] },
        { k: "조심할 일", v: BAD[w.main] },
      ],
    };
    if (restOfWeek.length > 1) summary.rows.push({ k: "좋은 날", v: `${dayLabel(w.best)}, ${GOOD[w.best.tenGod]}에 힘을 실어 보세요` });
    if (clashDay) summary.rows.push({ k: "조심할 날", v: `${dayLabel(clashDay)}, 나와 부딪치는 기운이 들어옵니다. 이동·이사·큰 결정은 미루세요` });
    else if (restOfWeek.length > 1 && w.worst !== w.best && dayScore(w.worst) < 0)
      summary.rows.push({ k: "조심할 날", v: `${dayLabel(w.worst)}, ${BAD[w.worst.tenGod]}을 특히 조심하세요` });
    const daily: SectionItem[] = restOfWeek.map((d) => ({
      label: dayLabel(d),
      badge: stars(3 + dayScore(d) / 2),
      title: d.clash ? "부딪치는 기운이 들어오는 날" : DAY_TITLE[d.tenGod],
      rows: [
        { k: "좋은 일", v: GOOD[d.tenGod] },
        { k: "조심", v: d.clash ? "운전·이동, 다툼, 큰 결정" : BAD[d.branchTenGod] ?? BAD[d.tenGod] },
      ],
    }));
    out.push(
      withItems(
        "week",
        "이번 주 운세",
        `${dayLabel(restOfWeek[0])}부터 ${dayLabel(restOfWeek[restOfWeek.length - 1])}까지, 하루하루의 흐름입니다.`,
        [summary, ...daily],
      ),
    );

    const periods: SectionItem[] = [];
    if (nextWeek.length) {
      const n = weekBlock(nextWeek);
      const nClash = nextWeek.find((d) => d.clash);
      const rows = [
        { k: "잘되는 일", v: GOOD[n.main] },
        { k: "조심할 일", v: BAD[n.main] },
        { k: "좋은 날", v: `${dayLabel(n.best)}` },
      ];
      if (nClash) rows.push({ k: "조심할 날", v: `${dayLabel(nClash)}, 이동과 큰 결정을 피하세요` });
      periods.push({
        label: `다음 주 (${md(nextWeek[0].date)}~${md(nextWeek[nextWeek.length - 1].date)})`,
        badge: stars(3 + nextWeek.reduce((a, d) => a + dayScore(d), 0) / nextWeek.length / 2),
        title: MONTH_DETAIL[n.main]?.theme.replace("달", "주"),
        rows,
      });
    }
    const [m0, m1] = saju.months;
    for (const [m, name] of [[m0, "이번 달"], [m1, "다음 달"]] as const)
      if (m)
        periods.push({
          label: `${name} (${m.month}월)`,
          badge: stars(monthScore(saju, m)),
          title: MONTH_DETAIL[m.tenGod]?.theme,
          rows: [
            { k: "잘되는 일", v: GOOD[m.tenGod] },
            { k: "조심할 일", v: BAD[m.tenGod] },
          ],
        });
    const [y0, y1] = saju.years;
    for (const [y, name] of [[y0, `올해 (${y0?.year}년 남은 기간)`], [y1, `내년 (${y1?.year}년)`]] as const)
      if (y)
        periods.push({
          label: name,
          badge: stars(3 + ((SCORE[y.tenGod] ?? 0) + (SCORE[y.branchTenGod] ?? 0)) / 2),
          title: YEAR_TEXT[y.tenGod],
          rows: [
            { k: "잘되는 일", v: GOOD[y.tenGod] },
            { k: "조심할 일", v: BAD[y.tenGod] },
            { k: "하반기", v: `${GOOD[y.branchTenGod]} 쪽으로 기운이 옮겨 갑니다` },
          ],
        });
    if (saju.currentDaeun)
      periods.push({
        label: "지금의 10년",
        title: `${saju.currentDaeun.startAge}세부터 ‘${DAEUN_TEXT[saju.currentDaeun.stemTenGod] ?? "흐름이 바뀌는 10년"}’ 속에 있습니다`,
        rows: [{ k: "열쇠", v: DAEUN_LONG[saju.currentDaeun.stemTenGod] ?? "흐름에 맞춰 차근차근 나아가세요" }],
      });
    out.push(withItems("periods", "다가오는 흐름", "오늘 이후 다가올 흐름을 기간별로 정리했습니다. 별이 많을수록 순조로운 시기입니다.", periods));
  }
  return out;
}

type Month = SajuConsensus["months"][number];
const dayBranchOf = (saju: SajuConsensus) => saju.pillars.find((p) => p.key === "day")?.ganzhi[1] ?? "";
const clashes = (a: string, b: string) => {
  const i = BRANCHES.indexOf(a as (typeof BRANCHES)[number]);
  const j = BRANCHES.indexOf(b as (typeof BRANCHES)[number]);
  return i >= 0 && j >= 0 && Math.abs(i - j) === 6;
};
const helps = (saju: SajuConsensus, gz: string) =>
  saju.yongsin.find((e) => STEM_ELEMENT[gz[0]] === e || BRANCH_ELEMENT[gz[1]] === e);
function monthScore(saju: SajuConsensus, m: Month) {
  return 3 + ((SCORE[m.tenGod] ?? 0) + (SCORE[m.branchTenGod] ?? 0)) / 2 + (helps(saju, m.ganzhi) ? 1 : 0) - (clashes(m.ganzhi[1], dayBranchOf(saju)) ? 1 : 0);
}

function monthItem(saju: SajuConsensus, m: Month): SectionItem {
  const d = MONTH_DETAIL[m.tenGod] ?? MONTH_DETAIL.비견;
  const rows = [
    { k: "잘되는 일", v: GOOD[m.tenGod] },
    { k: "조심할 일", v: BAD[m.tenGod] },
    { k: "돈", v: d.money },
    { k: "일", v: d.work },
    { k: "사람", v: d.people },
    { k: "몸", v: d.body },
  ];
  if (m.branchTenGod !== m.tenGod) rows.push({ k: "달 후반", v: `${GOOD[m.branchTenGod]} 쪽으로 기운이 옮겨 갑니다` });
  const help = helps(saju, m.ganzhi);
  if (help) rows.push({ k: "기운", v: `나를 돕는 ${ELEMENT_TRAIT[help].name} 기운이 들어와 힘이 붙습니다` });
  if (clashes(m.ganzhi[1], dayBranchOf(saju))) rows.push({ k: "주의", v: "나와 부딪치는 기운이 있어 이사·이직·큰 계약은 한 번 더 따져 보세요" });
  const good = saju.days.filter((x) => Number(x.date.slice(5, 7)) === m.month && Number(x.date.slice(0, 4)) === m.year && dayScore(x) >= 3);
  if (good.length) rows.push({ k: "좋은 날", v: good.slice(0, 3).map(dayLabel).join(", ") });
  rows.push({ k: "할 일", v: d.todo });
  return { label: m.label, badge: stars(monthScore(saju, m)), title: d.theme, rows };
}

/** 사주와 관상에서 '같이' 높게 나온 테마만 고른다 */
export function findCommon(saju: SajuConsensus, features: FeatureScores | null, readings: FeatureReading[]): CommonTheme[] {
  const s = sajuThemes(saju);
  const f = features ? faceThemes(features) : null;
  const obs = (part: string) => readings.find((r) => r.part === part)?.observation;

  const rows = THEME_KEYS.map((k) => {
    const faceScore = f ? f[k] : s.score[k];
    const feats = features
      ? THEME_FEATURES[k].filter((x) => features[x] >= 0.55).map((x) => obs(FEATURE_PART[x]) ?? FEATURE_PART[x])
      : [];
    return {
      key: k,
      label: THEMES[k].label,
      saju: s.score[k],
      face: faceScore,
      sajuReason: s.reasons[k].length ? s.reasons[k].slice(0, 2).join(", ") : "원국 전반에 고르게 깔림",
      faceReason: feats.length ? feats.slice(0, 2).join(", ") : "얼굴 전체의 균형에서 드러남",
      strong: s.score[k] >= 0.55 && faceScore >= 0.55,
    } satisfies CommonTheme;
  }).sort((a, b) => Math.min(b.saju, b.face) - Math.min(a.saju, a.face) || b.saju + b.face - (a.saju + a.face));

  const strong = rows.filter((r) => r.strong);
  return strong.length >= 3 ? strong.slice(0, 4) : rows.slice(0, 3);
}

const josa = (word: string, withBatchim: string, without: string) => {
  const c = word.charCodeAt(word.length - 1);
  if (c < 0xac00 || c > 0xd7a3) return word + without;
  return word + ((c - 0xac00) % 28 ? withBatchim : without);
};

export function composeReading(saju: SajuConsensus, common: CommonTheme[], hasFace: boolean, gender: "남" | "여"): Reading {
  const top = common[0];
  const both = hasFace ? "사주와 관상이 동시에" : "사주가";
  const labels = common.map((c) => THEMES[c.key].short);

  const fe = saju.fiveElements;
  const maxN = Math.max(...ELEMENTS.map((e) => fe[e]));
  const strongEls = ELEMENTS.filter((e) => fe[e] >= 3 && fe[e] === maxN);
  const missing = ELEMENTS.filter((e) => fe[e] === 0);

  const sections: Section[] = [];

  sections.push({
    id: "personality",
    eyebrow: "01",
    title: "성격 · 강점",
    body: [
      DAY_MASTER[saju.dayMaster.stem],
      ...common.slice(0, 3).map((c) => `${THEMES[c.key].trait}${hasFace && c.faceReason !== "얼굴 전체의 균형에서 드러남" ? ` 관상에서도 ${c.faceReason}에 이 기질이 보여요.` : ""}`),
    ],
  });

  const fewEls = ELEMENTS.filter((e) => fe[e] <= 1 && !strongEls.includes(e));
  const elBody: string[] = [
    `타고난 다섯 기운은 ${ELEMENTS.map((e) => `${ELEMENT_TRAIT[e].name} ${fe[e]}`).join(", ")}입니다.`,
  ];
  for (const e of strongEls.length ? strongEls : [ELEMENTS.reduce((a, b) => (fe[b] > fe[a] ? b : a))]) elBody.push(ELEMENT_TRAIT[e].many);
  for (const e of fewEls.slice(0, 2)) elBody.push(ELEMENT_TRAIT[e].few);
  if (saju.yongsin.length)
    elBody.push(`그래서 나를 가장 잘 돕는 기운은 ${saju.yongsin.map((e) => ELEMENT_TRAIT[e].name).reduce((a, n) => `${a}${(a.charCodeAt(a.length - 1) - 0xac00) % 28 ? "과" : "와"} ${n}`)}입니다. 아래 행운 포인트에 이 기운을 채우는 방법을 정리했습니다.`);
  sections.push({ id: "elements", eyebrow: "02", title: "타고난 기운", body: elBody });

  const wealthCount = (saju.tenGodCounts["편재"] ?? 0) + (saju.tenGodCounts["정재"] ?? 0);
  const moneyYear = saju.years.find((y) => ["편재", "정재", "식신"].includes(y.tenGod));
  sections.push({
    id: "career",
    eyebrow: "02",
    title: "재물 · 직업",
    body: [
      THEMES[top.key].career,
      common[1] ? THEMES[common[1].key].career : "",
      wealthCount >= 2
        ? "사주에 재물의 별이 뚜렷해 돈을 다루는 감각이 좋습니다. 수입원을 둘 이상으로 나누면 재물이 더 안정됩니다."
        : wealthCount === 1
          ? "재물의 별이 적당히 자리 잡고 있어 꾸준히 쌓는 방식이 가장 잘 맞습니다."
          : "사주에 재물의 별이 드러나지 않아 큰돈을 쫓기보다 실력과 이름값을 먼저 키우면 재물이 따라오는 구조입니다.",
      WORK_STYLE[saju.strength],
      moneyYear
        ? `재물 흐름이 가장 좋은 해는 ${moneyYear.year}년입니다. 이 해에 수입원을 넓히거나 몸값을 올리는 시도를 해 보세요.`
        : "앞으로 3년은 큰돈보다 실력을 쌓는 시기입니다. 지금 쌓은 것이 다음 10년의 재물이 됩니다.",
      common[2] ? THEMES[common[2].key].career : "",
    ].filter(Boolean),
  });

  const spouseStar = gender === "남" ? ["편재", "정재"] : ["편관", "정관"];
  const spouseCount = spouseStar.reduce((a, g) => a + (saju.tenGodCounts[g] ?? 0), 0);
  const loveYear = saju.years.find((y) => spouseStar.includes(y.tenGod) || spouseStar.includes(y.branchTenGod));
  const matchEls = saju.yongsin.length ? saju.yongsin : [ELEMENTS.find((e) => fe[e] === 0) ?? "토"];
  sections.push({
    id: "love",
    eyebrow: "03",
    title: "연애 · 인간관계",
    body: [
      THEMES[top.key].love,
      common.some((c) => c.key === "sociability")
        ? "사람을 통해 운이 들어오는 구조입니다. 오래된 인연을 소중히 하세요."
        : "넓은 관계보다 깊은 소수의 관계에서 힘을 얻는 편입니다.",
      spouseCount >= 2
        ? "배우자 자리의 기운이 여럿 보여 인연의 기회가 많습니다. 선택의 기준을 분명히 하세요."
        : spouseCount === 1
          ? "인연의 별이 하나 또렷하게 자리 잡고 있어, 한 사람과 깊이 가는 연애가 잘 맞습니다."
          : "인연은 서두르지 않을 때 찾아옵니다. 일과 생활이 안정될 때 좋은 사람이 나타나는 흐름입니다.",
      LOVE_STYLE[saju.dayMaster.element],
      `잘 맞는 사람은 ${matchEls.map((e) => ELEMENT_TRAIT[e as Element].person).join(", 또는 ")}입니다. 나에게 부족한 기운을 채워 주는 사람이라 함께 있으면 편안합니다.`,
      loveYear ? `인연의 기운이 가장 강한 해는 ${loveYear.year}년입니다. 이 해의 만남은 오래갈 가능성이 큽니다.` : "",
    ].filter(Boolean),
  });

  const healthBody: string[] = [];
  if (strongEls.length) healthBody.push(`${strongEls.join("·")} 기운이 강해 ${strongEls.map((e) => HEALTH[e]).join(", ")} 쪽에 무리가 가지 않도록 리듬을 조절하세요.`);
  if (missing.length) healthBody.push(`${missing.join("·")} 기운이 비어 있어 ${missing.map((e) => HEALTH[e]).join(", ")} 관리가 평소 포인트입니다.`);
  if (!healthBody.length) healthBody.push("오행이 비교적 고르게 분포해 큰 약점은 드러나지 않습니다. 생활 리듬만 지키면 건강운이 무난합니다.");
  if (saju.yongsin.length) healthBody.push(`평소 ${saju.yongsin.map((e) => LUCK[e].thing).join(", ")} 같은 습관이 몸의 균형을 잡아 줍니다.`);
  healthBody.push(
    saju.strength === "strong"
      ? "에너지가 넘치는 만큼 과로를 과로로 느끼지 못할 수 있습니다. 쉬는 날을 달력에 먼저 적어 두세요."
      : "쉽게 지치는 시기가 오면 무리해서 버티기보다 일찍 쉬는 쪽이 길게 갑니다.",
  );
  healthBody.push("건강 내용은 오락용 참고이며, 몸에 이상이 있다면 반드시 의료 전문가와 상담하세요.");
  sections.push({ id: "health", eyebrow: "04", title: "건강", body: healthBody });

  if (saju.daeunList.length) {
    const life = saju.daeunList
      .filter((d) => d.startAge <= saju.age + 30)
      .map((d) => `${d.startAge}~${d.startAge + 9}세${d.current ? " (지금)" : ""} — ${DAEUN_LONG[d.stemTenGod] ?? "흐름이 바뀌는 시기입니다."}`);
    sections.push({ id: "life", eyebrow: "", title: "인생의 큰 흐름", body: ["사주는 10년마다 큰 흐름이 바뀝니다. 지금까지와 앞으로 30년의 흐름입니다.", ...life] });
  }

  if (saju.months.length) {
    sections.push(
      withItems(
        "months",
        "앞으로 12개월",
        "이번 달부터 한 달씩 나눈 흐름입니다. 각 달은 절기에 따라 그달 초순(4~8일경)부터 시작하고, 별이 많을수록 순조로운 달입니다.",
        saju.months.map((m) => monthItem(saju, m)),
      ),
    );
  }

  if (saju.yongsin.length) {
    const ys = saju.yongsin;
    const L = ys.map((e) => LUCK[e]);
    const M = ys.map((e) => LUCK_MORE[e]);
    const names = ys.map((e) => ELEMENT_TRAIT[e].name).join("·");
    const avoid = ELEMENTS.filter((e) => ys.some((y) => CONTROLS[e] === y) && !ys.includes(e));
    const luckyDays = [...saju.days].filter((d) => !d.clash).sort((a, b) => dayScore(b) - dayScore(a)).slice(0, 3).sort((a, b) => a.date.localeCompare(b.date));
    const items: SectionItem[] = [
      { label: "행운의 색", title: L.map((l) => l.color).join(", "), rows: [{ k: "이렇게", v: M.map((m) => m.colorUse).join(", ") }] },
      ...(avoid.length ? [{ label: "줄이면 좋은 색", title: avoid.map((e) => LUCK[e].color).join(", "), rows: [{ k: "이유", v: "나를 돕는 기운을 누르는 색입니다. 중요한 날에는 피하세요" }] }] : []),
      { label: "행운의 방향", title: L.map((l) => l.direction).join(", "), rows: [{ k: "이렇게", v: M.map((m) => m.directionUse).join(" / ") }] },
      { label: "행운의 숫자", title: L.map((l) => l.number).join(", "), rows: [{ k: "이렇게", v: "중요한 약속 날짜, 좌석·층수, 비밀번호의 끝자리로 써 보세요" }] },
      { label: "행운의 요일·시간", title: M.map((m) => m.day).join(", "), rows: [{ k: "시간대", v: M.map((m) => m.time).join(", ") }, { k: "이렇게", v: "면접·계약·고백처럼 중요한 일은 이 요일과 시간에 잡아 보세요" }] },
      ...(luckyDays.length ? [{ label: "가까운 행운의 날", title: luckyDays.map(dayLabel).join(", "), rows: [{ k: "이렇게", v: "앞으로 2주 중 기운이 가장 좋은 날입니다. 미뤄 둔 일을 이날 처리하세요" }] }] : []),
      { label: "기운이 살아나는 계절", title: L.map((l) => l.season).join(", "), rows: [{ k: "이렇게", v: "이 계절에는 새로운 시작을, 다른 계절에는 준비와 정리를 하세요" }] },
      { label: "행운의 음식", title: M.map((m) => m.food).join(", "), rows: [] },
      { label: "행운의 장소", title: M.map((m) => m.place).join(", "), rows: [{ k: "이렇게", v: "마음이 복잡할 때 이런 곳에 가면 기운이 채워집니다" }] },
      { label: "추천 취미·운동", title: M.map((m) => m.hobby).join(", "), rows: [] },
      { label: "잘 맞는 띠", title: M.map((m) => m.zodiac).join(", "), rows: [{ k: "이렇게", v: "동업·연애·팀 구성에서 힘이 되는 인연입니다" }] },
      { label: "곁에 두면 좋은 것", title: [...M.map((m) => m.item), ...L.map((l) => l.thing)].join(", "), rows: [] },
    ];
    sections.push(withItems("luck", "행운 포인트", `나를 돕는 기운은 ${names}입니다. 생활 속에서 이 기운을 채우는 방법을 모았습니다.`, items));
  }

  const caution: string[] = [];
  if (saju.relations.length)
    caution.push("타고난 기운 중에 서로 부딪치는 것이 있어 이사·이직·관계의 변동이 잦을 수 있습니다. 큰 결정은 한 번 더 점검하세요.");
  const shadows: Partial<Record<ThemeKey, string>> = {
    leadership: "추진력이 강한 만큼 독단으로 보이지 않게 주변 의견을 한 번 더 들으세요.",
    wealth: "돈 냄새를 잘 맡는 만큼 한 번에 크게 거는 투자는 피하세요.",
    expression: "말이 무기인 만큼 말이 화살이 되지 않게 감정적인 순간에는 말을 아끼세요.",
    sensitivity: "예민함이 피로로 쌓이기 쉽습니다. 혼자 정리하는 시간을 꼭 확보하세요.",
    stability: "신중함이 지나치면 기회를 놓칩니다. 70% 확신이면 움직여 보세요.",
    intellect: "생각이 많아 실행이 늦어질 수 있습니다. 작게라도 먼저 시작하세요.",
    sociability: "사람에게 쓰는 에너지와 돈이 새지 않도록 경계를 정하세요.",
    willpower: "고집이 기회를 막지 않도록, 방향이 틀렸다면 빠르게 수정하는 용기도 필요합니다.",
    independence: "혼자 다 짊어지려 하지 마세요. 도움을 청하는 것도 실력입니다.",
  };
  for (const c of common.slice(0, 2)) if (shadows[c.key]) caution.push(shadows[c.key]!);
  const hardYear = saju.years.find((y) => ["편관", "겁재", "상관"].includes(y.tenGod));
  if (hardYear) caution.push(`${hardYear.year}년은 무리하기 쉬운 해입니다. 계약서·건강검진·인간관계를 꼼꼼히 챙기세요.`);
  sections.push({ id: "caution", eyebrow: "", title: "주의사항", body: caution });
  sections.unshift(...timeSections(saju));
  sections.forEach((sec, i) => (sec.eyebrow = String(i + 1).padStart(2, "0")));

  const advice: string[] = [];
  if (saju.yongsin.length) {
    advice.push(`나를 돕는 기운은 ${saju.yongsin.join("·")}입니다. ${saju.yongsin.map((e) => BOOST[e]).join(" / ")}이 운을 보탭니다.`);
  }
  advice.push(`당신의 무기는 ${labels.join(", ")}입니다. 이 강점을 숨기지 말고 드러내세요.`);
  advice.push(WORK_STYLE[saju.strength].split(". ")[1] ? `${WORK_STYLE[saju.strength].split(". ")[1]}` : "좋은 사람을 곁에 두세요.");
  advice.push("잘 풀리는 해에는 씨앗을 뿌리고, 조심할 해에는 뿌리를 다지세요. 운은 준비된 사람에게 옵니다.");
  advice.push("운은 흐름일 뿐, 결정은 당신이 합니다. 좋은 시기엔 과감하게, 조심할 시기엔 차분하게.");

  return {
    headline: HEADLINE[top.key],
    summary: `${both} 말하는 당신의 핵심은 ‘${labels.join(" · ")}’입니다. ${josa(
      THEMES[top.key].label,
      "이",
      "가",
    )} 가장 뚜렷하게 겹쳤습니다.`,
    sections,
    advice,
    source: "rules",
  };
}
