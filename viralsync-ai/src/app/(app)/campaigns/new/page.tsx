import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listClientOptions } from "@/lib/services/clients";
import { Card, CardBody, PageHeader } from "@/components/ui/card";
import { EmptyState, Forbidden } from "@/components/ui/misc";
import { LinkButton } from "@/components/ui/button";
import { BriefForm } from "@/components/forms/brief-form";

export const metadata = { title: "광고 의뢰 접수" };

export default async function NewCampaignPage({ searchParams }: { searchParams: Promise<{ clientId?: string }> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "campaign:write")) return <Forbidden />;
  const { clientId } = await searchParams;
  const clients = await listClientOptions(ctx);
  return (
    <>
      <PageHeader title="광고 의뢰 접수" description="고객의 홍보 의뢰를 접수합니다. 접수 후 AI 분석을 실행할 수 있습니다." />
      {clients.length === 0 ? (
        <EmptyState title="먼저 고객을 등록하세요" action={<LinkButton href="/clients/new">고객 등록</LinkButton>} />
      ) : (
        <Card>
          <CardBody>
            <BriefForm clients={clients} values={{ clientId }} />
          </CardBody>
        </Card>
      )}
    </>
  );
}
