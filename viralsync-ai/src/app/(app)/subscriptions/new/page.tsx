import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listClientOptions } from "@/lib/services/clients";
import { monthlyPlans } from "@/lib/services/subscriptions";
import { str, type SP } from "@/lib/page";
import { Card, CardBody, PageHeader } from "@/components/ui/card";
import { Forbidden } from "@/components/ui/misc";
import { SubscriptionForm } from "@/components/subscriptions/forms";

export const metadata = { title: "새 월 정액 계약" };

export default async function NewSubscriptionPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "sales:manage")) return <Forbidden />;
  const sp = await searchParams;
  const [clients, plans] = await Promise.all([listClientOptions(ctx), monthlyPlans(ctx)]);
  const today = new Date(Date.now() + 9 * 3_600_000).toISOString().slice(0, 10);
  return (
    <>
      <PageHeader title="새 월 정액 계약" description="가격은 깎지 말고 양(패키지)으로 조절합니다. 무료 체험은 시작일·종료일이 계약서에 들어갑니다." />
      <Card>
        <CardBody>
          <SubscriptionForm clients={clients} plans={plans} clientId={str(sp, "clientId")} today={today} />
        </CardBody>
      </Card>
    </>
  );
}
