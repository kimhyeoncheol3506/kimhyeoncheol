"use client";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { Toggle } from "@/components/Toggle";
import { accountRole, allPermissions, permission } from "@/lib/labels";
import { newId, today } from "@/lib/format";
import type { AccountRole, Permission } from "@/lib/types";

// 계정 · 권한: 사람 계정 등록, 구매자(고객) 목록, AI 직원 권한 한눈에 보기
export default function Accounts() {
  const { data, add, update } = useStore();

  const togglePerm = (staffId: string, p: Permission) => {
    const s = data.staff.find((x) => x.id === staffId);
    if (!s) return;
    update("staff", staffId, {
      permissions: s.permissions.includes(p) ? s.permissions.filter((x) => x !== p) : [...s.permissions, p],
    });
  };

  return (
    <>
      <PageHeader title="계정 · 권한" desc="운영자 계정, 구매자 목록, AI 직원 권한을 관리합니다." />

      {/* 운영자 계정 */}
      <section className="card">
        <h2 className="font-semibold">👤 운영자 계정</h2>
        <AccountForm onSubmit={(a) => add("accounts", { id: newId("a"), active: true, createdAt: today(), ...a })} />
        <div className="mt-4 overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-line">
              <tr>
                <th className="th">이름</th>
                <th className="th">이메일</th>
                <th className="th">역할</th>
                <th className="th">등록일</th>
                <th className="th">사용</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {data.accounts.map((a) => (
                <tr key={a.id}>
                  <td className="td font-medium">{a.name}</td>
                  <td className="td text-sub">{a.email}</td>
                  <td className="td">
                    {a.role === "owner" ? (
                      <Badge label={accountRole.owner} />
                    ) : (
                      <select className="input w-auto py-1 text-xs" value={a.role} onChange={(e) => update("accounts", a.id, { role: e.target.value as AccountRole })}>
                        <option value="manager">관리자</option>
                        <option value="viewer">열람</option>
                      </select>
                    )}
                  </td>
                  <td className="td text-sub">{a.createdAt}</td>
                  <td className="td">
                    <Toggle on={a.active} onClick={() => a.role !== "owner" && update("accounts", a.id, { active: !a.active })} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* AI 직원 권한 */}
      <section className="card mt-4">
        <h2 className="font-semibold">🔐 AI 직원 권한</h2>
        <p className="mt-1 text-xs text-mute">스위치를 끄면 해당 직원은 그 일을 할 수 없습니다. (재무 접근 · 메일 발송은 신중하게)</p>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-line">
              <tr>
                <th className="th">직원</th>
                {allPermissions.map((p) => (
                  <th key={p} className="th text-center">
                    {permission[p]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {data.staff.map((s) => (
                <tr key={s.id}>
                  <td className="td font-medium">
                    {s.avatar} {s.name}
                    <span className="ml-1 text-xs text-mute">{s.role}</span>
                  </td>
                  {allPermissions.map((p) => (
                    <td key={p} className="td text-center">
                      <Toggle on={s.permissions.includes(p)} onClick={() => togglePerm(s.id, p)} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 구매자 */}
      <section className="card mt-4">
        <h2 className="font-semibold">🧾 구매자 목록</h2>
        <BuyerForm onSubmit={(b) => add("buyers", { id: newId("b"), registeredAt: today(), ...b })} />
        <div className="mt-4 overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-line">
              <tr>
                <th className="th">담당자</th>
                <th className="th">회사</th>
                <th className="th">이메일</th>
                <th className="th">연락처</th>
                <th className="th text-right">주문 수</th>
                <th className="th">등록일</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {data.buyers.map((b) => (
                <tr key={b.id}>
                  <td className="td font-medium">{b.name}</td>
                  <td className="td">{b.company}</td>
                  <td className="td text-sub">{b.email}</td>
                  <td className="td text-sub">{b.phone}</td>
                  <td className="td text-right">{data.orders.filter((o) => o.buyerId === b.id).length}</td>
                  <td className="td text-sub">{b.registeredAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function AccountForm({ onSubmit }: { onSubmit: (a: { name: string; email: string; role: AccountRole }) => void }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<AccountRole>("manager");
  return (
    <form
      className="mt-3 grid gap-2 sm:grid-cols-4"
      onSubmit={(e) => {
        e.preventDefault();
        if (!name.trim() || !email.includes("@")) return;
        onSubmit({ name: name.trim(), email: email.trim(), role });
        setName("");
        setEmail("");
      }}
    >
      <input className="input" placeholder="이름" value={name} onChange={(e) => setName(e.target.value)} />
      <input className="input" placeholder="이메일" value={email} onChange={(e) => setEmail(e.target.value)} />
      <select className="input" value={role} onChange={(e) => setRole(e.target.value as AccountRole)}>
        <option value="manager">관리자</option>
        <option value="viewer">열람</option>
      </select>
      <button className="btn-primary" disabled={!name.trim() || !email.includes("@")}>
        ＋ 계정 등록
      </button>
    </form>
  );
}

function BuyerForm({ onSubmit }: { onSubmit: (b: { name: string; company: string; email: string; phone: string }) => void }) {
  const [f, setF] = useState({ name: "", company: "", email: "", phone: "" });
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value });
  return (
    <form
      className="mt-3 grid gap-2 sm:grid-cols-5"
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.name.trim() || !f.company.trim()) return;
        onSubmit(f);
        setF({ name: "", company: "", email: "", phone: "" });
      }}
    >
      <input className="input" placeholder="담당자" value={f.name} onChange={set("name")} />
      <input className="input" placeholder="회사" value={f.company} onChange={set("company")} />
      <input className="input" placeholder="이메일" value={f.email} onChange={set("email")} />
      <input className="input" placeholder="연락처" value={f.phone} onChange={set("phone")} />
      <button className="btn-primary" disabled={!f.name.trim() || !f.company.trim()}>
        ＋ 구매자 등록
      </button>
    </form>
  );
}
