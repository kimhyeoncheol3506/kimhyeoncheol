import { Fragment, useMemo, useState } from "react";
import { api, getIdentity } from "../api";
import { Badge, Card, ErrorBox, Table, fmtCell, useAsync } from "../components/ui";
import { TrendChart } from "../components/TrendChart";
import { fmtAmount, fmtRate, fmtTime, STATUS_LABEL } from "../format";

const TABS = ["검증", "요약", "증감 분석", "예외", "처리 데이터", "대사", "분개 초안", "입력·매핑", "승인·감사", "다운로드"];
const DETAIL_COLS = ["role", "file", "table", "source_row", "key", "column", "source_value", "computed", "compared", "difference",
  "formula", "rate_status", "reason", "cause_candidates", "period", "currency", "rule_id", "status", "type", "detail"];
const COL_LABEL: Record<string, string> = {
  role: "입력", file: "파일", table: "시트/표", source_row: "원천 위치", key: "키", column: "컬럼", source_value: "원천값",
  computed: "계산값", compared: "비교값", difference: "차이", formula: "검증식", rate_status: "증감상태", reason: "사유",
  cause_candidates: "원인 후보(추정)", period: "비교기간", currency: "통화", rule_id: "규칙", status: "상태", type: "유형", detail: "내용",
};
const AMOUNT_KEYS = new Set(["computed", "compared", "difference"]);

export default function RunDetail({ id }: { id: string }) {
  const { data: run, error, loading, reload } = useAsync(() => api.get(`/api/runs/${encodeURIComponent(id)}`), [id]);
  const audit = useAsync(() => api.get(`/api/audit?entity_id=${encodeURIComponent(id)}`), [id, run?.status, run?.approvals?.length]);
  const [tab, setTab] = useState("검증");
  const [fStatus, setFStatus] = useState("NON_PASS");
  const [fSev, setFSev] = useState("");
  const [fCat, setFCat] = useState("");
  const [sel, setSel] = useState<string | null>(null);
  const [comment, setComment] = useState("");
  const [actErr, setActErr] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const role = getIdentity().role;

  const checks = run?.checks || [];
  const filtered = useMemo(() => checks.filter((c: any) =>
    (fStatus === "" || (fStatus === "NON_PASS" ? !["PASS", "NOT_APPLICABLE"].includes(c.status) : c.status === fStatus)) &&
    (!fSev || c.severity === fSev) && (!fCat || c.category === fCat)), [checks, fStatus, fSev, fCat]);

  if (error) return <ErrorBox error={error} />;
  if (loading || !run) return <p className="muted">불러오는 중…</p>;

  const acked = new Set(run.approvals.filter((a: any) => a.action === "ACKNOWLEDGE").map((a: any) => a.check_id));
  const excepted = new Set(run.approvals.filter((a: any) => a.action === "EXCEPTION").map((a: any) => a.check_id));
  const selCheck = checks.find((c: any) => c.check_id === sel);

  async function act(action: string, check_id?: string) {
    setBusy(true); setActErr(null);
    try {
      if (action === "FINALIZE") await api.post(`/api/runs/${encodeURIComponent(id)}/finalize`, { comment });
      else await api.post(`/api/runs/${encodeURIComponent(id)}/actions`, { action, check_id, comment });
      setComment(""); reload();
    } catch (e) { setActErr(e); } finally { setBusy(false); }
  }
  const can = (roles: string[]) => roles.includes(role);
  const g = run.gate;
  const closed = ["FINALIZED", "REJECTED", "FAILED", "RUNNING"].includes(run.status);

  return (
    <>
      <div className="row">
        <h1>{run.template_name}</h1><Badge s={run.status} />
        <span className="spacer" /><a href="#/runs">← 실행 이력</a>
      </div>
      <p className="sub">
        기준일 <b>{run.base_date}</b> · 실행 <span className="mono">{run.id}</span> · {run.template_key} v{run.template_version} ·
        {" "}{run.created_by} · {fmtTime(run.created_at)}{run.rerun_reason ? ` · 재실행 사유: ${run.rerun_reason}` : ""}
      </p>
      {run.status === "FAILED" && <div className="alert fail">처리 실패: {run.error}<br />원본 파일과 기존 결과는 변경되지 않았습니다.</div>}

      {g && (
        <>
          {run.status === "FINALIZED" ? (
            <div className="alert ok">확정 완료 — 업로드 파일 생성됨 ({run.finalized?.check}). 원장·외부 시스템에는 반영하지 않았습니다.</div>
          ) : g.blockers.length ? (
            <div className="alert fail"><b>업로드 확정 차단 사유 {g.blockers.length}건</b>
              <ul>{g.blockers.map((b: any, i: number) => <li key={i}>{b.check_id ? <a href="#" onClick={(e) => { e.preventDefault(); setTab("검증"); setSel(b.check_id); }}>{b.check_id}</a> : null} {b.reason}</li>)}</ul></div>
          ) : null}
          {!closed && g.pending_reviews.length > 0 && (
            <div className="alert warn"><b>사람의 확인이 필요한 항목 {g.pending_reviews.length}건</b>
              <ul>{g.pending_reviews.map((b: any) => <li key={b.check_id}><a href="#" onClick={(e) => { e.preventDefault(); setTab("검증"); setSel(b.check_id); }}>{b.check_id}</a> {b.reason}</li>)}</ul></div>
          )}
        </>
      )}

      {!closed && g && (
        <Card title="검토·승인">
          <ErrorBox error={actErr} />
          <textarea rows={2} placeholder="의견/사유 (모든 작업에 필수 · 감사 기록에 남습니다)" value={comment} onChange={(e) => setComment(e.target.value)} />
          <div className="row" style={{ marginTop: 8 }}>
            {can(["admin", "reviewer", "approver"]) && <button className="btn" disabled={busy || comment.trim().length < 2} onClick={() => act("REVIEW")}>검토 완료</button>}
            {can(["admin", "approver"]) && <button className="btn primary" disabled={busy || comment.trim().length < 2 || !g.can_approve} onClick={() => act("APPROVE")} title={g.can_approve ? "" : "검토 완료 + 차단사유·확인필요 항목 해소 필요"}>승인</button>}
            {can(["admin", "approver"]) && <button className="btn primary" disabled={busy || comment.trim().length < 2 || !g.can_finalize} onClick={() => act("FINALIZE")} title={g.can_finalize ? "" : "승인 후 확정 가능"}>확정·업로드 파일 생성</button>}
            {can(["admin", "approver"]) && <button className="btn danger" disabled={busy || comment.trim().length < 2} onClick={() => act("REJECT")}>반려</button>}
            <span className="spacer" />
            <span className="muted small">진행: 검토 완료 → 승인 → 확정. 실행자 본인은 검토·승인할 수 없습니다.</span>
          </div>
        </Card>
      )}

      {run.check_summary && (
        <div className="row" style={{ marginBottom: 12 }}>
          {Object.entries(run.check_summary.by_status).map(([s, n]: any) => n > 0 && (
            <button key={s} className="btn sm" onClick={() => { setTab("검증"); setFStatus(s); }}><Badge s={s} /> {n}</button>))}
        </div>
      )}

      <div className="tabs" role="tablist">{TABS.map((t) => <button key={t} role="tab" aria-selected={tab === t} className={tab === t ? "on" : ""} onClick={() => setTab(t)}>{t}</button>)}</div>

      {tab === "검증" && (
        <div className="grid split">
          <Card title="검증 결과" right={
            <div className="row">
              <select aria-label="상태" value={fStatus} onChange={(e) => setFStatus(e.target.value)}>
                <option value="NON_PASS">통과·해당없음 제외</option><option value="">전체</option>
                {["PASS", "WARNING", "FAIL", "REVIEW_REQUIRED", "NOT_APPLICABLE", "NOT_RUN"].map((s) => <option key={s} value={s}>{STATUS_LABEL[s]}</option>)}
              </select>
              <select aria-label="심각도" value={fSev} onChange={(e) => setFSev(e.target.value)}>
                <option value="">심각도 전체</option>{["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((s) => <option key={s}>{s}</option>)}
              </select>
              <select aria-label="범주" value={fCat} onChange={(e) => setFCat(e.target.value)}>
                <option value="">범주 전체</option>{[...new Set(checks.map((c: any) => c.category))].map((s: any) => <option key={s}>{s}</option>)}
              </select>
            </div>}>
            <Table rows={filtered} onRow={(r: any) => setSel(r.check_id)} selected={(r: any) => r.check_id === sel} empty="조건에 맞는 검증이 없습니다."
              cols={[
                { key: "check_id", label: "ID", render: (r: any) => <b>{r.check_id}</b> },
                { key: "name", label: "검증", render: (r: any) => <>{r.name}<div className="small muted">{r.category}{r.mandatory ? " · 필수" : ""}</div></> },
                { key: "status", label: "상태", render: (r: any) => <>
                  <Badge s={r.status} />
                  {acked.has(r.check_id) && <div className="small" style={{ color: "var(--ok)" }}>확인됨</div>}
                  {excepted.has(r.check_id) && <div className="small" style={{ color: "var(--review)" }}>예외승인</div>}</> },
                { key: "severity", label: "심각도", render: (r: any) => <span className="sev">{r.severity}</span> },
              ]} />
          </Card>
          <Card title={selCheck ? `${selCheck.check_id} ${selCheck.name}` : "항목을 선택하세요"}>
            {selCheck ? (
              <>
                <div className="row"><Badge s={selCheck.status} /><span className="sev">{selCheck.severity}</span>{selCheck.mandatory && <span className="small muted">필수 검증</span>}</div>
                <p>{selCheck.message}</p>
                {selCheck.method && <p className="small muted">검증 방법: <span className="mono">{selCheck.method}</span></p>}
                {!closed && selCheck.status === "REVIEW_REQUIRED" && !acked.has(selCheck.check_id) && can(["admin", "reviewer", "approver"]) &&
                  <button className="btn" disabled={busy || comment.trim().length < 2} onClick={() => act("ACKNOWLEDGE", selCheck.check_id)}>확인 처리(위 의견란에 근거 입력)</button>}
                {!closed && selCheck.status === "FAIL" && selCheck.severity !== "CRITICAL" && !excepted.has(selCheck.check_id) && can(["admin", "approver"]) &&
                  <button className="btn danger" disabled={busy || comment.trim().length < 2} onClick={() => act("EXCEPTION", selCheck.check_id)}>예외 승인(원래 결과는 보존)</button>}
                {selCheck.status === "FAIL" && selCheck.severity === "CRITICAL" && <p className="small" style={{ color: "var(--fail)" }}>CRITICAL 실패는 예외승인할 수 없습니다. 원천 자료를 수정해 재실행하세요.</p>}
                {(!g || g.blockers.length || g.pending_reviews.length) && comment.trim().length < 2 && !closed ? <p className="small muted">확인/예외승인하려면 상단 의견란에 사유를 입력하세요.</p> : null}
                {run.approvals.filter((a: any) => a.check_id === selCheck.check_id).map((a: any) => (
                  <div key={a.id} className="alert info small">{a.action} · {a.actor}({a.role}) · {fmtTime(a.at)}<br />{a.comment}</div>))}
                {selCheck.details?.length > 0 && (
                  <>
                    <h3>상세 {selCheck.details.length}건{selCheck.details_truncated ? ` (+${selCheck.details_truncated}건 생략 — Excel 참조)` : ""}</h3>
                    <Table rows={selCheck.details} cols={DETAIL_COLS.filter((k) => selCheck.details.some((d: any) => d[k] !== undefined && d[k] !== null))
                      .concat(Object.keys(selCheck.details[0]).filter((k) => !DETAIL_COLS.includes(k)))
                      .map((k) => ({ key: k, label: COL_LABEL[k] || k, num: AMOUNT_KEYS.has(k), render: AMOUNT_KEYS.has(k) ? (r: any) => fmtAmount(r[k]) : undefined }))} />
                  </>
                )}
              </>
            ) : <p className="muted">왼쪽에서 검증 항목을 클릭하면 원천 파일·행·컬럼·원천값·계산값·비교값·검증식·사유를 볼 수 있습니다.</p>}
          </Card>
        </div>
      )}

      {tab === "요약" && <Summary run={run} />}
      {tab === "증감 분석" && <Variance run={run} />}
      {tab === "예외" && (
        <Card title={`처리 제외 행 ${run.exceptions?.length || 0}건`}>
          <Table rows={run.exceptions || []} empty="예외 없음" cols={[
            { key: "_src", label: "원천 위치" }, { key: "code", label: "코드" }, { key: "name", label: "명칭" },
            { key: "currency", label: "통화" }, { key: "reason", label: "사유" }]} />
        </Card>
      )}
      {tab === "처리 데이터" && <Card title={`처리 결과 ${run.processed_total}행`}><DynTable rows={run.processed} /></Card>}
      {tab === "대사" && <Card title="대사 결과"><DynTable rows={run.reconciliation || []} /></Card>}
      {tab === "분개 초안" && (
        <Card title="분개 초안 (DRAFT · 원장 미반영)">
          <div className="alert warn">분개 계정이 예시(가상)이거나 정책 미승인일 수 있습니다. 원장 반영은 이 시스템의 기능이 아닙니다.</div>
          <DynTable rows={run.journal || []} />
        </Card>
      )}
      {tab === "입력·매핑" && (
        <>
          {run.confirmed_changes && <div className="alert warn">형식 변경 확인됨 — {run.confirmed_changes.by}: {run.confirmed_changes.reason}</div>}
          {Object.entries(run.inputs || {}).map(([role, i]: any) => (
            <Card key={role} title={`${i.label} (${role})`}>
              <dl className="kv"><dt>파일</dt><dd>{i.file || "미제출"}</dd><dt>SHA-256</dt><dd className="mono">{i.sha256 || "-"}</dd>
                <dt>표</dt><dd>{i.table || "-"} · {i.rows}행</dd><dt>기준일 표기</dt><dd>{i.base_date_detected || "-"}</dd></dl>
              {i.mapping && <Table rows={Object.entries(i.mapping.fields).map(([f, m]: any) => ({ f, ...m }))} cols={[
                { key: "label", label: "항목" }, { key: "source", label: "원천 컬럼" }, { key: "method", label: "방법" },
                { key: "confidence", label: "신뢰도", num: true }]} />}
              {i.drift?.length > 0 && <div className="alert warn" style={{ marginTop: 8 }}>형식 변경<ul>{i.drift.map((d: any, k: number) => <li key={k}>{d.type}: {d.detail}</li>)}</ul></div>}
            </Card>
          ))}
        </>
      )}
      {tab === "승인·감사" && (
        <>
          <Card title="승인 이력">
            <Table rows={run.approvals} empty="승인 이력 없음" cols={[
              { key: "at", label: "시각", render: (r: any) => fmtTime(r.at) }, { key: "action", label: "작업" }, { key: "check_id", label: "검증" },
              { key: "actor", label: "수행자" }, { key: "role", label: "역할" }, { key: "comment", label: "의견" }]} />
          </Card>
          <Card title="감사 로그(이 실행)">
            <Table rows={audit.data || []} cols={[
              { key: "id", label: "#" }, { key: "at", label: "시각", render: (r: any) => fmtTime(r.at) }, { key: "actor", label: "수행자" },
              { key: "action", label: "작업" }, { key: "details_json", label: "내용", render: (r: any) => <span className="mono">{r.details_json.slice(0, 300)}</span> }]} />
          </Card>
        </>
      )}
      {tab === "다운로드" && (
        <Card title="산출물">
          <ul>{(run.downloads || []).map((n: string) => <li key={n}><a href={api.fileUrl(run.id, n)} target="_blank" rel="noreferrer">{n}</a>
            <span className="small muted"> — {n.startsWith("upload_") ? "확정 업로드 파일(표준 형식)" : n === "final.xlsx" ? "확정 결과 Excel" : n === "review.xlsx" ? "검토용 Excel(미확정)" : "검토 보고서"}</span></li>)}</ul>
          {run.status !== "FINALIZED" && <p className="muted small">업로드 파일은 승인 후 확정 단계에서만 생성됩니다.</p>}
          {run.finalized && <pre className="json">{JSON.stringify(run.finalized, null, 2)}</pre>}
        </Card>
      )}
    </>
  );
}

function DynTable({ rows }: { rows: any[] }) {
  if (!rows?.length) return <p className="muted">데이터 없음</p>;
  const keys: string[] = [];
  rows.slice(0, 50).forEach((r) => Object.keys(r).forEach((k) => { if (!keys.includes(k) && !(k.startsWith("_") && k !== "_src")) keys.push(k); }));
  return <Table rows={rows} cols={keys.map((k) => ({ key: k, label: k, render: (r: any) => (/^-?\d+(\.\d+)?$/.test(String(r[k] ?? "")) && k !== "line_no" ? <span className="num">{fmtAmount(r[k])}</span> : fmtCell(r[k])) }))} />;
}

function Summary({ run }: { run: any }) {
  const s = run.summary || {};
  return (
    <div className="grid g2">
      <Card title="처리 요약">
        <dl className="kv">
          {[["원천 건수", s.source_count], ["처리 건수", s.processed_count], ["예외 건수", s.exception_count], ["미매칭", s.unmatched_count],
            ["단가 건수", s.price_count], ["전월 결과 건수", s.prior_count], ["전표 수", s.voucher_count], ["차변 합계", s.total_debit && fmtAmount(s.total_debit)],
            ["대변 합계", s.total_credit && fmtAmount(s.total_credit)], ["일치", s.matched], ["차이", s.different], ["좌측 단독", s.left_only], ["우측 단독", s.right_only]]
            .filter(([, v]) => v !== undefined && v !== null).map(([k, v]) => <Fragment key={k as string}><dt>{k}</dt><dd>{String(v)}</dd></Fragment>)}
          <dt>결과 해시</dt><dd className="mono">{run.result_hash}</dd>
        </dl>
      </Card>
      {s.totals_by_currency && (
        <Card title="통화별 합계">
          <Table rows={Object.entries(s.totals_by_currency).map(([c, t]: any) => ({ c, ...t }))} cols={[
            { key: "c", label: "통화" }, { key: "count", label: "건수", num: true },
            { key: "book_amount_source", label: "원천 장부금액", num: true, render: (r: any) => fmtAmount(r.book_amount_source) },
            { key: "eval_amount", label: "평가금액", num: true, render: (r: any) => fmtAmount(r.eval_amount) },
            { key: "valuation_gain", label: "평가손익", num: true, render: (r: any) => fmtAmount(r.valuation_gain) }]} />
        </Card>
      )}
      <Card title="규칙 버전">
        <Table rows={run.rule_versions || []} empty="계산 규칙 없음" cols={[{ key: "rule_id", label: "규칙" }, { key: "version", label: "버전" }, { key: "approval_status", label: "승인상태" }]} />
      </Card>
      {run.confirm_items?.length > 0 && <Card title="실제 적용 전 확인 사항"><ul>{run.confirm_items.map((c: string) => <li key={c}>{c}</li>)}</ul></Card>}
    </div>
  );
}

function Variance({ run }: { run: any }) {
  const periods = run.variance?.periods || {};
  const codes = Object.keys(periods);
  const [code, setCode] = useState(codes.find((c) => periods[c].result) || codes[0]);
  const [onlyAnom, setOnlyAnom] = useState(true);
  const v = periods[code];
  const trend = run.variance?.trend || [];
  return (
    <>
      <Card title="기간 비교" right={<select aria-label="비교 기간" value={code} onChange={(e) => setCode(e.target.value)}>
        {codes.map((c) => <option key={c} value={c}>{periods[c].label} ({periods[c].base_date}){periods[c].result ? "" : " — 미수행"}</option>)}</select>}>
        {!v ? <p className="muted">비교 정보 없음</p> : !v.result ? <div className="alert warn">미수행: {v.not_run_reason}</div> : (
          <>
            <div className="grid g4">
              <div className="kpi"><div className="l">당기 합계</div><div className="v">{fmtAmount(v.result.total.current)}</div></div>
              <div className="kpi"><div className="l">비교 합계 ({v.base_date})</div><div className="v">{fmtAmount(v.result.total.base)}</div></div>
              <div className="kpi"><div className="l">증감</div><div className="v">{fmtAmount(v.result.total.delta)}</div></div>
              <div className="kpi"><div className="l">증감률 · 이상 후보</div><div className="v">{fmtRate(v.result.total.rate, v.result.total.rate_status)} · {v.result.anomaly_count}</div></div>
            </div>
            <p className="small muted">출처: {v.source} · 건수 {v.result.total.base_count} → {v.result.total.current_count} · 기준: 절대 {fmtAmount(v.result.thresholds.abs_amount)}, 비율 {Number(v.result.thresholds.pct) * 100}%. 이상 후보는 오류 단정이 아니며 원인은 추정입니다.</p>
            <label className="small"><input type="checkbox" checked={onlyAnom} onChange={(e) => setOnlyAnom(e.target.checked)} /> 이상 후보만</label>
            <Table rows={v.result.rows.filter((r: any) => !onlyAnom || r.anomaly)} cols={[
              { key: "key", label: "항목" }, { key: "label", label: "명칭" },
              { key: "current", label: "당기", num: true, render: (r: any) => fmtAmount(r.current) },
              { key: "base", label: "비교", num: true, render: (r: any) => fmtAmount(r.base) },
              { key: "delta", label: "증감", num: true, render: (r: any) => fmtAmount(r.delta) },
              { key: "rate", label: "증감률", num: true, render: (r: any) => fmtRate(r.rate, r.rate_status) },
              { key: "share_change", label: "구성비 변화", num: true, render: (r: any) => r.share_change == null ? "-" : `${(Number(r.share_change) * 100).toFixed(2)}%p` },
              { key: "flags", label: "이상 신호", render: (r: any) => r.flags.join(", ") || "-" },
              { key: "cause_candidates", label: "원인 후보(미확인)", render: (r: any) => <span className="small">{r.cause_candidates.join(" ")}</span> },
            ]} />
          </>
        )}
      </Card>
      <Card title="최근 추이 — 결산 기준일별 합계">
        <TrendChart data={trend} title="결산 기준일별 합계 추이" />
        <Table rows={trend} cols={[{ key: "base_date", label: "기준일" }, { key: "total", label: "합계", num: true, render: (r: any) => fmtAmount(r.total) },
          { key: "count", label: "건수", num: true }, { key: "run_id", label: "실행", render: (r: any) => <a href={`#/runs/${r.run_id}`} className="mono">{r.run_id}</a> }]} />
      </Card>
    </>
  );
}
