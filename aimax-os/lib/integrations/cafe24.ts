// 카페24 주문 연동 (서버에서만 실행)
// .env.local 에 CAFE24_MALL_ID, CAFE24_ACCESS_TOKEN 을 넣으면 실제 주문을 가져옵니다.
// 카페24 Admin API 문서: https://developers.cafe24.com/docs/api/admin/#orders
// ※ 아래 응답 필드 이름(order_id 등)은 실제 연결 후 카페24 응답과 한 번 대조해 주세요.

export interface Cafe24Order {
  id: string;
  buyerName: string;
  product: string;
  amount: number;
  orderedAt: string;
}

export function isCafe24Configured(): boolean {
  return Boolean(process.env.CAFE24_MALL_ID && process.env.CAFE24_ACCESS_TOKEN);
}

export async function fetchCafe24Orders(startDate: string, endDate: string): Promise<Cafe24Order[]> {
  const mall = process.env.CAFE24_MALL_ID;
  const token = process.env.CAFE24_ACCESS_TOKEN;
  const url = `https://${mall}.cafe24api.com/api/v2/admin/orders?start_date=${startDate}&end_date=${endDate}&embed=items`;

  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`카페24 응답 오류 (${res.status}): ${(await res.text()).slice(0, 300)}`);
  }
  const json = (await res.json()) as { orders?: Record<string, unknown>[] };

  return (json.orders ?? []).map((o) => {
    const items = (o.items as { product_name?: string }[] | undefined) ?? [];
    const amount = (o.actual_order_amount as { payment_amount?: string } | undefined)?.payment_amount ?? o.payment_amount ?? 0;
    return {
      id: String(o.order_id),
      buyerName: String(o.billing_name ?? o.buyer_name ?? "카페24 고객"),
      product: items[0]?.product_name ?? "카페24 주문",
      amount: Number(amount),
      orderedAt: String(o.order_date ?? "").replace("T", " ").slice(0, 16),
    };
  });
}
