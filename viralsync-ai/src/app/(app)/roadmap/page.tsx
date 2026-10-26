import Link from "next/link";
import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { businessProfile, roadmapChecks } from "@/lib/services/business";
import { currentWeek, ROADMAP, ROADMAP_KEYS } from "@/lib/business/roadmap";
import { dateOnly } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ProfileForm, RoadmapToggle } from "@/components/business/forms";

export const metadata = { title: "52주 실행표" };

export default async function RoadmapPage() {
  const ctx = await requireCtx();
  const [profile, checks] = await Promise.all([businessProfile(ctx), roadmapChecks(ctx)]);
  const week = currentWeek(profile.businessStartDate);
  const done = ROADMAP_KEYS.filter((k) => checks.has(k)).length;
  const canCheck = can(ctx.role, "sales:manage");
  return (
    <>
      <PageHeader
        title="52주 실행표"
        description="사업은 읽는 게 아니라 파는 것. 이번 주 할 일부터 체크하세요. 첫 계약 1건 → 1년 유지 → 과정을 글로 남기기."
      />
      <Card className="mb-6">
        <div id="settings" />
        <CardHeader title="사업 기본값" description={`전체 ${done}/${ROADMAP_KEYS.length} 완료${week ? ` · 지금 ${week}주차` : " · 시작일을 정하면 몇 주차인지 보여 드려요"}`} />
        <CardBody>
          <div className="mb-4 h-2 rounded bg-slate-100"><div className="h-2 rounded bg-emerald-500" style={{ width: `${(done / ROADMAP_KEYS.length) * 100}%` }} /></div>
          <ProfileForm
            canEdit={can(ctx.role, "finance:manage")}
            v={{ positioning: profile.positioning, targetIndustry: profile.targetIndustry, businessStartDate: profile.businessStartDate?.toISOString().slice(0, 10) ?? "", cashReserveKrw: profile.cashReserveKrw }}
          />
        </CardBody>
      </Card>
      <div className="space-y-6">
        {ROADMAP.map((st) => {
          const now = week != null && week >= st.weeks[0] && week <= st.weeks[1];
          const n = st.items.filter((i) => checks.has(i.key)).length;
          return (
            <Card key={st.title} className={now ? "ring-2 ring-brand-400" : ""}>
              <CardHeader title={<span>{st.title} {now && <Badge tone="indigo">이번 주</Badge>}</span>} description={`목표: ${st.goal} · ${n}/${st.items.length}`} />
              <CardBody>
                <ul className="space-y-2">
                  {st.items.map((it) => {
                    const at = checks.get(it.key);
                    return (
                      <li key={it.key} className="flex items-start gap-2 text-sm">
                        {canCheck ? <RoadmapToggle itemKey={it.key} done={!!at} label={it.text} /> : <span aria-hidden>{at ? "✅" : "⬜"}</span>}
                        <span className={at ? "text-slate-400 line-through" : ""}>{it.text}</span>
                        <span className="ml-auto flex shrink-0 items-center gap-2 text-[11px] text-slate-400">
                          {it.part}
                          {it.href && <Link href={it.href} className="link">열기</Link>}
                          {at && dateOnly(at)}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </>
  );
}
