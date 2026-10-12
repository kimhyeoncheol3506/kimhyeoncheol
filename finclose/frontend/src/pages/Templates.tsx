import { useEffect, useState } from "react";
import { api } from "../api";
import { Badge, Card, ErrorBox, Table, navigate, useAsync } from "../components/ui";
import { fmtTime } from "../format";

export default function Templates({ focus }: { focus?: string }) {
  const { data, error, reload } = useAsync(() => api.get("/api/templates"), []);
  const loadErr = error;
  const [selKey, setSelKey] = useState<string | undefined>(focus);
  const [selVer, setSelVer] = useState<number | null>(null);
  const [text, setText] = useState("");
  const [reason, setReason] = useState("");
  const [msg, setMsg] = useState<any>(null);
  const [err, setErr] = useState<any>(null);
  const [test, setTest] = useState<any>(null);

  useEffect(() => { if (focus) setSelKey(focus); }, [focus]);
  const list: any[] = data || [];
  const keys = [...new Set(list.map((t) => t.template_key))];
  const versions = list.filter((t) => t.template_key === selKey);
  const cur = versions.find((t) => t.version === selVer) || versions[0];
  useEffect(() => { if (cur) { setText(JSON.stringify(cur.body, null, 2)); setTest(null); } }, [cur?.template_key, cur?.version]);

  async function wrap(f: () => Promise<any>, ok: string) {
    setErr(null); setMsg(null);
    try { await f(); setMsg(ok); reload(); } catch (e) { setErr(e); }
  }
  function parsed() { return JSON.parse(text); }

  return (
    <>
      <h1>업무 템플릿</h1>
      <p className="sub">입력·매핑·계산 규칙·검증·출력 양식을 사람이 읽을 수 있는 JSON으로 관리합니다. 수정은 항상 새 버전(DRAFT)으로 저장되며 이전 버전은 삭제되지 않습니다.</p>
      <ErrorBox error={err || loadErr} />
      {msg && <div className="alert ok">{msg}</div>}
      <div className="grid split wide-right">
        <Card title="업무 목록">
          <Table rows={keys.map((k) => { const vs = list.filter((t) => t.template_key === k); const act = vs.find((t) => t.status === "ACTIVE");
            return { k, name: vs[0].name, versions: vs.length, active: act?.version }; })}
            onRow={(r: any) => { setSelKey(r.k); setSelVer(null); navigate(`/templates/${r.k}`); }} selected={(r: any) => r.k === selKey}
            cols={[{ key: "name", label: "업무", render: (r: any) => <>{r.name}<div className="mono muted">{r.k}</div></> },
              { key: "active", label: "활성 버전", render: (r: any) => r.active ? `v${r.active}` : <span className="muted">없음</span> },
              { key: "versions", label: "버전 수", num: true }]} />
        </Card>
        {cur ? (
          <Card title={`${cur.name}`} right={<select aria-label="버전" value={cur.version} onChange={(e) => setSelVer(Number(e.target.value))}>
            {versions.map((v) => <option key={v.version} value={v.version}>v{v.version} — {v.status}</option>)}</select>}>
            <div className="row"><Badge s={cur.status} /><span className="small muted">작성 {cur.created_by} · {fmtTime(cur.created_at)} · 사유: {cur.change_reason}</span></div>
            <p className="small">규칙 테스트: {cur.test_result?.ok ? <Badge s="PASS" /> : <Badge s="FAIL" />} {cur.test_result?.results?.length ?? 0}건</p>
            {cur.test_result && !cur.test_result.ok && <ul className="small">{cur.test_result.results.filter((r: any) => !r.ok).map((r: any, i: number) => <li key={i}>{r.rule_id} #{r.case}: {r.error || r.detail}</li>)}</ul>}
            <label className="small muted" htmlFor="tjson">템플릿 정의(JSON) — 수정 후 새 버전으로 저장</label>
            <textarea id="tjson" className="mono" rows={22} value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} />
            <div className="row" style={{ marginTop: 8 }}>
              <button className="btn" onClick={async () => { setErr(null); try { setTest(await api.post("/api/templates/test", parsed())); } catch (e) { setErr(e); } }}>검증·규칙 테스트 실행</button>
              <input type="text" placeholder="변경 사유(필수)" value={reason} onChange={(e) => setReason(e.target.value)} style={{ flex: 1, minWidth: 160 }} />
              <button className="btn primary" disabled={reason.trim().length < 2} onClick={() => wrap(() => api.post("/api/templates", { body: parsed(), reason }), "새 버전(DRAFT)을 저장했습니다. 승인자가 활성화해야 사용됩니다.")}>새 버전 저장</button>
            </div>
            {test && <div className={`alert ${test.ok ? "ok" : "fail"}`} style={{ marginTop: 8 }}>{test.ok ? "정의 검증·규칙 테스트 통과" : "실패"}
              <ul>{test.errors.map((e: string, i: number) => <li key={i}>{e}</li>)}{test.tests.results.filter((r: any) => !r.ok).map((r: any, i: number) => <li key={"t" + i}>{r.rule_id} #{r.case}: {r.error || r.detail}</li>)}</ul></div>}
            <div className="row" style={{ marginTop: 12 }}>
              <button className="btn" disabled={cur.status === "ACTIVE"} onClick={() => { const r = prompt("활성화 사유"); if (r) wrap(() => api.post(`/api/templates/${cur.template_key}/${cur.version}/status`, { status: "ACTIVE", reason: r }), "활성화했습니다(규칙 테스트 재실행 통과)."); }}>이 버전 활성화(승인자)</button>
              <button className="btn" disabled={cur.status === "INACTIVE"} onClick={() => { const r = prompt("비활성화 사유"); if (r) wrap(() => api.post(`/api/templates/${cur.template_key}/${cur.version}/status`, { status: "INACTIVE", reason: r }), "비활성화했습니다."); }}>비활성화</button>
              <button className="btn" onClick={() => { const k = prompt("새 템플릿 키(영문 대문자/숫자/_)", `${cur.template_key}_COPY`); const n = k && prompt("새 업무명", `${cur.name} (복제)`);
                if (k && n) wrap(() => api.post(`/api/templates/${cur.template_key}/${cur.version}/clone`, { new_key: k, new_name: n }).then((t) => { setSelKey(t.template_key); }), "복제했습니다(DRAFT, 승인상태 초기화)."); }}>복제</button>
            </div>
            <p className="small muted">담당자는 규칙의 approval_status를 APPROVED로 올릴 수 없습니다(승인자 권한). 활성화 시 모든 규칙 테스트가 다시 실행됩니다.</p>
          </Card>
        ) : <Card><p className="muted">왼쪽에서 업무를 선택하세요.</p></Card>}
      </div>
    </>
  );
}
