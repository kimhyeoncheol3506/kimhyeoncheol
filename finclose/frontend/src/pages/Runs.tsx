import { useState } from "react";
import { api } from "../api";
import { Badge, Card, ErrorBox, Table, navigate, useAsync } from "../components/ui";
import { fmtTime, STATUS_LABEL } from "../format";

export default function Runs() {
  const { data, error } = useAsync(() => api.get("/api/runs"), []);
  const [st, setSt] = useState("");
  const [tpl, setTpl] = useState("");
  if (error) return <ErrorBox error={error} />;
  const rows = (data || []).filter((r: any) => (!st || r.status === st) && (!tpl || r.template_key === tpl));
  const tpls = [...new Set((data || []).map((r: any) => r.template_key))] as string[];
  return (
    <>
      <h1>실행 이력</h1>
      <p className="sub">모든 실행은 삭제되지 않고 보존됩니다. 검증 결과가 바뀌면 새 실행으로 기록됩니다.</p>
      <Card right={<div className="row">
        <select aria-label="상태" value={st} onChange={(e) => setSt(e.target.value)}><option value="">상태 전체</option>
          {["READY_FOR_REVIEW", "BLOCKED", "REVIEWED", "APPROVED", "FINALIZED", "REJECTED", "FAILED"].map((s) => <option key={s} value={s}>{STATUS_LABEL[s]}</option>)}</select>
        <select aria-label="업무" value={tpl} onChange={(e) => setTpl(e.target.value)}><option value="">업무 전체</option>{tpls.map((t) => <option key={t}>{t}</option>)}</select>
      </div>} title={`${rows.length}건`}>
        <Table rows={rows} onRow={(r: any) => navigate(`/runs/${r.id}`)} cols={[
          { key: "id", label: "실행 ID", render: (r: any) => <span className="mono">{r.id}</span> },
          { key: "created_at", label: "실행 시각", render: (r: any) => fmtTime(r.created_at) },
          { key: "base_date", label: "기준일" },
          { key: "template_name", label: "업무", render: (r: any) => <>{r.template_name}<div className="small muted">v{r.template_version}</div></> },
          { key: "input_files", label: "입력 파일", render: (r: any) => <span className="small">{Object.values(r.input_files || {}).map((f: any) => f.name).join(", ")}</span> },
          { key: "status", label: "상태", render: (r: any) => <Badge s={r.status} /> },
          { key: "cs", label: "실패/경고/검토/미수행", render: (r: any) => r.check_summary ? `${r.check_summary.FAIL}/${r.check_summary.WARNING}/${r.check_summary.REVIEW_REQUIRED}/${r.check_summary.NOT_RUN}` : (r.error ? <span className="small" style={{ color: "var(--fail)" }}>{r.error.slice(0, 60)}</span> : "-") },
          { key: "created_by", label: "실행자" },
        ]} />
      </Card>
    </>
  );
}
