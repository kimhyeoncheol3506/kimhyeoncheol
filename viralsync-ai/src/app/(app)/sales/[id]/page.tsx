import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { getProspect } from "@/lib/services/sales";
import { dmDraft, INTERVIEW_QUESTIONS } from "@/lib/business/playbook";
import { PROSPECT_STAGE_LABEL } from "@/lib/labels";
import { dateOnly, num } from "@/lib/format";
import { orNotFound } from "@/lib/page";
import { prisma } from "@/lib/db";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Forbidden } from "@/components/ui/misc";
import { LinkButton } from "@/components/ui/button";
import { CopyText } from "@/components/ui/copy-text";
import { ConvertButton, ProspectForm, StageButtons } from "@/components/sales/forms";

export default async function ProspectPage({ params }: { params: Promise<{ id: string }> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "sales:manage")) return <Forbidden />;
  const p = await orNotFound(getProspect(ctx, (await params).id));
  const org = await prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { positioning: true } });
  const ymd = (d: Date | null) => (d ? d.toISOString().slice(0, 10) : "");

  return (
    <>
      <PageHeader
        title={p.name}
        description={
          <span className="flex flex-wrap items-center gap-2">
            <Badge tone="indigo">{PROSPECT_STAGE_LABEL[p.stage]}</Badge>
            <span className="text-xs text-slate-500">{p.industry || "업종 미입력"} · {p.region || "지역 미입력"} · {p.instagram ?? "인스타 미입력"}{p.followers != null && ` · 팔로워 ${num(p.followers)}`}</span>
            <Link href="/sales" className="link text-xs">← 영업 리스트</Link>
          </span>
        }
        actions={<LinkButton href={`/sales/${p.id}/proposal`} variant="secondary">제안서 3페이지</LinkButton>}
      />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="1. 진단형 첫 DM" description="그 가게 사진으로 만든 20초 시안 링크와 함께, 캡틴 계정에서 직접 보내세요" />
          <CardBody className="space-y-3">
            <CopyText id="dm" label="DM 초안 (수정 가능)" text={dmDraft(p, org.positioning)} rows={7} />
            <p className="text-xs text-slate-500">보냈으면 아래 ‘DM 보냄 ✓’ 을 눌러 기록하세요. 하루 10통이 목표입니다.</p>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="2. 단계 기록" description={`DM ${p.dmSentAt ? dateOnly(p.dmSentAt) : "-"} · 답장 ${p.repliedAt ? dateOnly(p.repliedAt) : "-"} · 만남 ${p.meetingAt ? dateOnly(p.meetingAt) : "-"}`} />
          <CardBody className="space-y-4">
            <StageButtons id={p.id} current={p.stage} />
            {can(ctx.role, "client:write") && (
              p.clientId ? (
                <p className="text-sm">고객으로 등록됨 → <Link className="link" href={`/clients/${p.clientId}`}>고객 보기</Link> · <Link className="link" href={`/subscriptions/new?clientId=${p.clientId}`}>월 정액 계약 만들기</Link></p>
              ) : (
                <div className="rounded-lg bg-slate-50 p-3">
                  <p className="mb-2 text-xs text-slate-600">만남 후 ‘2주 무료 체험’ 에 동의하면 고객으로 등록하고 계약을 만드세요.</p>
                  <ConvertButton id={p.id} />
                </div>
              )
            )}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="3. 만남 때 물어볼 것" description="팔지 말고 들으세요 (30분)" />
          <CardBody>
            <ol className="list-decimal space-y-1 pl-5 text-sm">{INTERVIEW_QUESTIONS.map((q) => <li key={q}>{q}</li>)}</ol>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="가게 정보·진단 메모" />
          <CardBody>
            <ProspectForm values={{ ...p, lastPostAt: ymd(p.lastPostAt) }} />
          </CardBody>
        </Card>
      </div>
    </>
  );
}
