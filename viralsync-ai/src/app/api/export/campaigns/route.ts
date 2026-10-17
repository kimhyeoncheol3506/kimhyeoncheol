import { NextResponse, type NextRequest } from "next/server";
import { getCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { campaignSummary, parseReportFilter } from "@/lib/services/reports";
import { campaignsCsv } from "@/lib/export";
import { audit } from "@/lib/services/audit";

export async function GET(req: NextRequest) {
  const ctx = await getCtx();
  if (!ctx) return NextResponse.json({ error: "인증이 필요합니다." }, { status: 401 });
  if (!can(ctx.role, "report:export")) return NextResponse.json({ error: "내보내기 권한이 없습니다." }, { status: 403 });
  const filter = parseReportFilter(Object.fromEntries(req.nextUrl.searchParams));
  const rows = await campaignSummary(ctx, filter);
  await audit(ctx, "report.export", "Campaign", null, `캠페인 실적 CSV 내보내기 (${rows.length}행)`);
  return new NextResponse(campaignsCsv(rows, can(ctx.role, "cost:read")), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="viralsync-campaigns-${new Date().toISOString().slice(0, 10)}.csv"`,
      "Cache-Control": "no-store",
    },
  });
}
