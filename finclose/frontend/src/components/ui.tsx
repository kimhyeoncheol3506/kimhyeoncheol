import { ReactNode, useEffect, useState } from "react";
import { STATUS_ICON, STATUS_LABEL } from "../format";

export function Badge({ s }: { s: string }) {
  return <span className={`badge s-${s}`}>{STATUS_ICON[s] ? <span aria-hidden>{STATUS_ICON[s]}</span> : null}{STATUS_LABEL[s] ?? s}</span>;
}

export function ErrorBox({ error }: { error: any }) {
  if (!error) return null;
  return <div className="alert fail" role="alert">{String(error.message || error)}</div>;
}

export function Card({ title, right, children }: { title?: ReactNode; right?: ReactNode; children: ReactNode }) {
  return (
    <section className="card">
      {(title || right) && <div className="row" style={{ marginBottom: 10 }}><h2 style={{ margin: 0 }}>{title}</h2><span className="spacer" />{right}</div>}
      {children}
    </section>
  );
}

export type Col<T> = { key: string; label: string; num?: boolean; render?: (r: T) => ReactNode };

export function Table<T extends Record<string, any>>({ cols, rows, onRow, selected, empty = "데이터가 없습니다.", max = 500 }:
  { cols: Col<T>[]; rows: T[]; onRow?: (r: T) => void; selected?: (r: T) => boolean; empty?: string; max?: number }) {
  if (!rows?.length) return <p className="muted">{empty}</p>;
  return (
    <div className="tbl-wrap" style={{ maxHeight: 560 }}>
      <table className="tbl">
        <thead><tr>{cols.map((c) => <th key={c.key} className={c.num ? "num" : ""}>{c.label}</th>)}</tr></thead>
        <tbody>
          {rows.slice(0, max).map((r, i) => (
            <tr key={i} className={`${onRow ? "click" : ""} ${selected?.(r) ? "sel" : ""}`} onClick={() => onRow?.(r)}
              tabIndex={onRow ? 0 : undefined} onKeyDown={(e) => { if (onRow && e.key === "Enter") onRow(r); }}>
              {cols.map((c) => <td key={c.key} className={c.num ? "num" : ""}>{c.render ? c.render(r) : fmtCell(r[c.key])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > max && <p className="muted small" style={{ padding: 8 }}>상위 {max}행만 표시 — 전체는 Excel 결과 파일에서 확인하세요 (총 {rows.length}행).</p>}
    </div>
  );
}

export function fmtCell(v: any): ReactNode {
  if (v === null || v === undefined || v === "") return <span className="muted">-</span>;
  if (Array.isArray(v)) return v.map((x) => (typeof x === "object" ? JSON.stringify(x) : String(x))).join(", ");
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]): { data: T | null; error: any; loading: boolean; reload: () => void } {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [n, setN] = useState(0);
  useEffect(() => {
    let alive = true;
    setLoading(true);
    fn().then((d) => { if (alive) { setData(d); setError(null); } }).catch((e) => alive && setError(e)).finally(() => alive && setLoading(false));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, n]);
  return { data, error, loading, reload: () => setN((x) => x + 1) };
}

export function navigate(path: string) {
  window.location.hash = path;
}
