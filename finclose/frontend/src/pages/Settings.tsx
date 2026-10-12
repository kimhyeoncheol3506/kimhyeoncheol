import { useEffect, useState } from "react";
import { api } from "../api";
import { Card, ErrorBox, useAsync } from "../components/ui";

const FIELDS: [string, string, string][] = [
  ["abs_amount", "절대 증감 기준(원)", "이 금액 이상 증감 시 이상 후보"],
  ["pct", "증감률 기준(비율)", "0.1 = 10%"],
  ["share_pp", "구성비 변화 기준(비율)", "0.05 = 5%p"],
  ["qty_pct", "수량 변동 기준(비율)", "금액 유사·수량 급변 탐지"],
];

export default function SettingsPage() {
  const { data, error, reload } = useAsync(() => api.get("/api/settings/materiality"), []);
  const health = useAsync(() => api.get("/api/health"), []);
  const [form, setForm] = useState<Record<string, string>>({});
  const [msg, setMsg] = useState<any>(null);
  const [err, setErr] = useState<any>(null);
  useEffect(() => { if (data) setForm(data); }, [data]);
  if (error) return <ErrorBox error={error} />;
  return (
    <>
      <h1>설정</h1>
      <p className="sub">회사의 중요성 기준은 시스템이 임의로 정하지 않습니다. 아래 기본값은 예시이며 관리자가 회사 기준으로 등록해야 합니다.</p>
      <ErrorBox error={err} />
      {msg && <div className="alert ok">{msg}</div>}
      <Card title="이상 증감 탐지 기준 (관리자)">
        <div className="grid g2">
          {FIELDS.map(([k, label, hint]) => (
            <label key={k}><div><b>{label}</b> <span className="small muted">{hint}</span></div>
              <input type="text" inputMode="decimal" value={form[k] ?? ""} onChange={(e) => setForm({ ...form, [k]: e.target.value })} style={{ width: "100%" }} /></label>))}
        </div>
        <button className="btn primary" style={{ marginTop: 12 }} onClick={async () => {
          setErr(null); setMsg(null);
          try { await api.put("/api/settings/materiality", form); setMsg("저장했습니다(감사 로그 기록)."); reload(); } catch (e) { setErr(e); }
        }}>저장</button>
      </Card>
      <Card title="시스템 정보">
        {health.data && <dl className="kv">
          <dt>버전</dt><dd>{health.data.version}</dd><dt>인증</dt><dd>미구현 — 데모용 사용자 전환(운영 사용 비권장)</dd>
          <dt>외부 전송</dt><dd>없음(로컬 처리)</dd><dt>데이터 위치</dt><dd className="mono">{health.data.data_dir}</dd></dl>}
        <h3>앱으로 설치(PWA)</h3>
        <p className="small">PC: 크롬/엣지 주소창 오른쪽의 설치 아이콘 또는 상단 "앱으로 설치". 모바일: 브라우저 메뉴 → "홈 화면에 추가".
          설치형 앱은 <b>localhost 또는 HTTPS</b> 주소에서만 활성화됩니다(브라우저 보안 정책). 앱은 화면만 캐시하며 결산 데이터는 저장하지 않습니다.</p>
      </Card>
    </>
  );
}
