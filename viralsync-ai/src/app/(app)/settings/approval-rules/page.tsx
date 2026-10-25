import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listRules } from "@/lib/services/approvals";
import { APPROVAL_GATE_LABEL, ROLE_LABEL } from "@/lib/labels";
import { won } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, Forbidden } from "@/components/ui/misc";
import { DeleteRuleButton, RuleForm } from "@/components/forms/org-forms";

export const metadata = { title: "결재 규칙" };

export default async function ApprovalRulesPage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "user:manage")) return <Forbidden />;
  const rules = await listRules(ctx);
  return (
    <>
      <PageHeader title="결재 규칙" description="업무(문구·견적·계약)마다 금액·위험도 조건에 따라 결재 라인을 정합니다. 조건에 맞는 규칙이 여러 개면 가장 엄격한(단계가 많은) 규칙이 적용됩니다." />
      <div className="mb-4">
        <Alert tone="info">
          원칙: 요청자 본인은 결재할 수 없고, 한 사람이 같은 결재의 두 단계를 처리할 수 없습니다. 관리자는 모든 단계를 대결할 수 있습니다. 홍보 문구는 규칙이 없어도 검토자 1단계 결재가 적용됩니다.
        </Alert>
      </div>
      <Card className="mb-6">
        <CardHeader title="규칙 추가" />
        <CardBody><RuleForm /></CardBody>
      </Card>
      <div className="space-y-3">
        {rules.map((r) => (
          <Card key={r.id} className={r.active ? "" : "opacity-60"}>
            <CardBody>
              <div className="flex flex-wrap items-center gap-2">
                <Badge tone="indigo">{APPROVAL_GATE_LABEL[r.gate]}</Badge>
                <span className="font-semibold">{r.name}</span>
                <span className="text-xs text-slate-500">
                  {r.minAmount != null ? `${won(r.minAmount)} 이상` : "금액 무관"} · {r.minRisk ? `위험도 ${r.minRisk} 이상` : "위험도 무관"}
                </span>
                <span className="text-sm">{r.steps.length ? r.steps.map((s) => ROLE_LABEL[s]).join(" → ") : "결재 없음"}</span>
                {r.aiPrecheck && <Badge tone="red">AI 차단 적용</Badge>}
                {!r.active && <Badge tone="gray">사용 안 함</Badge>}
                <span className="ml-auto"><DeleteRuleButton id={r.id} /></span>
              </div>
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-brand-600">수정</summary>
                <div className="mt-3"><RuleForm rule={r} /></div>
              </details>
            </CardBody>
          </Card>
        ))}
      </div>
    </>
  );
}
