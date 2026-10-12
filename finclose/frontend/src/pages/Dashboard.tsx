import { api } from "../api";
import { Badge, Card, ErrorBox, Table, navigate, useAsync } from "../components/ui";
import { fmtTime } from "../format";

export default function Dashboard() {
  const { data, error, loading } = useAsync(() => api.get("/api/dashboard"), []);
  if (error) return <ErrorBox error={error} />;
  if (loading || !data) return <p className="muted">불러오는 중…</p>;
  const s = data.by_status || {};
  const inProgress = (s.READY_FOR_REVIEW || 0) + (s.BLOCKED || 0) + (s.REVIEWED || 0) + (s.APPROVED || 0);
  return (
    <>
      <h1>대시보드</h1>
      <p className="sub">결산 업무 진행 현황 · 검증 결과 · 검토 대기</p>
      {!data.audit.ok && <div className="alert fail">감사 로그 무결성 검증 실패(레코드 {data.audit.broken_at_id}) — 관리자에게 즉시 보고하세요.</div>}
      <div className="grid g4">
        <div className="card kpi"><div className="l">진행 중(검토·승인 대기)</div><div className="v">{inProgress}</div></div>
        <div className="card kpi"><div className="l">검증 차단</div><div className="v" style={{ color: "var(--fail)" }}>{s.BLOCKED || 0}</div></div>
        <div className="card kpi"><div className="l">확정 완료</div><div className="v">{s.FINALIZED || 0}</div></div>
        <div className="card kpi"><div className="l">처리 완료율(확정/유효 실행)</div><div className="v">{data.completion_rate == null ? "-" : `${(data.completion_rate * 100).toFixed(0)}%`}</div></div>
      </div>
      <div className="grid g2">
        <Card title="검토·승인 대기" right={<a href="#/runs">전체 보기</a>}>
          <Table rows={data.pending} onRow={(r: any) => navigate(`/runs/${r.id}`)} empty="대기 중인 실행이 없습니다." cols={[
            { key: "base_date", label: "기준일" }, { key: "template_name", label: "업무" },
            { key: "status", label: "상태", render: (r: any) => <Badge s={r.status} /> }, { key: "created_by", label: "실행자" }]} />
        </Card>
        <Card title="최근 자주 실패한 검증(최근 50회)">
          <Table rows={data.top_failures.map(([k, v]: [string, number]) => ({ k, v }))} empty="실패한 검증이 없습니다."
            cols={[{ key: "k", label: "검증" }, { key: "v", label: "횟수", num: true }]} />
        </Card>
      </div>
      <Card title="반복 업무별 자동화 현황" right={<span className="muted small">활성 템플릿 {data.active_templates} / 등록 업무 {data.template_count}</span>}>
        <Table rows={data.per_template} empty="실행 이력이 없습니다. '결산 실행'에서 시작하세요." cols={[
          { key: "name", label: "업무" }, { key: "runs", label: "실행", num: true }, { key: "finalized", label: "확정", num: true },
          { key: "last_run", label: "최근 실행", render: (r: any) => fmtTime(r.last_run) },
          { key: "last_status", label: "최근 상태", render: (r: any) => <Badge s={r.last_status} /> }]} />
      </Card>
      <Card title="최근 실행">
        <Table rows={data.recent} onRow={(r: any) => navigate(`/runs/${r.id}`)} cols={[
          { key: "id", label: "실행 ID", render: (r: any) => <span className="mono">{r.id}</span> },
          { key: "base_date", label: "기준일" }, { key: "template_name", label: "업무" },
          { key: "status", label: "상태", render: (r: any) => <Badge s={r.status} /> },
          { key: "checks", label: "검증(실패/경고/검토)", render: (r: any) => r.check_summary ? `${r.check_summary.FAIL}/${r.check_summary.WARNING}/${r.check_summary.REVIEW_REQUIRED}` : "-" },
          { key: "created_at", label: "실행 시각", render: (r: any) => fmtTime(r.created_at) }]} />
      </Card>
      <p className="muted small">감사 로그 해시 체인: {data.audit.ok ? `정상 (${data.audit.count}건)` : "손상"}</p>
    </>
  );
}
