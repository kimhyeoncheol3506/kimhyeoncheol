import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { staffOptions } from "@/lib/services/reports";
import { Card, CardBody, PageHeader } from "@/components/ui/card";
import { Forbidden } from "@/components/ui/misc";
import { PolicyForm } from "@/components/forms/policy-form";

export const metadata = { title: "정책 검토 등록" };

export default async function NewPolicyPage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "policy:write")) return <Forbidden />;
  const users = await staffOptions(ctx);
  const next = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);
  return (
    <>
      <PageHeader title="정책 검토 등록" />
      <Card>
        <CardBody>
          <PolicyForm users={users} values={{ nextReviewAt: next }} />
        </CardBody>
      </Card>
    </>
  );
}
