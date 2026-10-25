import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { staffOptions } from "@/lib/services/reports";
import { listTeams } from "@/lib/services/teams";
import { Card, CardBody, PageHeader } from "@/components/ui/card";
import { Forbidden } from "@/components/ui/misc";
import { ClientForm } from "@/components/forms/client-form";

export const metadata = { title: "고객 등록" };

export default async function NewClientPage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "client:write")) return <Forbidden />;
  const [staff, teams] = await Promise.all([staffOptions(ctx), listTeams(ctx)]);
  return (
    <>
      <PageHeader title="고객 등록" description="고객 기본 정보와 브랜드 프로필을 입력합니다." />
      <Card>
        <CardBody>
          <ClientForm managers={staff} teams={teams.map((t) => ({ id: t.id, name: t.name }))} />
        </CardBody>
      </Card>
    </>
  );
}
