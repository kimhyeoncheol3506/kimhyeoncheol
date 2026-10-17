// AIMAX OS에서 다루는 모든 데이터의 모양(타입)을 한곳에 모아 둡니다.
// 새 항목을 추가할 때는 여기부터 고치면 됩니다.

export type StaffStatus = "available" | "working" | "review" | "needs_connection" | "paused";

export type Permission =
  | "read_files"
  | "write_files"
  | "send_email"
  | "post_content"
  | "access_finance"
  | "external_api"
  | "schedule";

export interface Staff {
  id: string;
  name: string;
  role: string; // 예: 블로그 담당
  department: string;
  avatar: string; // 이모지
  summary: string;
  personality: string[]; // 업무 성향
  resume: { career: string[]; skills: string[]; strengths: string };
  runtime: { engine: string; tools: string[]; schedule: string }; // 실행 환경
  permissions: Permission[];
  status: StaffStatus;
  joinedAt: string;
}

export type MissionStatus = "todo" | "doing" | "review" | "done";
export type Priority = "low" | "normal" | "high";

export interface Mission {
  id: string;
  staffId: string;
  title: string;
  detail: string;
  priority: Priority;
  status: MissionStatus;
  dueDate: string;
  createdAt: string;
  feedback: string; // CEO 검수 의견
}

export type ErrorStatus = "open" | "in_progress" | "resolved";
export type Severity = "low" | "medium" | "high";

export interface ErrorReport {
  id: string;
  title: string;
  message: string;
  source: "auto" | "manual"; // auto: 화면에서 자동 감지, manual: 직접 보고
  page: string;
  staffId?: string;
  severity: Severity;
  status: ErrorStatus;
  createdAt: string;
  stack?: string;
  feedback: string; // CEO 메모 / 처리 내용
}

export type OrderStatus = "paid" | "in_production" | "delivered" | "refunded";

export interface Order {
  id: string;
  channel: "cafe24" | "direct";
  buyerId: string;
  product: string;
  amount: number;
  status: OrderStatus;
  orderedAt: string;
}

export interface Buyer {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  registeredAt: string;
}

export type AccountRole = "owner" | "manager" | "viewer";

export interface Account {
  id: string;
  name: string;
  email: string;
  role: AccountRole;
  active: boolean;
  createdAt: string;
}

export interface Integration {
  id: string;
  name: string;
  description: string;
  status: "connected" | "needs_connection" | "error";
  lastSync?: string;
}

export interface Collections {
  staff: Staff[];
  missions: Mission[];
  errors: ErrorReport[];
  orders: Order[];
  buyers: Buyer[];
  accounts: Account[];
  integrations: Integration[];
}
