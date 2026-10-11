import { getDataset } from "@/lib/dataset";
import { channelsCsv, datasetJson, snapshotsCsv, videosCsv } from "@/lib/export";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export function GET(req: Request) {
  const url = new URL(req.url);
  const type = url.searchParams.get("type") ?? "videos";
  const format = url.searchParams.get("format") ?? "csv";
  const ds = getDataset();
  const stamp = new Date().toISOString().slice(0, 10);
  const prefix = ds.source === "demo" ? "DEMO_" : "";
  if (format === "json") {
    return new Response(JSON.stringify(datasetJson(ds), null, 1), {
      headers: { "Content-Type": "application/json; charset=utf-8", "Content-Disposition": `attachment; filename="${prefix}faceless-econ_${stamp}.json"` },
    });
  }
  const csv = type === "channels" ? channelsCsv(ds) : type === "snapshots" ? snapshotsCsv(ds) : videosCsv(ds);
  return new Response(csv, {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="${prefix}${type}_${stamp}.csv"` },
  });
}
