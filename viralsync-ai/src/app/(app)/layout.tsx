import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { prisma } from "@/lib/db";
import { ROLE_LABEL } from "@/lib/labels";
import { NAV } from "@/components/layout/nav";
import { Sidebar } from "@/components/layout/sidebar";
import { logout } from "@/app/actions/auth";
import { campaignWhere } from "@/lib/auth/context";
import { ToastProvider } from "@/components/ui/toast";

export const dynamic = "force-dynamic";

// 참고: 이 라우트 그룹에는 loading.tsx 를 두지 않는다. Next 15.5 에서 그룹 단위 loading 경계가 있으면
// 스트리밍되는 상세 페이지로의 클라이언트 이동이 간헐적으로 멈추는 현상을 재현·확인했다 (E2E 로 검증).
// 이동 중 표시는 사이드바 링크의 useLinkStatus 로, 제출 중 표시는 SubmitButton 으로 처리한다.

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const ctx = await requireCtx();
  const [org, pending] = await Promise.all([
    prisma.organization.findUnique({ where: { id: ctx.organizationId }, select: { name: true, isDemo: true } }),
    can(ctx.role, "approval:decide")
      ? prisma.generatedContent.count({ where: { organizationId: ctx.organizationId, status: "PENDING_REVIEW", campaign: campaignWhere(ctx) } })
      : Promise.resolve(0),
  ]);
  const items = NAV.filter((i) => !i.permission || can(ctx.role, i.permission));
  return (
    <ToastProvider>
    <div className="min-h-screen">
      <Sidebar items={items} pendingReview={pending} />
      <div className="lg:pl-60">
        <header className="no-print sticky top-0 z-20 flex flex-wrap items-center gap-3 border-b border-slate-200 bg-white/90 px-4 py-2.5 pl-14 backdrop-blur lg:pl-6">
          <form action="/search" className="min-w-0 flex-1" role="search">
            <label htmlFor="global-search" className="sr-only">전체 검색</label>
            <input id="global-search" name="q" type="search" placeholder="고객·캠페인·게시물·문구 검색" className="input max-w-md" />
          </form>
          {org?.isDemo && (
            <span className="hidden rounded-full bg-violet-100 px-2.5 py-1 text-xs font-medium text-violet-700 sm:inline" title="외부 SNS 에 게시하지 않는 모의 실행 모드">
              데모 · 모의 실행 모드
            </span>
          )}
          <div className="text-right text-xs leading-tight">
            <p className="font-semibold text-slate-800">{ctx.name}</p>
            <p className="text-slate-500">
              {ROLE_LABEL[ctx.role]} · {org?.name}
            </p>
          </div>
          <form action={logout}>
            <button type="submit" className="rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs text-slate-600 hover:bg-slate-50">
              로그아웃
            </button>
          </form>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</main>
      </div>
    </div>
    </ToastProvider>
  );
}
