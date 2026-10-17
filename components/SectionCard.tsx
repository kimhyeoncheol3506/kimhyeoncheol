import type { Section } from "@/lib/reading/types";

/** 풀이 한 장 (표 항목이 있으면 카드형으로) */
export default function SectionCard({ s }: { s: Section }) {
  const [lead, ...rest] = s.body;
  return (
    <div className="card">
      <h2 className={`text-title font-bold ${s.id === "caution" ? "text-warn" : ""}`}>{s.title}</h2>
      {s.items?.length ? (
        <>
          <p className="mt-2 text-[15px] leading-[1.6] text-mute">{lead}</p>
          <div className="mt-4 space-y-3">
            {s.items.map((it, i) => (
              <div key={i} className="rounded-2xl bg-smoke px-4 py-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[16px] font-bold text-ink">{it.label}</p>
                  {it.badge && <span className="shrink-0 text-[14px] tracking-[1px] text-accent">{it.badge}</span>}
                </div>
                {it.title && <p className="mt-1 text-[16px] font-medium leading-[1.6] text-sub">{it.title}</p>}
                {it.rows.length > 0 && (
                  <dl className="mt-3 space-y-2 border-t border-line pt-3">
                    {it.rows.map((r, j) => (
                      <div key={j} className="flex gap-3 text-[15px] leading-[1.6]">
                        <dt className={`w-[76px] shrink-0 font-semibold ${r.k.includes("조심") || r.k === "주의" ? "text-warn" : "text-mute"}`}>{r.k}</dt>
                        <dd className="text-sub">{r.v}</dd>
                      </div>
                    ))}
                  </dl>
                )}
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="mt-3 space-y-3">
          {[lead, ...rest].map((p, i) => (
            <p key={i} className="text-[17px] leading-[1.7] text-sub">
              {p}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
