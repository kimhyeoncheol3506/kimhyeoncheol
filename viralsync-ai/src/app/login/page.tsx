import { redirect } from "next/navigation";
import { brand } from "@/config/brand";
import { prisma } from "@/lib/db";
import { getCtx } from "@/lib/auth/current";
import { ROLE_LABEL } from "@/lib/labels";
import { demoLogin } from "@/app/actions/auth";
import { Alert } from "@/components/ui/misc";
import { LoginForm } from "./login-form";
import { demoLoginAllowed } from "@/lib/auth/demo";

export const metadata = { title: "로그인" };
export const dynamic = "force-dynamic";

const ERRORS: Record<string, string> = {
  demo_disabled: "데모 원클릭 로그인은 이 PC(localhost)에서만 사용할 수 있습니다. 외부 주소에서는 이메일·비밀번호로 로그인하세요.",
  demo_missing: "데모 계정을 찾을 수 없습니다. `npm run db:seed` 로 데모 데이터를 생성하세요.",
};

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  if (await getCtx()) redirect("/dashboard");
  const { error } = await searchParams;
  const demoMode = await demoLoginAllowed();
  let demoUsers: { email: string; name: string; role: keyof typeof ROLE_LABEL; organization: { name: string } }[] = [];
  let dbError = false;
  if (demoMode) {
    try {
      demoUsers = await prisma.user.findMany({
        where: { isDemo: true, active: true },
        select: { email: true, name: true, role: true, organization: { select: { name: true } } },
        orderBy: [{ organization: { createdAt: "asc" } }, { createdAt: "asc" }],
      });
    } catch {
      dbError = true;
    }
  }
  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-50 via-white to-slate-100 px-4 py-10">
      <div className="w-full max-w-4xl">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 text-xl font-bold text-white">V</div>
          <h1 className="text-2xl font-bold text-slate-900">{brand.name}</h1>
          <p className="mt-1 text-sm text-slate-500">{brand.tagline}</p>
        </div>
        {error && ERRORS[error] && (
          <div className="mb-4">
            <Alert tone="error">{ERRORS[error]}</Alert>
          </div>
        )}
        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold">이메일 로그인</h2>
            <LoginForm />
          </section>
          {demoMode && (
            <section className="rounded-2xl border border-violet-200 bg-white p-6 shadow-sm" aria-labelledby="demo-title">
              <h2 id="demo-title" className="text-base font-semibold">데모 계정으로 체험</h2>
              <p className="mb-4 mt-1 text-xs text-slate-500">
                모든 데모 계정·고객·SNS 게시물은 가상 데이터이며 실제 사용자나 실제 SNS 계정이 아닙니다. 외부 SNS 에는 아무것도 게시되지 않습니다.
              </p>
              {dbError && <Alert tone="error">데이터베이스에 연결할 수 없습니다. DATABASE_URL 과 PostgreSQL 실행 상태를 확인하세요.</Alert>}
              {!dbError && demoUsers.length === 0 && <Alert tone="warn">데모 계정이 없습니다. `npm run db:seed` 를 실행하세요.</Alert>}
              <ul className="space-y-2">
                {demoUsers.map((u) => (
                  <li key={u.email}>
                    <form action={demoLogin}>
                      <input type="hidden" name="email" value={u.email} />
                      <button
                        type="submit"
                        className="flex w-full items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-left text-sm hover:border-brand-500 hover:bg-brand-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                      >
                        <span>
                          <span className="block font-medium text-slate-800">{u.name}</span>
                          <span className="block text-xs text-slate-500">{u.organization.name}</span>
                        </span>
                        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{ROLE_LABEL[u.role]}</span>
                      </button>
                    </form>
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-xs text-slate-400">데모 계정 비밀번호: demo1234!</p>
            </section>
          )}
        </div>
      </div>
    </main>
  );
}
