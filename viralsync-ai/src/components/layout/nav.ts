import type { Permission } from "@/lib/auth/permissions";

export interface NavItem {
  href: string;
  label: string;
  icon: string;
  permission?: Permission;
}

export const NAV: NavItem[] = [
  { href: "/dashboard", label: "대시보드", icon: "📊" },
  { href: "/inquiries", label: "문의 접수함", icon: "📥", permission: "inquiry:manage" },
  { href: "/clients", label: "고객관리", icon: "🏢" },
  { href: "/campaigns", label: "광고 의뢰·캠페인", icon: "📝" },
  { href: "/opportunities", label: "홍보 기회 탐색", icon: "🔎" },
  { href: "/content", label: "AI 문구 생성", icon: "✍️" },
  { href: "/approvals", label: "승인 관리", icon: "✅" },
  { href: "/executions", label: "실행 관리", icon: "🚀" },
  { href: "/fulfillment", label: "매체 집행 작업", icon: "🧾" },
  { href: "/services", label: "서비스 상품", icon: "🏷️", permission: "inquiry:manage" },
  { href: "/platforms", label: "SNS 통합 관리", icon: "🔌" },
  { href: "/reports", label: "실적·보고서", icon: "📈" },
  { href: "/policies", label: "정책 관리 센터", icon: "📜" },
  { href: "/settings/users", label: "직원·권한", icon: "👥", permission: "user:manage" },
  { href: "/audit", label: "감사 로그", icon: "🗂️", permission: "audit:read" },
];
