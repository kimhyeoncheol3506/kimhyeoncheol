import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { platformStatuses } from "@/lib/services/platforms";
import { INTEGRATION_STATUS_LABEL } from "@/lib/labels";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { DemoBadge } from "@/components/ui/badge";
import { IntegrationBadge } from "@/components/ui/status";
import { Alert } from "@/components/ui/misc";

export const metadata = { title: "SNS 통합 관리" };

export default async function PlatformsPage() {
  const ctx = await requireCtx();
  const rows = await platformStatuses(ctx);
  const showSecrets = can(ctx.role, "account:manage");
  return (
    <>
      <PageHeader title="SNS 통합 관리" description="플랫폼별 Adapter 와 연동 상태입니다. 공식 API 권한이 없는 기능은 지원한다고 표시하지 않습니다." />
      <div className="mb-6 space-y-3">
        <Alert tone="info" title="연동 상태 단계">
          {Object.values(INTEGRATION_STATUS_LABEL).join(" → ")}. 현재 MVP 는 모든 플랫폼의 실제 게시 호출이 구현되어 있지 않아 ‘4. 게시 가능’ 상태가 될 수 없으며, 모든 실행은 모의 실행으로 처리됩니다.
        </Alert>
        {!showSecrets && <Alert tone="warn">계정 인증정보 관리 권한이 없어 환경변수·토큰 정보는 표시되지 않습니다.</Alert>}
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {rows.map((p) => (
          <Card key={p.key}>
            <CardHeader title={p.name} action={<IntegrationBadge status={p.status} />} />
            <CardBody className="space-y-3 text-sm">
              <p className="text-xs text-slate-600">{p.apiNotes}</p>
              <dl className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <dt className="text-slate-500">최대 글자 수</dt>
                  <dd className="font-medium">{p.maxTextLength.toLocaleString()}자</dd>
                </div>
                <div>
                  <dt className="text-slate-500">일일 실행 한도 (자체)</dt>
                  <dd className="font-medium">{p.dailyLimit}건</dd>
                </div>
                <div>
                  <dt className="text-slate-500">실제 게시 호출</dt>
                  <dd className="font-medium">{p.livePublishImplemented ? "구현됨" : "미구현 (별도 단계)"}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">개발자 문서</dt>
                  <dd><a href={p.docsUrl} target="_blank" rel="noreferrer noopener" className="link break-all">공식 문서 ↗</a></dd>
                </div>
              </dl>
              {p.missingEnv && (
                <div className="text-xs">
                  <p className="text-slate-500">필요 환경변수 (서버 전용)</p>
                  {p.missingEnv.length === 0 ? (
                    <p className="text-emerald-700">모두 설정됨</p>
                  ) : (
                    <p className="text-rose-600">미설정: {p.missingEnv.join(", ")}</p>
                  )}
                </div>
              )}
              <div>
                <p className="mb-1 text-xs text-slate-500">연결 계정</p>
                {p.accounts.length === 0 ? (
                  <p className="text-xs text-slate-400">없음</p>
                ) : (
                  <ul className="space-y-1">
                    {p.accounts.map((a) => (
                      <li key={a.id} className="flex flex-wrap items-center gap-1.5 text-xs">
                        <span className="font-medium">{a.accountName}</span>
                        {a.isDemo && <DemoBadge />}
                        <IntegrationBadge status={a.status} />
                        {a.tokenHint && <code className="text-slate-400">{a.tokenHint}</code>}
                        {a.lastError && <span className="text-rose-600">{a.lastError}</span>}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  );
}
