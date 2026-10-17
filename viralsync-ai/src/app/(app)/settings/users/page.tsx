import { requireCtx } from "@/lib/auth/current";
import { can, permissionsOf, PERMISSIONS } from "@/lib/auth/permissions";
import { listUsers } from "@/lib/services/users";
import { listClientOptions } from "@/lib/services/clients";
import { ROLE_LABEL } from "@/lib/labels";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Forbidden, Table } from "@/components/ui/misc";
import { CreateUserForm, UserRow } from "@/components/forms/user-forms";
import type { Role } from "@prisma/client";

export const metadata = { title: "직원·권한 관리" };

const PERM_LABEL: Record<string, string> = {
  "client:read": "고객 조회",
  "client:pii": "고객 연락처·계약",
  "client:write": "고객 등록·수정",
  "campaign:read": "캠페인 조회",
  "campaign:write": "의뢰 접수·수정",
  "analysis:run": "AI 분석",
  "candidate:write": "후보 관리",
  "content:generate": "문구 생성",
  "content:edit": "문구 수정",
  "approval:decide": "승인·반려",
  "publication:execute": "실행",
  "cost:read": "비용 데이터",
  "account:manage": "SNS 인증정보",
  "policy:write": "정책 검토",
  "user:manage": "직원 관리",
  "report:export": "보고서·CSV",
  "audit:read": "감사 로그",
};

export default async function UsersPage() {
  const ctx = await requireCtx();
  if (!can(ctx.role, "user:manage")) return <Forbidden />;
  const [users, clients] = await Promise.all([listUsers(ctx), listClientOptions(ctx)]);
  const roles = Object.keys(ROLE_LABEL) as Role[];
  return (
    <>
      <PageHeader title="직원 및 권한 관리" description="역할별 권한과 직원별 고객 접근 범위를 관리합니다. 관리자 외 역할은 배정된 고객 데이터만 볼 수 있습니다." />
      <Card className="mb-6">
        <CardHeader title="역할별 권한표" />
        <Table minWidth={720}>
          <thead className="bg-slate-50">
            <tr>
              <th className="th">권한</th>
              {roles.map((r) => <th key={r} className="th text-center">{ROLE_LABEL[r]}</th>)}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {PERMISSIONS.map((p) => (
              <tr key={p}>
                <td className="td text-xs">{PERM_LABEL[p]}</td>
                {roles.map((r) => (
                  <td key={r} className="td text-center" aria-label={permissionsOf(r).includes(p) ? "허용" : "불가"}>
                    {permissionsOf(r).includes(p) ? "●" : <span className="text-slate-300">–</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>
      <Card className="mb-6">
        <CardHeader title="직원 등록" />
        <CardBody><CreateUserForm /></CardBody>
      </Card>
      <h2 className="mb-3 text-sm font-semibold text-slate-900">직원 목록 ({users.length})</h2>
      <div className="space-y-3">
        {users.map((u) => (
          <UserRow key={u.id} self={u.id === ctx.userId} clients={clients} user={{ ...u, clientIds: u.clientAccess.map((a) => a.clientId) }} />
        ))}
      </div>
    </>
  );
}
