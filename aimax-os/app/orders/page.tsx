"use client";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { integrationStatus, orderStatus } from "@/lib/labels";
import { newId, nowStamp, today, won } from "@/lib/format";
import type { OrderStatus } from "@/lib/types";
import type { Cafe24Order } from "@/lib/integrations/cafe24";

// 주문 및 연동 관리
export default function Orders() {
  const { data, add, update, logError } = useStore();
  const [syncing, setSyncing] = useState(false);
  const [notice, setNotice] = useState("");

  const buyer = (id: string) => data.buyers.find((b) => b.id === id);
  const total = data.orders.filter((o) => o.status !== "refunded").reduce((s, o) => s + o.amount, 0);

  // 카페24 주문 가져오기. 실패하면 오류 센터에 자동 기록됩니다.
  const syncCafe24 = async () => {
    setSyncing(true);
    setNotice("");
    try {
      const res = await fetch("/api/cafe24/orders");
      const body = (await res.json()) as { connected: boolean; message?: string; error?: string; orders?: Cafe24Order[] };
      if (!body.connected) {
        setNotice(body.message ?? "카페24 연결이 필요해요.");
        update("integrations", "cafe24", { status: "needs_connection" });
        return;
      }
      if (body.error) throw new Error(body.error);

      let added = 0;
      for (const o of body.orders ?? []) {
        if (data.orders.some((x) => x.id === `c24-${o.id}`)) continue;
        let b = data.buyers.find((x) => x.name === o.buyerName);
        if (!b) {
          b = { id: newId("b"), name: o.buyerName, company: "-", email: "", phone: "", registeredAt: today() };
          add("buyers", b);
        }
        add("orders", { id: `c24-${o.id}`, channel: "cafe24", buyerId: b.id, product: o.product, amount: o.amount, status: "paid", orderedAt: o.orderedAt });
        added++;
      }
      update("integrations", "cafe24", { status: "connected", lastSync: nowStamp() });
      setNotice(`카페24 주문 ${added}건을 새로 가져왔어요.`);
    } catch (e) {
      update("integrations", "cafe24", { status: "error" });
      logError({ title: "카페24 동기화 실패", message: (e as Error).message, page: "/orders", severity: "high" });
      setNotice("동기화에 실패했어요. 오류 · 피드백 센터에 기록했습니다.");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <>
      <PageHeader
        title="주문 · 연동 관리"
        desc="카페24 등 외부 서비스 연결 상태와 주문을 관리합니다."
        actions={
          <button className="btn-primary" onClick={syncCafe24} disabled={syncing}>
            {syncing ? "가져오는 중…" : "🔄 카페24 주문 가져오기"}
          </button>
        }
      />

      {notice && <p className="mb-4 rounded-lg bg-brand-soft px-4 py-3 text-sm text-brand">{notice}</p>}

      <h2 className="mb-2 font-semibold">연동 상태</h2>
      <div className="mb-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {data.integrations.map((i) => (
          <div key={i.id} className="card p-4">
            <div className="flex items-center justify-between">
              <p className="font-semibold">{i.name}</p>
              <Badge label={integrationStatus[i.status]} />
            </div>
            <p className="mt-1 text-sm text-sub">{i.description}</p>
            <p className="mt-2 text-xs text-mute">마지막 동기화: {i.lastSync ?? "없음"}</p>
          </div>
        ))}
      </div>

      <div className="mb-2 flex items-end justify-between">
        <h2 className="font-semibold">주문 목록</h2>
        <p className="text-sm text-sub">
          합계(환불 제외) <b className="text-ink">{won(total)}</b>
        </p>
      </div>
      <div className="card overflow-x-auto p-0">
        <table className="w-full">
          <thead className="border-b border-line bg-canvas">
            <tr>
              <th className="th">주문번호</th>
              <th className="th">채널</th>
              <th className="th">고객사</th>
              <th className="th">상품</th>
              <th className="th text-right">금액</th>
              <th className="th">주문일</th>
              <th className="th">상태</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {data.orders.map((o) => (
              <tr key={o.id}>
                <td className="td font-mono text-xs">{o.id}</td>
                <td className="td">{o.channel === "cafe24" ? "카페24" : "직접"}</td>
                <td className="td">{buyer(o.buyerId)?.company ?? "-"}</td>
                <td className="td">{o.product}</td>
                <td className="td text-right font-semibold">{won(o.amount)}</td>
                <td className="td text-sub">{o.orderedAt}</td>
                <td className="td">
                  <select
                    className="input w-auto py-1 text-xs"
                    value={o.status}
                    onChange={(e) => update("orders", o.id, { status: e.target.value as OrderStatus })}
                  >
                    {(Object.keys(orderStatus) as OrderStatus[]).map((k) => (
                      <option key={k} value={k}>
                        {orderStatus[k].text}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
