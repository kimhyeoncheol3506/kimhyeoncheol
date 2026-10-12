import { useRef, useState } from "react";
import { api, ApiError } from "../api";
import { Badge, Card, ErrorBox, Table, navigate, useAsync } from "../components/ui";
import { fmtBytes, fmtTime } from "../format";

type Brief = {
  id: string; name: string; ext: string; size: number; status: string; error?: string; base_date?: string;
  sheets: string[]; tables: { name: string; rows: number; columns: string[] }[]; warnings: string[]; uploaded_at?: string;
  duplicate_of?: { id: string; original_name: string }[];
};

const METHOD_LABEL: Record<string, string> = { exact: "일치", synonym: "동의어", fuzzy: "유사(확인필요)", manual: "수동지정", unmapped: "미매핑" };

export default function NewRun() {
  const [files, setFiles] = useState<Brief[]>([]);
  const [rejected, setRejected] = useState<{ name: string; error: string }[]>([]);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [plan, setPlan] = useState<any>(null);
  const [assign, setAssign] = useState<Record<string, string>>({});
  const [overrides, setOverrides] = useState<Record<string, Record<string, string>>>({});
  const [baseDate, setBaseDate] = useState("");
  const [confirm, setConfirm] = useState<any>(null);
  const [confirmReason, setConfirmReason] = useState("");
  const [dup, setDup] = useState<any>(null);
  const [rerunReason, setRerunReason] = useState("");
  const [over, setOver] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const recent = useAsync(() => api.get("/api/files"), [files.length]);

  const step = plan ? 3 : analysis ? 2 : files.length ? 1 : 0;

  async function doUpload(list: FileList | File[]) {
    const arr = Array.from(list);
    if (!arr.length) return;
    setBusy("업로드·판독 중…"); setError(null);
    try {
      const res = await api.upload(arr);
      setFiles((f) => [...f, ...res.filter((r: any) => r.ok)]);
      setRejected((r) => [...r, ...res.filter((x: any) => !x.ok)]);
      setAnalysis(null); setPlan(null);
    } catch (e) { setError(e); } finally { setBusy(""); }
  }

  async function analyze() {
    setBusy("업무 식별 중…"); setError(null); setPlan(null);
    try {
      const a = await api.post("/api/analyze", { file_ids: files.filter((f) => f.status === "PARSED").map((f) => f.id) });
      setAnalysis(a);
      if (a.plan) adoptPlan(a.plan);
    } catch (e) { setError(e); } finally { setBusy(""); }
  }

  function adoptPlan(p: any) {
    setPlan(p);
    setAssign(Object.fromEntries(Object.entries(p.roles).filter(([, v]: any) => v.file_id).map(([k, v]: any) => [k, v.file_id])));
    if (p.base_date && !baseDate) setBaseDate(p.base_date);
  }

  async function replan(key: string, version: number | null, a: Record<string, string>, ov: Record<string, Record<string, string>>, bd?: string) {
    setBusy("처리 계획 계산 중…"); setError(null);
    try {
      const p = await api.post("/api/plan", { template_key: key, version, files: a, base_date: bd || baseDate || null, overrides: ov });
      setPlan(p); setAssign(a); setOverrides(ov);
      if (p.base_date && !baseDate) setBaseDate(p.base_date);
    } catch (e) { setError(e); } finally { setBusy(""); }
  }

  async function run(extra: Record<string, any> = {}) {
    setBusy("실행·검증 중…"); setError(null);
    try {
      const r = await api.post("/api/runs", {
        template_key: plan.template_key, version: plan.version, base_date: baseDate, files: assign, overrides, ...extra,
      });
      navigate(`/runs/${r.id}`);
    } catch (e) {
      if (e instanceof ApiError && e.payload?.code === "NEEDS_CONFIRMATION") setConfirm(e.payload);
      else if (e instanceof ApiError && e.payload?.code === "DUPLICATE_RUN") setDup(e.payload);
      else setError(e);
    } finally { setBusy(""); }
  }

  async function saveDraft() {
    const reason = window.prompt("신규 업무 템플릿 초안 저장 사유를 입력하세요", "신규 업무 등록");
    if (!reason) return;
    try {
      const t = await api.post("/api/templates", { body: analysis.new_workflow.template, reason });
      navigate(`/templates/${t.template_key}`);
    } catch (e) { setError(e); }
  }

  const fileOptions = [...files, ...(recent.data || []).filter((r: Brief) => !files.some((f) => f.id === r.id))];

  return (
    <>
      <h1>결산 실행</h1>
      <p className="sub">파일 업로드 → 업무 식별·처리 계획 확인 → 실행·검증. 업로드만으로는 아무것도 실행되지 않습니다.</p>
      <div className="steps">
        {["① 파일 업로드", "② 업무 식별", "③ 계획·매핑 확인", "④ 실행"].map((s, i) => <span key={s} className={i <= step ? "on" : ""}>{s}</span>)}
      </div>
      <ErrorBox error={error} />
      {busy && <div className="alert info" aria-live="polite">{busy}</div>}

      <Card title="① 파일 업로드" right={<span className="muted small">xlsx · xlsm · csv · pdf (여러 개 동시)</span>}>
        <div className={`drop ${over ? "over" : ""}`} role="button" tabIndex={0}
          onClick={() => input.current?.click()} onKeyDown={(e) => e.key === "Enter" && input.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
          onDrop={(e) => { e.preventDefault(); setOver(false); doUpload(e.dataTransfer.files); }}>
          파일을 여기로 끌어다 놓거나 클릭해서 선택하세요
          <input ref={input} type="file" multiple hidden accept=".xlsx,.xlsm,.csv,.txt,.pdf" onChange={(e) => { const picked = Array.from(e.target.files || []); e.target.value = ""; doUpload(picked); }} />
        </div>
        {rejected.length > 0 && <div className="alert fail" style={{ marginTop: 12 }}>업로드 거부:<ul>{rejected.map((r, i) => <li key={i}>{r.name}: {r.error}</li>)}</ul></div>}
        {files.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Table rows={files} cols={[
              { key: "name", label: "파일명" }, { key: "ext", label: "형식" }, { key: "size", label: "크기", num: true, render: (r) => fmtBytes(r.size) },
              { key: "status", label: "판독", render: (r) => <><Badge s={r.status} />{r.error && <div className="small" style={{ color: "var(--fail)" }}>{r.error}</div>}</> },
              { key: "sheets", label: "시트/표", render: (r) => r.tables.map((t) => `${t.name}(${t.rows}행)`).join(", ") || r.sheets.join(", ") || "-" },
              { key: "base_date", label: "기준일(추정)" },
              { key: "warnings", label: "알림", render: (r) => <>
                {r.duplicate_of?.length ? <div className="small" style={{ color: "var(--warn)" }}>동일 파일 이전 업로드 {r.duplicate_of.length}건</div> : null}
                {r.warnings.map((w, i) => <div key={i} className="small muted">{w}</div>)}</> },
              { key: "x", label: "", render: (r) => <button className="btn sm" onClick={() => { setFiles(files.filter((f) => f.id !== r.id)); setAnalysis(null); setPlan(null); }}>제외</button> },
            ]} />
            <div className="row" style={{ marginTop: 10 }}>
              <span className="spacer" />
              <button className="btn primary" disabled={!!busy || !files.some((f) => f.status === "PARSED")} onClick={analyze}>② 업무 식별·분석</button>
            </div>
          </div>
        )}
        {recent.data?.length > 0 && (
          <details style={{ marginTop: 12 }}>
            <summary className="small">이전에 업로드한 파일에서 추가</summary>
            <Table rows={recent.data.filter((r: Brief) => !files.some((f) => f.id === r.id)).slice(0, 30)} cols={[
              { key: "name", label: "파일명" }, { key: "uploaded_at", label: "업로드", render: (r: Brief) => fmtTime(r.uploaded_at) },
              { key: "status", label: "판독", render: (r: Brief) => <Badge s={r.status} /> },
              { key: "a", label: "", render: (r: Brief) => <button className="btn sm" onClick={() => { setFiles([...files, r]); setAnalysis(null); setPlan(null); }}>추가</button> }]} />
          </details>
        )}
      </Card>

      {analysis && (
        <Card title="② 업무 식별 결과" right={<span className="muted small">로컬 규칙 기반 추정 — 확정이 아닙니다</span>}>
          <Table rows={analysis.candidates} cols={[
            { key: "name", label: "등록 업무(템플릿)" },
            { key: "score", label: "유사도", num: true, render: (r: any) => `${(r.score * 100).toFixed(0)}%` },
            { key: "evidence", label: "근거", render: (r: any) => <>{r.evidence.map((e: string, i: number) => <div key={i} className="small">{e}</div>)}
              {r.missing_roles.length > 0 && <div className="small" style={{ color: "var(--warn)" }}>누락 입력: {r.missing_roles.join(", ")}</div>}</> },
            { key: "sel", label: "", render: (r: any) => <button className="btn sm" onClick={() => replan(r.template_key, r.version,
              Object.fromEntries(Object.entries(r.assignments).map(([k, v]: any) => [k, v.file_id])), {})}>이 업무로 계획</button> },
          ]} />
          {analysis.new_workflow && (
            <div style={{ marginTop: 14 }}>
              <h3>등록된 업무와 일치하지 않음 → 신규 업무 초안</h3>
              {analysis.new_workflow.ok ? (
                <>
                  <dl className="kv">
                    <dt>추정 업무</dt><dd>{analysis.new_workflow.template.name}</dd>
                    <dt>결합 키 후보</dt><dd>{analysis.new_workflow.key_fields.map((k: string) => analysis.new_workflow.template.inputs.left.columns[k].label).join(", ")}</dd>
                    <dt>비교 금액/수량 후보</dt><dd>{analysis.new_workflow.compare_fields.map((k: string) => analysis.new_workflow.template.inputs.left.columns[k].label).join(", ") || "-"}</dd>
                  </dl>
                  <div className="alert warn" style={{ marginTop: 10 }}>불확실한 사항<ul>{analysis.new_workflow.uncertainties.map((u: string, i: number) => <li key={i}>{u}</li>)}</ul></div>
                  <details><summary className="small">초안 템플릿(JSON) 보기</summary><pre className="json">{JSON.stringify(analysis.new_workflow.template, null, 2)}</pre></details>
                  <button className="btn primary" onClick={saveDraft}>초안 템플릿으로 저장(DRAFT)</button>
                  <span className="muted small"> 저장 후 승인자가 검토·활성화해야 실행할 수 있습니다.</span>
                </>
              ) : <div className="alert warn">{analysis.new_workflow.reason}<ul>{analysis.new_workflow.uncertainties?.map((u: string, i: number) => <li key={i}>{u}</li>)}</ul></div>}
            </div>
          )}
        </Card>
      )}

      {plan && (
        <Card title={`③ 처리 계획 — ${plan.name} (v${plan.version})`}>
          <p className="muted">{plan.description}</p>
          <div className="row" style={{ marginBottom: 12 }}>
            <label htmlFor="bd"><b>결산 기준일</b></label>
            <input id="bd" type="date" value={baseDate} onChange={(e) => setBaseDate(e.target.value)} />
            <span className="muted small">파일에서 추정: {plan.base_date || "없음"}</span>
          </div>
          {plan.uncertainties.length > 0 && <div className="alert warn">확인 필요 사항<ul>{plan.uncertainties.map((u: string, i: number) => <li key={i}>{u}</li>)}</ul></div>}
          {Object.keys(plan.drift || {}).length > 0 && (
            <div className="alert fail">이전 승인 실행 대비 형식 변경 — 실행 시 사유와 함께 확인이 필요합니다
              <ul>{Object.entries(plan.drift as Record<string, any[]>).flatMap(([role, ds]) => ds.map((d: any, i: number) => <li key={role + i}>[{(plan.roles as any)[role].label}] {d.type}: {d.detail}</li>))}</ul>
            </div>
          )}
          <h3>입력 파일별 역할과 컬럼 매핑</h3>
          {Object.entries(plan.roles).map(([role, e]: any) => (
            <div key={role} className="card" style={{ background: "var(--surface-2)" }}>
              <div className="row">
                <b>{e.label}</b>{e.required ? <span className="badge s-WARNING">필수</span> : <span className="badge s-NOT_APPLICABLE">선택</span>}
                <span className="spacer" />
                <select aria-label={`${e.label} 파일`} value={assign[role] || ""} onChange={(ev) => {
                  const a = { ...assign }; if (ev.target.value) a[role] = ev.target.value; else delete a[role];
                  const ov = { ...overrides }; delete ov[role]; replan(plan.template_key, plan.version, a, ov);
                }}>
                  <option value="">(파일 없음)</option>
                  {fileOptions.filter((f) => f.status === "PARSED").map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
              {e.error && <div className="alert fail" style={{ marginTop: 8 }}>{e.error}</div>}
              {e.mapping && (
                <>
                  <p className="small muted">표: {e.table} · {e.rows}행 · 단위 표기: {e.unit?.label || "없음"} · 기준일 표기: {e.base_date || "없음"}</p>
                  <Table rows={Object.entries(e.mapping.fields).map(([f, m]: any) => ({ f, ...m }))} cols={[
                    { key: "label", label: "업무 항목", render: (r: any) => <>{r.label}{r.required && <span style={{ color: "var(--fail)" }}> *</span>}</> },
                    { key: "source", label: "원천 컬럼", render: (r: any) => (
                      <select aria-label={`${r.label} 원천 컬럼`} value={r.source || ""} onChange={(ev) => {
                        const ov: Record<string, Record<string, string>> = { ...overrides, [role]: { ...(overrides[role] || {}) } };
                        if (ev.target.value) ov[role][r.f] = ev.target.value; else delete ov[role][r.f];
                        replan(plan.template_key, plan.version, assign, ov);
                      }}>
                        <option value="">(없음)</option>
                        {e.columns.map((c: string) => <option key={c} value={c}>{c}</option>)}
                      </select>) },
                    { key: "method", label: "매핑 방법", render: (r: any) => <span className={`badge s-${r.method === "fuzzy" ? "REVIEW_REQUIRED" : r.source ? "PASS" : r.required ? "FAIL" : "NOT_APPLICABLE"}`}>{METHOD_LABEL[r.method] || r.method}</span> },
                    { key: "confidence", label: "신뢰도", num: true, render: (r: any) => r.source ? `${Math.round(r.confidence * 100)}%` : "-" },
                    { key: "type_ok_ratio", label: "형식 적합", num: true, render: (r: any) => r.type_ok_ratio == null ? "-" : `${Math.round(r.type_ok_ratio * 100)}%` },
                  ]} />
                  {e.mapping.extra_source_columns.length > 0 && <p className="small muted">사용하지 않는 원천 컬럼: {e.mapping.extra_source_columns.join(", ")}</p>}
                </>
              )}
            </div>
          ))}
          <div className="grid g2">
            <div>
              <h3>자동화 절차</h3>
              <ol className="plan">{plan.steps.map((s: string, i: number) => <li key={i}>{s}</li>)}</ol>
            </div>
            <div>
              <h3>계산 규칙</h3>
              {plan.rules.length ? plan.rules.map((r: any) => (
                <div key={r.rule_id} style={{ marginBottom: 8 }}>
                  <b>{r.rule_id}</b> v{r.version} <Badge s={r.approval_status === "APPROVED" ? "APPROVED" : "DRAFT"} /> <span className="small muted">{r.approval_status}</span>
                  <div className="mono">{r.expression} {r.params && Object.keys(r.params).length ? JSON.stringify(r.params) : ""}</div>
                  <div className="small muted">{r.basis}</div>
                </div>)) : <p className="muted">계산 규칙 없음(대사·검증 업무)</p>}
              <h3>예상 산출물</h3>
              <p className="small">{plan.outputs.join(" · ")} + 확정 후 업로드 파일(CSV/XLSX)</p>
              {plan.confirm_items.length > 0 && <><h3>실제 적용 전 확인 사항</h3><ul className="small">{plan.confirm_items.map((c: string) => <li key={c}>{c}</li>)}</ul></>}
            </div>
          </div>

          {confirm && (
            <div className="alert fail">
              <b>{confirm.detail}</b>
              <ul>{Object.entries(confirm.drift || {}).flatMap(([role, ds]: any) => ds.map((d: any, i: number) => <li key={role + i}>{role}: {d.type} — {d.detail}</li>))}</ul>
              <textarea rows={2} placeholder="변경 내용을 확인한 사유 (감사 기록에 남습니다)" value={confirmReason} onChange={(e) => setConfirmReason(e.target.value)} />
              <button className="btn danger" disabled={confirmReason.trim().length < 2} onClick={() => { setConfirm(null); run({ confirm_changes: true, confirm_reason: confirmReason }); }}>변경 확인 후 실행</button>
            </div>
          )}
          {dup && (
            <div className="alert warn">
              <b>{dup.detail}</b>
              <ul>{dup.runs.map((r: any) => <li key={r.id}><a href={`#/runs/${r.id}`}>{r.id}</a> ({r.status})</li>)}</ul>
              <textarea rows={2} placeholder="재실행 사유" value={rerunReason} onChange={(e) => setRerunReason(e.target.value)} />
              <button className="btn" disabled={rerunReason.trim().length < 2} onClick={() => { setDup(null); run({ rerun_reason: rerunReason }); }}>사유 입력 후 재실행</button>
            </div>
          )}
          <div className="row">
            <span className="muted small">실행하면 계산·검증·증감 분석과 검토용 Excel이 생성됩니다. 업로드 파일은 승인 후 확정 단계에서만 생성됩니다.</span>
            <span className="spacer" />
            <button className="btn primary" disabled={!!busy || !baseDate} onClick={() => run()}>④ 실행·검증</button>
          </div>
        </Card>
      )}
    </>
  );
}
