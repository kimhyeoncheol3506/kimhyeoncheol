// 화면에 보이는 한글 이름과 색상. 문구를 바꾸고 싶으면 여기만 고치세요.
import type {
  AccountRole,
  ErrorStatus,
  Integration,
  MissionStatus,
  OrderStatus,
  Permission,
  Priority,
  Severity,
  StaffStatus,
} from "./types";

type Label = { text: string; tone: Tone };
export type Tone = "green" | "blue" | "amber" | "red" | "gray";

export const staffStatus: Record<StaffStatus, Label> = {
  available: { text: "사용 가능", tone: "green" },
  working: { text: "작업 중", tone: "blue" },
  review: { text: "검수 중", tone: "amber" },
  needs_connection: { text: "연결 필요", tone: "red" },
  paused: { text: "중지", tone: "gray" },
};

export const missionStatus: Record<MissionStatus, Label> = {
  todo: { text: "대기", tone: "gray" },
  doing: { text: "진행 중", tone: "blue" },
  review: { text: "검수 중", tone: "amber" },
  done: { text: "완료", tone: "green" },
};

export const priority: Record<Priority, Label> = {
  low: { text: "낮음", tone: "gray" },
  normal: { text: "보통", tone: "blue" },
  high: { text: "긴급", tone: "red" },
};

export const errorStatus: Record<ErrorStatus, Label> = {
  open: { text: "접수", tone: "red" },
  in_progress: { text: "처리 중", tone: "amber" },
  resolved: { text: "해결", tone: "green" },
};

export const severity: Record<Severity, Label> = {
  low: { text: "낮음", tone: "gray" },
  medium: { text: "보통", tone: "amber" },
  high: { text: "심각", tone: "red" },
};

export const orderStatus: Record<OrderStatus, Label> = {
  paid: { text: "결제 완료", tone: "blue" },
  in_production: { text: "제작 중", tone: "amber" },
  delivered: { text: "납품 완료", tone: "green" },
  refunded: { text: "환불", tone: "gray" },
};

export const integrationStatus: Record<Integration["status"], Label> = {
  connected: { text: "연결됨", tone: "green" },
  needs_connection: { text: "연결 필요", tone: "red" },
  error: { text: "오류", tone: "red" },
};

export const accountRole: Record<AccountRole, Label> = {
  owner: { text: "대표", tone: "green" },
  manager: { text: "관리자", tone: "blue" },
  viewer: { text: "열람", tone: "gray" },
};

export const permission: Record<Permission, string> = {
  read_files: "자료 열람",
  write_files: "문서 작성",
  send_email: "메일 발송",
  post_content: "콘텐츠 게시",
  access_finance: "재무 접근",
  external_api: "외부 API",
  schedule: "일정 관리",
};

export const allPermissions = Object.keys(permission) as Permission[];
