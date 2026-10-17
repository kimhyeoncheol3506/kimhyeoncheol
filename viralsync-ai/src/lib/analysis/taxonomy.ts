/**
 * 광고 의뢰·게시물 분류 체계. 키워드 사전 기반(규칙 엔진)이며, 키워드는 소문자로 비교한다.
 * sensitive: 광고 정책상 추가 검토가 필요한 분야 (정책 위험도 가산)
 */
export interface Subcategory {
  name: string;
  keywords: string[];
}

export interface Category {
  name: string;
  sensitive?: "HIGH" | "MEDIUM";
  subcategories: Subcategory[];
}

export const TAXONOMY: Category[] = [
  {
    name: "교육",
    subcategories: [
      { name: "어학", keywords: ["영어", "토익", "토플", "회화", "일본어", "중국어", "어학"] },
      { name: "입시·학습", keywords: ["수능", "입시", "공부", "학습", "과외", "학원", "문제집", "수학"] },
      { name: "자격증·직무", keywords: ["자격증", "직무", "취업", "코딩교육", "부트캠프", "강의", "인강", "클래스"] },
      { name: "육아·유아교육", keywords: ["유아", "육아", "초등", "아이 교육", "교구"] },
    ],
  },
  {
    name: "엔터테인먼트",
    subcategories: [
      { name: "음악", keywords: ["음악", "노래", "앨범", "뮤직비디오", "아이돌", "k-pop", "케이팝", "공연"] },
      { name: "영화·드라마", keywords: ["영화", "드라마", "ott", "넷플릭스", "시리즈", "예고편"] },
      { name: "예능·크리에이터", keywords: ["예능", "브이로그", "vlog", "챌린지", "밈", "웃긴", "크리에이터"] },
      { name: "웹툰·웹소설", keywords: ["웹툰", "웹소설", "만화", "애니"] },
    ],
  },
  {
    name: "시사",
    sensitive: "MEDIUM",
    subcategories: [
      { name: "사회 이슈", keywords: ["사회", "이슈", "뉴스", "사건", "논란"] },
      { name: "국제", keywords: ["국제", "해외 뉴스", "외교", "세계"] },
      { name: "환경", keywords: ["환경", "기후", "탄소", "친환경", "esg"] },
    ],
  },
  {
    name: "정치",
    sensitive: "HIGH",
    subcategories: [
      { name: "선거·정당", keywords: ["선거", "정당", "후보", "투표", "공약", "국회의원"] },
      { name: "정책", keywords: ["정책", "법안", "정부", "행정"] },
    ],
  },
  {
    name: "역사",
    subcategories: [
      { name: "한국사", keywords: ["한국사", "조선", "고려", "삼국", "독립운동"] },
      { name: "세계사", keywords: ["세계사", "로마", "중세", "근현대사", "전쟁사"] },
      { name: "문화유산", keywords: ["문화유산", "박물관", "유적", "궁궐"] },
    ],
  },
  {
    name: "경제·금융",
    sensitive: "HIGH",
    subcategories: [
      { name: "투자·주식", keywords: ["주식", "투자", "etf", "코인", "가상자산", "비트코인", "펀드", "수익률"] },
      { name: "재테크·절약", keywords: ["재테크", "적금", "예금", "절약", "가계부", "짠테크"] },
      { name: "대출·보험", keywords: ["대출", "보험", "신용", "카드", "금리"] },
      { name: "부동산", keywords: ["부동산", "아파트", "청약", "전세", "월세"] },
    ],
  },
  {
    name: "IT·AI",
    subcategories: [
      { name: "인공지능", keywords: ["ai", "인공지능", "챗봇", "gpt", "llm", "생성형", "머신러닝"] },
      { name: "개발·프로그래밍", keywords: ["개발", "프로그래밍", "코딩", "api", "개발자", "깃허브"] },
      { name: "디지털 기기", keywords: ["스마트폰", "노트북", "태블릿", "갤럭시", "아이폰", "가젯", "리뷰 기기"] },
      { name: "SaaS·업무도구", keywords: ["saas", "협업", "생산성", "업무 자동화", "노션", "툴"] },
    ],
  },
  {
    name: "여행·맛집",
    subcategories: [
      { name: "국내 여행", keywords: ["제주", "부산", "강릉", "국내여행", "국내 여행", "캠핑", "펜션"] },
      { name: "해외 여행", keywords: ["해외여행", "해외 여행", "일본 여행", "유럽", "항공권", "호텔"] },
      { name: "맛집·카페", keywords: ["맛집", "카페", "디저트", "레스토랑", "음식점", "브런치", "베이커리"] },
      { name: "레시피·요리", keywords: ["레시피", "요리", "집밥", "밀키트"] },
    ],
  },
  {
    name: "뷰티·패션",
    subcategories: [
      { name: "스킨케어", keywords: ["스킨케어", "화장품", "선크림", "세럼", "토너", "피부", "보습"] },
      { name: "메이크업", keywords: ["메이크업", "립", "쿠션", "파운데이션", "아이섀도"] },
      { name: "패션·잡화", keywords: ["패션", "코디", "옷", "신발", "가방", "룩북", "ootd"] },
      { name: "헤어", keywords: ["헤어", "샴푸", "염색", "펌"] },
    ],
  },
  {
    name: "건강·생활",
    sensitive: "MEDIUM",
    subcategories: [
      { name: "운동·피트니스", keywords: ["운동", "헬스", "필라테스", "요가", "홈트", "러닝", "다이어트"] },
      { name: "건강기능식품", keywords: ["영양제", "건강기능식품", "비타민", "유산균", "단백질", "보충제"] },
      { name: "생활용품·살림", keywords: ["생활용품", "살림", "청소", "수납", "인테리어", "가전"] },
      { name: "반려동물", keywords: ["반려동물", "강아지", "고양이", "펫", "사료"] },
    ],
  },
  {
    name: "게임",
    subcategories: [
      { name: "모바일 게임", keywords: ["모바일 게임", "모바일게임", "rpg", "가챠", "사전예약"] },
      { name: "PC·콘솔", keywords: ["pc게임", "스팀", "콘솔", "닌텐도", "플스", "플레이스테이션"] },
      { name: "e스포츠·스트리밍", keywords: ["e스포츠", "롤", "발로란트", "게임 방송", "스트리머"] },
    ],
  },
  {
    name: "앱·소프트웨어",
    subcategories: [
      { name: "생산성 앱", keywords: ["앱", "어플", "생산성", "일정 관리", "메모", "투두"] },
      { name: "커뮤니티·소셜 앱", keywords: ["커뮤니티", "소셜", "채팅", "매칭"] },
      { name: "핀테크 앱", keywords: ["간편결제", "송금", "핀테크", "가계부 앱"] },
      { name: "교육·학습 앱", keywords: ["학습 앱", "단어 앱", "공부 앱"] },
    ],
  },
  {
    name: "쇼핑·상품",
    subcategories: [
      { name: "식품", keywords: ["식품", "간식", "음료", "커피", "원두", "과일", "밀키트"] },
      { name: "가전·디지털 상품", keywords: ["가전", "이어폰", "충전기", "스피커", "키보드"] },
      { name: "리빙·인테리어", keywords: ["가구", "조명", "침구", "인테리어 소품"] },
      { name: "커머스 이벤트", keywords: ["할인", "특가", "쿠폰", "이벤트", "구매", "쇼핑", "스토어", "라이브커머스"] },
    ],
  },
  {
    name: "기타",
    subcategories: [{ name: "일반", keywords: [] }],
  },
];

export const CATEGORY_NAMES = TAXONOMY.map((c) => c.name);

/** 과장·단정·허위 우려 표현 (정책 위험도 산정용) */
export const RISKY_PHRASES = [
  "100%",
  "무조건",
  "완치",
  "보장",
  "최고",
  "1위",
  "부작용 없",
  "원금 보장",
  "수익 보장",
  "확정 수익",
  "기적",
  "즉시 효과",
  "단기간",
  "공짜",
  "무료로 돈",
];
