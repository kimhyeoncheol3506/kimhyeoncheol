import { NextResponse } from "next/server";
import { fetchCafe24Orders, isCafe24Configured } from "@/lib/integrations/cafe24";

export const dynamic = "force-dynamic";

// GET /api/cafe24/orders → 최근 30일 카페24 주문
export async function GET() {
  if (!isCafe24Configured()) {
    return NextResponse.json({
      connected: false,
      message: "카페24 연결 정보가 없어요. aimax-os/.env.local 에 CAFE24_MALL_ID, CAFE24_ACCESS_TOKEN 을 넣어 주세요.",
    });
  }
  const end = new Date();
  const start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000);
  const ymd = (d: Date) => d.toISOString().slice(0, 10);
  try {
    const orders = await fetchCafe24Orders(ymd(start), ymd(end));
    return NextResponse.json({ connected: true, orders });
  } catch (e) {
    return NextResponse.json({ connected: true, error: (e as Error).message }, { status: 502 });
  }
}
