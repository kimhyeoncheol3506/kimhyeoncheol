import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { Card, CardBody, PageHeader } from "@/components/ui/card";
import { Forbidden } from "@/components/ui/misc";
import { InquiryForm } from "@/components/inquiry/inquiry-form";

export const metadata = { title: "문의 붙여넣기" };

export default async function NewInquiryPage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "inquiry:manage")) return <Forbidden />;
  return (
    <>
      <PageHeader title="문의 붙여넣기" description="고객 메시지 원문을 그대로 붙여넣으면 자동으로 분석합니다." />
      <Card>
        <CardBody>
          <InquiryForm />
        </CardBody>
      </Card>
    </>
  );
}
