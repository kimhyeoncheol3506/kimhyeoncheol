import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getCampaign } from "@/lib/services/campaigns";
import { listClientOptions } from "@/lib/services/clients";
import { dateInput } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { Card, CardBody, PageHeader } from "@/components/ui/card";
import { Alert, Forbidden } from "@/components/ui/misc";
import { BriefForm } from "@/components/forms/brief-form";

export const metadata = { title: "캠페인 수정" };

export default async function EditCampaignPage({ params }: { params: Promise<{ id: string }> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "campaign:write")) return <Forbidden />;
  const { id } = await params;
  const [c, clients] = await Promise.all([orNotFound(getCampaign(ctx, id)), listClientOptions(ctx)]);
  const b = c.brief;
  return (
    <>
      <PageHeader title="캠페인 수정" description={c.name} />
      {(c.status === "DRAFT" || c.status === "ANALYZED") && b?.analyzedAt && (
        <div className="mb-4">
          <Alert tone="warn">의뢰 내용을 저장하면 기존 AI 분석 결과가 초기화되며, 다시 분석해야 합니다.</Alert>
        </div>
      )}
      <Card>
        <CardBody>
          <BriefForm
            clients={clients}
            values={{
              id: c.id,
              clientId: c.clientId,
              title: b?.title ?? c.name,
              targetUrl: b?.targetUrl,
              targetType: b?.targetType,
              goal: b?.goal,
              coreTarget: b?.coreTarget,
              budget: c.budget,
              startDate: dateInput(c.startDate),
              endDate: dateInput(c.endDate),
              desiredPlatforms: b?.desiredPlatforms,
              keywords: b?.keywords,
              bannedKeywords: b?.bannedKeywords,
              description: b?.description,
            }}
          />
        </CardBody>
      </Card>
    </>
  );
}
