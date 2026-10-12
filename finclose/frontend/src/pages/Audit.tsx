import { useState } from "react";
import { api } from "../api";
import { Card, ErrorBox, Table, useAsync } from "../components/ui";
import { fmtTime } from "../format";

export default function AuditPage() {
  const { data, error } = useAsync(() => api.get("/api/audit?limit=500"), []);
  const [v, setV] = useState<any>(null);
  const [q, setQ] = useState("");
  if (error) return <ErrorBox error={error} />;
  const rows = (data || []).filter((r: any) => !q || JSON.stringify(r).includes(q));
  return (
    <>
      <h1>감사 로그</h1>
      <p className="sub">누가·언제·무엇을·어떤 자료와 규칙으로 했는지 기록합니다. 각 기록은 이전 기록의 해시를 포함해 변조를 탐지합니다.</p>
      <Card right={<div className="row"><input type="text" placeholder="검색" value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn" onClick={async () => setV(await api.get("/api/audit/verify"))}>무결성 검증</button></div>} title={`최근 ${rows.length}건`}>
        {v && <div className={`alert ${v.ok ? "ok" : "fail"}`}>{v.ok ? `해시 체인 정상 (${v.count}건)` : `변조 탐지: 레코드 #${v.broken_at_id}`}</div>}
        <Table rows={rows} cols={[
          { key: "id", label: "#", num: true }, { key: "at", label: "시각", render: (r: any) => fmtTime(r.at) },
          { key: "actor", label: "수행자", render: (r: any) => `${r.actor} (${r.role})` }, { key: "action", label: "작업" },
          { key: "entity_id", label: "대상", render: (r: any) => r.entity_type === "run" ? <a href={`#/runs/${r.entity_id}`} className="mono">{r.entity_id}</a> : <span className="mono">{r.entity_id}</span> },
          { key: "details_json", label: "내용", render: (r: any) => <span className="mono">{r.details_json.slice(0, 240)}</span> },
          { key: "hash", label: "해시", render: (r: any) => <span className="mono">{r.hash.slice(0, 10)}…</span> },
        ]} />
      </Card>
    </>
  );
}
