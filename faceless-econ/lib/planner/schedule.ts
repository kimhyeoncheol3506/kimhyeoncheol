// 30일 출시 일정. priority: 필수(must) / 권장(should) / 선택(could)
// 일정이 밀리면 화면에서 '선택' → '권장' 순으로 축소해 게시일(22일차)을 지킨다.

export interface Task {
  id: string;
  dayStart: number;
  dayEnd: number;
  phase: string;
  title: string;
  done: string; // 완료 조건
  hours: number;
  priority: "must" | "should" | "could";
}

export const PHASES = [
  { range: "1~3일", name: "채널 분석과 주제 확정" },
  { range: "4~7일", name: "자료 조사 및 대본 작성" },
  { range: "8~14일", name: "내레이션, 차트, 장면 제작" },
  { range: "15~21일", name: "편집, 썸네일 제작, 검수" },
  { range: "22~30일", name: "게시, 성과 관측, 후속 영상 개선" },
];

export const TASKS: Task[] = [
  { id: "t01", dayStart: 1, dayEnd: 1, phase: PHASES[0].name, title: "YouTube API 키 발급·.env.local 설정, 첫 수집 실행", done: "'데이터 및 설정'에 실제 데이터 배지가 표시되고 수집 기록이 성공/부분 성공", hours: 1, priority: "must" },
  { id: "t02", dayStart: 1, dayEnd: 2, phase: PHASES[0].name, title: "상위 3개 채널 대표 영상 각 3개 시청·정밀 분석 입력", done: "9개 영상의 썸네일·도입부·시각 방식 항목이 '직접 확인'으로 저장", hours: 4, priority: "must" },
  { id: "t03", dayStart: 2, dayEnd: 3, phase: PHASES[0].name, title: "매일 같은 시각 재수집(스냅샷 누적)", done: "스냅샷 3회 이상 → 채널 내 상대 성과 지표 계산 시작", hours: 0.5, priority: "should" },
  { id: "t04", dayStart: 3, dayEnd: 3, phase: PHASES[0].name, title: "첫 영상 주제 확정 + 채널명·채널 아트 문구 결정", done: "주제 1개, 제목 후보 3개, 채널명 확정", hours: 2, priority: "must" },
  { id: "t05", dayStart: 4, dayEnd: 5, phase: PHASES[1].name, title: "공식 자료 확인: 기준금리·COFIX·법령 조항, 기준일 기록", done: "【확인 필요】 4칸이 모두 출처 URL·기준일과 함께 채워짐", hours: 3, priority: "must" },
  { id: "t06", dayStart: 5, dayEnd: 6, phase: PHASES[1].name, title: "대본 다듬기 (내 말투로 수정, 8~9분 분량)", done: "소리 내어 읽었을 때 8~9분, 문장마다 근거 출처 표시", hours: 4, priority: "must" },
  { id: "t07", dayStart: 7, dayEnd: 7, phase: PHASES[1].name, title: "사실 검증 체크 (수치·용어·권유 표현)", done: "체크리스트 통과: 수치 기준일, '보장/무조건' 표현 없음, 예시 표기", hours: 1.5, priority: "must" },
  { id: "t08", dayStart: 8, dayEnd: 9, phase: PHASES[2].name, title: "내레이션 녹음 또는 TTS 생성", done: "잡음 없는 음성 파일, 장면별로 분할", hours: 3, priority: "must" },
  { id: "t09", dayStart: 9, dayEnd: 11, phase: PHASES[2].name, title: "도식·차트 제작 (노선도, 수식, 타임라인, 계산표)", done: "장면 1~8의 핵심 그래픽 8장 이상, 출처·기준일 표기", hours: 6, priority: "must" },
  { id: "t10", dayStart: 11, dayEnd: 13, phase: PHASES[2].name, title: "간단한 모션(슬라이드 인·카운트업) 적용", done: "장면 전환 효과 적용된 클립", hours: 4, priority: "should" },
  { id: "t11", dayStart: 13, dayEnd: 14, phase: PHASES[2].name, title: "쇼츠 2개용 세로 그래픽 준비", done: "9:16 그래픽 세트", hours: 2, priority: "could" },
  { id: "t12", dayStart: 15, dayEnd: 17, phase: PHASES[3].name, title: "1차 편집 (내레이션 + 그래픽 + 자막)", done: "처음부터 끝까지 재생 가능한 1차 편집본", hours: 6, priority: "must" },
  { id: "t13", dayStart: 17, dayEnd: 18, phase: PHASES[3].name, title: "썸네일 3안 제작 및 선택", done: "모바일 크기에서 문구가 읽히는 썸네일 3안", hours: 2, priority: "must" },
  { id: "t14", dayStart: 18, dayEnd: 19, phase: PHASES[3].name, title: "배경음악·효과음·음량 정리", done: "내레이션 -14 LUFS 근처, 저작권 확인된 음원 목록 기록", hours: 2, priority: "should" },
  { id: "t15", dayStart: 19, dayEnd: 20, phase: PHASES[3].name, title: "검수: 지인 1~2명 시청 피드백 + 사실 재확인", done: "지적 사항 반영, 수치 기준일 재확인", hours: 2, priority: "should" },
  { id: "t16", dayStart: 21, dayEnd: 21, phase: PHASES[3].name, title: "설명란·타임라인·출처·고정 댓글 준비, 예약 업로드", done: "예약 게시 완료", hours: 1, priority: "must" },
  { id: "t17", dayStart: 22, dayEnd: 22, phase: PHASES[4].name, title: "게시 + 첫 24시간 지표 기록", done: "24시간 후 조회수·노출 클릭률·평균 시청 지속 시간 기록(YouTube 스튜디오)", hours: 1, priority: "must" },
  { id: "t18", dayStart: 23, dayEnd: 25, phase: PHASES[4].name, title: "쇼츠 2개 파생 게시", done: "쇼츠 2개 게시, 롱폼 링크 연결", hours: 3, priority: "could" },
  { id: "t19", dayStart: 25, dayEnd: 27, phase: PHASES[4].name, title: "72시간·7일 성과 리뷰, 시청 지속 그래프 이탈 구간 분석", done: "이탈 구간 3곳과 원인 가설 기록", hours: 2, priority: "must" },
  { id: "t20", dayStart: 27, dayEnd: 30, phase: PHASES[4].name, title: "두 번째 영상 주제 확정·대본 초안 (첫 영상 개선점 반영)", done: "다음 영상 대본 초안과 개선 체크리스트", hours: 5, priority: "should" },
];

export const PRIORITY_LABELS = { must: "필수", should: "권장", could: "선택" } as const;
