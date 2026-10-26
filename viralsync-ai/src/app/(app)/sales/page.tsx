import Link from "next/link";
import type { ProspectStage } from "@prisma/client";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { DAILY_DM_GOAL, LIST_GOAL, listProspects, salesStats, STAGE_ORDER } from "@/lib/services/sales";
import { OBJECTIONS } from "@/lib/business/playbook";
import { PROSPECT_STAGE_LABEL } from "@/lib/labels";
import { dateOnly, num } from "@/lib/format";
import { str, type SP } from "@/lib/page";
import { prisma } from "@/lib/db";
import { Card, CardBody, CardHeader, PageHeader, StatCard } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState, Forbidden, Table } from "@/components/ui/misc";
import { ImportForm, ProspectForm } from "@/components/sales/forms";
import { Button } from "@/components/ui/button";

export const metadata = { title: "영업 리스트" };

export default async function SalesPage({ searchParams }: { searchParams: Promise<SP> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "sales:manage")) return <Forbidden />;
  const sp = await searchParams;
  const stageRaw = str(sp, "stage");
  const stage = stageRaw && (STAGE_ORDER as string[]).includes(stageRaw) ? (stageRaw as ProspectStage) : undefined;
  const q = str(sp, "q");
  const [rows, s, org] = await Promise.all([
    listProspects(ctx, { stage, q }),
    salesStats(ctx),
    prisma.organization.findUniqueOrThrow({ where: { id: ctx.organizationId }, select: { targetIndustry: true } }),
  ]);
  const pct = (a: number, b: number) => (b ? `${Math.round((a / b) * 100)}%` : "-");

  return (
    <>
      <PageHeader
        title="영업 리스트"
        description="동네 가게 100곳을 적고, 하루 10통씩 ‘진단형’ DM 을 보냅니다. DM 은 캡틴 계정에서 직접 보내고, 여기에는 기록만 남깁니다 (자동 발송 없음)."
      />
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="사냥 리스트" value={`${s.total} / ${LIST_GOAL}`} hint="목표 100곳" tone={s.total >= LIST_GOAL ? "good" : "default"} />
        <StatCard label="오늘 보낸 DM" value={`${s.dmToday} / ${DAILY_DM_GOAL}`} hint={`누적 ${num(s.dmTotal)}통`} tone={s.dmToday >= DAILY_DM_GOAL ? "good" : "warn"} />
        <StatCard label="답장 → 만남" value={`${s.replied} → ${s.met}`} hint={`답장률 ${pct(s.replied, s.dmTotal)} · 보통 100통에 5~10개`} />
        <StatCard label="계약 (체험·유료)" value={`${s.count.TRIAL} · ${s.count.WON}`} hint={s.count.WAITLIST ? `대기 고객 ${s.count.WAITLIST}명` : "100통에 계약 1건이 보통"} tone={s.count.WON > 0 ? "good" : "default"} />
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <Card>
            <CardHeader title={`가게 목록 (${rows.length})`} description="3개월 넘게 게시물이 없는 가게가 1순위입니다" />
            <CardBody>
              <form className="mb-3 flex flex-wrap gap-2" action="/sales">
                <label htmlFor="q" className="sr-only">검색</label>
                <input id="q" name="q" defaultValue={q} placeholder="가게·지역·업종 검색" className="input max-w-xs" />
                <label htmlFor="stage" className="sr-only">단계</label>
                <select id="stage" name="stage" defaultValue={stage ?? ""} className="input w-auto">
                  <option value="">전체 단계</option>
                  {STAGE_ORDER.map((st) => <option key={st} value={st}>{PROSPECT_STAGE_LABEL[st]} ({s.count[st]})</option>)}
                </select>
                <Button type="submit" variant="secondary">적용</Button>
              </form>
              {rows.length === 0 ? (
                <EmptyState title="아직 리스트가 없습니다" description="카카오맵·네이버 지도에서 업종을 검색해 인스타 게시물이 뜸한 가게를 적어 보세요." />
              ) : (
                <Table minWidth={720}>
                  <thead>
                    <tr className="text-left text-xs text-slate-500">
                      {["가게", "업종·지역", "인스타", "마지막 게시", "단계", "DM"].map((h) => <th key={h} className="th">{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((p) => {
                      const stale = p.lastPostAt && Date.now() - p.lastPostAt.getTime() > 90 * 86_400_000;
                      return (
                        <tr key={p.id} className="border-t border-slate-100">
                          <td className="td min-w-36"><Link href={`/sales/${p.id}`} className="link font-medium">{p.name}</Link></td>
                          <td className="td text-xs">{p.industry || "-"} · {p.region || "-"}</td>
                          <td className="td text-xs">{p.instagram ?? "-"}{p.followers != null && <span className="text-slate-400"> · {num(p.followers)}</span>}</td>
                          <td className="td text-xs">{p.lastPostAt ? dateOnly(p.lastPostAt) : "-"} {stale && <Badge tone="amber">3개월+</Badge>}</td>
                          <td className="td"><Badge tone={p.stage === "WON" ? "green" : p.stage === "LOST" ? "gray" : p.stage === "LISTED" ? "gray" : "indigo"}>{PROSPECT_STAGE_LABEL[p.stage]}</Badge></td>
                          <td className="td whitespace-nowrap text-xs">{p.dmSentAt ? dateOnly(p.dmSentAt) : "-"}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </Table>
              )}
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="가게 추가" />
            <CardBody className="space-y-6">
              <ProspectForm defaultIndustry={org.targetIndustry} />
              <div className="border-t border-slate-100 pt-4"><ImportForm /></div>
            </CardBody>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader title="첫 만남 루틴" description="PART 7-4" />
            <CardBody>
              <ol className="list-decimal space-y-1 pl-5 text-sm">
                <li>카페에서 30분 — 팔지 말고 가게 이야기를 듣기</li>
                <li>24시간 안에 ‘진단 요약 + 무료 시안 1개’ 보내기</li>
                <li>시안에 대해 전화 10분, 수정 반영</li>
                <li>패키지 표 보여 주고 ‘2주 무료 후 결정’ (당일 계약 압박 금지)</li>
              </ol>
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="반박 대응" description="휴대폰 메모에도 저장해 두세요" />
            <CardBody>
              <dl className="space-y-3 text-sm">
                {OBJECTIONS.map((o) => (
                  <div key={o.q}>
                    <dt className="font-medium text-slate-800">“{o.q}”</dt>
                    <dd className="mt-0.5 text-slate-600">→ {o.a}</dd>
                  </div>
                ))}
              </dl>
            </CardBody>
          </Card>
        </div>
      </div>
    </>
  );
}
