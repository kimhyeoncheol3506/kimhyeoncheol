"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

const SERIES = ["var(--series-1)", "var(--series-2)", "var(--series-3)"];
const axisProps = { stroke: "var(--axis)", fontSize: 12, tickLine: false };

/** 영상 1개의 스냅샷별 조회수 (실제 관측점만, 보간·역산 없음) */
export function SnapshotChart({ points }: { points: { label: string; ageH: number; views: number }[] }) {
  if (points.length < 2)
    return <p className="text-sm text-neutral-500">스냅샷이 {points.length}개뿐이라 추이를 그리지 않습니다. 같은 영상을 다른 시각에 다시 수집하면 표시됩니다.</p>;
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={points} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke="var(--grid)" vertical={false} />
          <XAxis dataKey="ageH" type="number" {...axisProps} tickFormatter={(h) => `${Math.round(h / 24)}일`} domain={["dataMin", "dataMax"]} />
          <YAxis {...axisProps} tickFormatter={(v) => (v >= 10000 ? `${(v / 10000).toFixed(0)}만` : String(v))} width={48} />
          <Tooltip
            formatter={(v: number) => [v.toLocaleString("ko-KR"), "조회수"]}
            labelFormatter={(h: number) => `게시 후 ${(h / 24).toFixed(1)}일`}
          />
          <Line type="monotone" dataKey="views" stroke="var(--series-1)" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 길이(분) × 바이럴 점수, 채널별 색 (최대 3개 채널) */
export function DurationScatter({ series }: { series: { name: string; points: { x: number; y: number; title: string }[] }[] }) {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 8, right: 16, left: 8, bottom: 16 }}>
          <CartesianGrid stroke="var(--grid)" />
          <XAxis dataKey="x" type="number" name="길이" unit="분" {...axisProps} />
          <YAxis dataKey="y" type="number" name="바이럴 점수" domain={[0, 100]} {...axisProps} width={36} />
          <ZAxis range={[110, 110]} />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={({ payload }) => {
              const p = payload?.[0]?.payload as { x: number; y: number; title: string } | undefined;
              if (!p) return null;
              return (
                <div className="max-w-xs rounded-md border border-neutral-200 bg-white p-2 text-xs shadow">
                  <div className="font-semibold">{p.title}</div>
                  <div>길이 {p.x.toFixed(1)}분 · 바이럴 {p.y.toFixed(1)}</div>
                </div>
              );
            }}
          />
          <Legend />
          {series.slice(0, 3).map((s, i) => (
            <Scatter key={s.name} name={s.name} data={s.points} fill={SERIES[i]} stroke="#fff" strokeWidth={2} isAnimationActive={false} />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 단일 계열 가로 막대 */
export function HBar({ data, unit = "" }: { data: { name: string; value: number }[]; unit?: string }) {
  return (
    <div className="w-full" style={{ height: Math.max(120, data.length * 34 + 30) }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
          <CartesianGrid stroke="var(--grid)" horizontal={false} />
          <XAxis type="number" {...axisProps} />
          <YAxis type="category" dataKey="name" width={150} {...axisProps} />
          <Tooltip formatter={(v: number) => [`${v.toFixed(1)}${unit}`, "값"]} />
          <Bar dataKey="value" fill="var(--series-1)" radius={[0, 4, 4, 0]} barSize={16} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
