import { useEffect, useState } from "react";
import { getIdentity, ROLE_LABELS, Role, setIdentity } from "./api";
import Dashboard from "./pages/Dashboard";
import NewRun from "./pages/NewRun";
import Runs from "./pages/Runs";
import RunDetail from "./pages/RunDetail";
import Templates from "./pages/Templates";
import AuditPage from "./pages/Audit";
import SettingsPage from "./pages/Settings";
import { openFolder, quitApp, startHeartbeat, useDesktop } from "./desktop";

const NAV = [
  { path: "/", label: "대시보드", icon: "▦" },
  { path: "/new", label: "결산 실행", icon: "＋" },
  { path: "/runs", label: "실행 이력", icon: "≡" },
  { path: "/templates", label: "업무 템플릿", icon: "▤" },
  { path: "/audit", label: "감사 로그", icon: "⛬" },
  { path: "/settings", label: "설정", icon: "⚙" },
];

function useHash() {
  const [h, setH] = useState(window.location.hash.slice(1) || "/");
  useEffect(() => {
    const f = () => { setH(window.location.hash.slice(1) || "/"); window.scrollTo(0, 0); };
    window.addEventListener("hashchange", f);
    return () => window.removeEventListener("hashchange", f);
  }, []);
  return h;
}

export default function App() {
  const path = useHash();
  const [id, setId] = useState(getIdentity());
  const [installEvt, setInstallEvt] = useState<any>(null);
  useEffect(() => {
    const f = (e: Event) => { e.preventDefault(); setInstallEvt(e); };
    window.addEventListener("beforeinstallprompt", f);
    return () => window.removeEventListener("beforeinstallprompt", f);
  }, []);
  const desktop = useDesktop();
  const [closed, setClosed] = useState(false);
  useEffect(() => {
    if (!desktop) return;
    const t = startHeartbeat();
    return () => window.clearInterval(t);
  }, [desktop]);
  async function quit() {
    try { await quitApp(); } catch { /* 이미 꺼진 경우 */ }
    setClosed(true);
    window.setTimeout(() => window.close(), 300);
  }
  if (closed) {
    return <div className="content"><div className="card" style={{ maxWidth: 520, margin: "15vh auto" }}>
      <h1>FinClose를 종료했습니다</h1><p className="sub">이 창을 닫아도 됩니다. 다시 쓰려면 바탕화면의 FinClose 아이콘을 실행하세요.</p></div></div>;
  }
  const update = (user: string, role: Role) => { setIdentity(user, role); setId({ user, role }); };
  const seg = path.split("/").filter(Boolean);
  let page;
  if (seg[0] === "new") page = <NewRun />;
  else if (seg[0] === "runs" && seg[1]) page = <RunDetail id={decodeURIComponent(seg[1])} key={`${seg[1]}-${id.user}-${id.role}`} />;
  else if (seg[0] === "runs") page = <Runs />;
  else if (seg[0] === "templates") page = <Templates focus={seg[1] ? decodeURIComponent(seg[1]) : undefined} />;
  else if (seg[0] === "audit") page = <AuditPage />;
  else if (seg[0] === "settings") page = <SettingsPage />;
  else page = <Dashboard />;
  const active = (p: string) => (p === "/" ? path === "/" : path.startsWith(p));
  return (
    <div className="app">
      <aside className="side">
        <div className="logo"><img src="/icon.svg" alt="" />FinClose AI</div>
        <nav className="nav">{NAV.map((n) => <a key={n.path} href={`#${n.path}`} className={active(n.path) ? "on" : ""}><span aria-hidden>{n.icon}</span>{n.label}</a>)}</nav>
        <p className="muted small" style={{ margin: "24px 8px 0" }}>로컬 처리 · 외부 전송 없음<br />원장 반영 기능 없음(업로드 파일만 생성)</p>
        {desktop && (
          <div style={{ margin: "16px 6px 0", display: "grid", gap: 6 }}>
            <button className="btn sm" onClick={() => openFolder("practice")}>연습용 파일 폴더 열기</button>
            <button className="btn sm" onClick={() => openFolder("home")}>FinClose 폴더 열기</button>
            <button className="btn sm danger" onClick={quit}>FinClose 종료</button>
          </div>
        )}
      </aside>
      <div className="main">
        <header className="top">
          <strong className="mobile-only" style={{ display: "none" }}>FinClose</strong>
          <div className="who">
            <label className="small muted" htmlFor="user">사용자</label>
            <input id="user" type="text" value={id.user} style={{ width: 110 }} onChange={(e) => update(e.target.value, id.role)} />
            <select aria-label="역할" value={id.role} onChange={(e) => update(id.user, e.target.value as Role)}>
              {(Object.keys(ROLE_LABELS) as Role[]).map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
            </select>
            <span className="demo-note" title="MVP는 인증이 없습니다. 운영 사용 전 SSO 연동 필요.">데모용 사용자 전환 · 인증 아님</span>
          </div>
          {desktop?.mode === "practice" && <span className="badge s-REVIEW_REQUIRED" title={desktop.data_dir}>연습 모드 · 실제 업무 데이터와 분리됨</span>}
          {desktop && <button className="btn sm danger mobile-quit" onClick={quit}>종료</button>}
          {!desktop && installEvt && <button className="btn sm" onClick={() => { installEvt.prompt(); setInstallEvt(null); }}>앱으로 설치</button>}
        </header>
        <main className="content">{page}</main>
      </div>
      <nav className="mobile-nav">
        {NAV.slice(0, 5).map((n) => <a key={n.path} href={`#${n.path}`} className={active(n.path) ? "on" : ""}><span aria-hidden>{n.icon}</span>{n.label}</a>)}
      </nav>
    </div>
  );
}
