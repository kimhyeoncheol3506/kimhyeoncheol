import { useState } from "react";
import { fmtAmount } from "../format";

type Pt = { base_date: string; total: string; count: number; current?: boolean };

// 단일 계열 막대: 최근 결산 기준일별 합계. 범례 없음(제목이 계열을 명명), 호버 툴팁, 표 보기 별도 제공.
export function TrendChart({ data, title }: { data: Pt[]; title: string }) {
  const [hover, setHover] = useState<number | null>(null);
  if (!data.length) return <p className="muted">추이 데이터(승인된 과거 실행)가 없습니다.</p>;
  const W = 640, H = 200, padL = 8, padR = 8, padT = 12, padB = 28;
  const vals = data.map((d) => Number(d.total));
  const max = Math.max(...vals.map(Math.abs), 1);
  const bw = Math.min(36, (W - padL - padR) / data.length - 6);
  const x = (i: number) => padL + (i + 0.5) * ((W - padL - padR) / data.length);
  const y = (v: number) => padT + (H - padT - padB) * (1 - Math.max(v, 0) / max);
  const base = H - padB;
  return (
    <div className="chart" onMouseLeave={() => setHover(null)}>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={title}>
        {[0.25, 0.5, 0.75, 1].map((f) => <line key={f} x1={padL} x2={W - padR} y1={base - (base - padT) * f} y2={base - (base - padT) * f} stroke="var(--grid)" strokeWidth={1} />)}
        <line x1={padL} x2={W - padR} y1={base} y2={base} stroke="var(--border)" strokeWidth={1} />
        {data.map((d, i) => {
          const top = y(vals[i]);
          const h = Math.max(base - top, 1);
          const r = Math.min(4, bw / 2, h);
          const x0 = x(i) - bw / 2;
          const path = `M${x0},${base} V${top + r} Q${x0},${top} ${x0 + r},${top} H${x0 + bw - r} Q${x0 + bw},${top} ${x0 + bw},${top + r} V${base} Z`;
          return (
            <g key={d.base_date} onMouseEnter={() => setHover(i)}>
              <rect x={x(i) - bw / 2 - 3} y={padT} width={bw + 6} height={base - padT} fill="transparent" />
              <path d={path} fill="var(--series-1)" opacity={hover === null || hover === i ? 1 : 0.55} />
              <text x={x(i)} y={H - 10} textAnchor="middle" fontSize={11} fill="var(--muted)">{d.base_date.slice(2, 7)}{d.current ? "*" : ""}</text>
            </g>
          );
        })}
      </svg>
      {hover !== null && (
        <div className="tip" style={{ left: `${(x(hover) / W) * 100}%`, top: `${(y(vals[hover]) / H) * 100}%` }}>
          <b>{data[hover].base_date}{data[hover].current ? " (당기)" : ""}</b><br />합계 {fmtAmount(data[hover].total)} · {data[hover].count}건
        </div>
      )}
      <p className="muted small">* 당기. 음수 합계는 0 기준선 아래로 표시하지 않습니다(표 참조).</p>
    </div>
  );
}
