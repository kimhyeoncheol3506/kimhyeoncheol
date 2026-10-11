"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FacelessClass, Settings, Weights } from "@/lib/types";

const W_LABELS: Record<keyof Weights, string> = {
  velocity: "게시 후 경과 시간 대비 조회 속도",
  relative: "채널 내 유사 경과 시간 영상 대비 성과",
  subRatio: "구독자 대비 조회수",
  likeRate: "좋아요율",
  commentRate: "댓글률",
  faceless: "페이스리스 재현 적합성 (최종 결합에만 사용)",
};

interface ChannelOpt {
  id: string;
  title: string;
}

async function post(url: string, body: unknown) {
  const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error ?? `HTTP ${r.status}`);
  return j;
}

export function CollectButton({ apiKey }: { apiKey: boolean }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  return (
    <div>
      <button
        disabled={!apiKey || busy}
        onClick={async () => {
          setBusy(true);
          setMsg("수집 중… 채널 수에 따라 1~3분 걸릴 수 있습니다.");
          try {
            const j = await post("/api/collect", {});
            setMsg(`완료: ${j.run.status} · 영상 ${j.run.videosCollected}개 · 사용 할당량 약 ${j.run.quotaUsed}단위`);
            router.refresh();
          } catch (e) {
            setMsg(`실패: ${(e as Error).message}`);
          } finally {
            setBusy(false);
          }
        }}
        className="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40"
      >
        {busy ? "수집 중…" : "지금 데이터 수집 실행"}
      </button>
      {!apiKey && <p className="mt-2 text-sm text-neutral-500">API 키가 없어 비활성화되었습니다.</p>}
      {msg && <p className="mt-2 text-sm">{msg}</p>}
    </div>
  );
}

export function SettingsForm({ settings }: { settings: Settings }) {
  const router = useRouter();
  const [w, setW] = useState(settings.weights);
  const [period, setPeriod] = useState(settings.periodDays);
  const [peer, setPeer] = useState(settings.peerWindowDays);
  const [mode, setMode] = useState(settings.dataMode);
  const [msg, setMsg] = useState("");
  const viralSum = w.velocity + w.relative + w.subRatio + w.likeRate + w.commentRate;

  async function save(extra: Record<string, unknown> = {}) {
    try {
      const j = await post("/api/settings", { weights: w, periodDays: period, peerWindowDays: peer, dataMode: mode, ...extra });
      if (extra.resetWeights) setW(j.settings.weights);
      setMsg(j.errors?.length ? j.errors.join(" ") : "저장했습니다.");
      router.refresh();
    } catch (e) {
      setMsg((e as Error).message);
    }
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {(Object.keys(W_LABELS) as (keyof Weights)[]).map((k) => (
          <label key={k} className="grid grid-cols-[1fr,160px,48px] items-center gap-3 text-sm">
            <span>{W_LABELS[k]}</span>
            <input type="range" min={0} max={50} value={w[k]} onChange={(e) => setW({ ...w, [k]: Number(e.target.value) })} />
            <input type="number" min={0} max={100} value={w[k]} onChange={(e) => setW({ ...w, [k]: Number(e.target.value) })} className="rounded border border-neutral-300 px-1 py-0.5 text-right" />
          </label>
        ))}
        <p className="text-xs text-neutral-500">
          바이럴 지표 합 {viralSum} · 페이스리스 {w.faceless} → 최종 결합 비율 바이럴 {((viralSum / (viralSum + w.faceless || 1)) * 100).toFixed(0)}% : 페이스리스{" "}
          {((w.faceless / (viralSum + w.faceless || 1)) * 100).toFixed(0)}%. 가중치는 합이 100이 아니어도 비율로 환산됩니다.
        </p>
      </div>
      <div className="flex flex-wrap gap-4 text-sm">
        <label>분석 기간 <input type="number" min={1} max={60} value={period} onChange={(e) => setPeriod(Number(e.target.value))} className="w-16 rounded border border-neutral-300 px-1 py-0.5" />일</label>
        <label>채널 내 비교 기간 <input type="number" min={14} max={365} value={peer} onChange={(e) => setPeer(Number(e.target.value))} className="w-16 rounded border border-neutral-300 px-1 py-0.5" />일</label>
        <label>
          데이터 모드{" "}
          <select value={mode} onChange={(e) => setMode(e.target.value as Settings["dataMode"])} className="rounded border border-neutral-300 px-1 py-0.5">
            <option value="auto">자동 (실제 데이터 있으면 실제)</option>
            <option value="demo">데모 데이터 보기</option>
            <option value="real">실제 데이터만</option>
          </select>
        </label>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={() => save()} className="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-semibold text-white">저장</button>
        <button onClick={() => save({ resetWeights: true })} className="rounded-lg px-4 py-2 text-sm ring-1 ring-neutral-300">초기 가중치로</button>
        <span className="text-sm text-neutral-600">{msg}</span>
      </div>
    </div>
  );
}

export function Top3Form({ settings, channels, slot3 }: { settings: Settings; channels: ChannelOpt[]; slot3: ChannelOpt[] }) {
  const router = useRouter();
  const [p, setP] = useState<string[]>([settings.pinnedTop3[0] ?? "", settings.pinnedTop3[1] ?? "", settings.pinnedTop3[2] ?? ""]);
  const [msg, setMsg] = useState("");
  const opts = [...channels];
  for (const s of slot3) if (!opts.some((o) => o.id === s.id)) opts.push(s);
  return (
    <div className="space-y-2 text-sm">
      {[0, 1, 2].map((i) => (
        <label key={i} className="flex items-center gap-2">
          <span className="w-24">대상 {i + 1}{i === 2 ? " (애니메이션)" : ""}</span>
          <select value={p[i]} onChange={(e) => setP(p.map((x, j) => (j === i ? e.target.value : x)))} className="flex-1 rounded border border-neutral-300 px-2 py-1">
            <option value="">— 미지정 —</option>
            {(i === 2 ? [...slot3, ...opts.filter((o) => !slot3.some((s) => s.id === o.id))] : opts).map((o) => (
              <option key={o.id} value={o.id}>{o.title} ({o.id})</option>
            ))}
          </select>
        </label>
      ))}
      <div className="flex items-center gap-2">
        <button
          onClick={async () => {
            try {
              await post("/api/settings", { pinnedTop3: p.filter(Boolean) });
              setMsg("저장했습니다.");
              router.refresh();
            } catch (e) {
              setMsg((e as Error).message);
            }
          }}
          className="rounded-lg bg-neutral-900 px-4 py-2 font-semibold text-white"
        >
          분석 대상 저장
        </button>
        <span className="text-neutral-600">{msg}</span>
      </div>
    </div>
  );
}

export function FacelessForm({ channels, overrides }: { channels: ChannelOpt[]; overrides: Settings["facelessOverrides"] }) {
  const router = useRouter();
  const [id, setId] = useState(channels[0]?.id ?? "");
  const [cls, setCls] = useState<FacelessClass>("A");
  const [confirmed, setConfirmed] = useState(false);
  const [note, setNote] = useState("");
  const [msg, setMsg] = useState("");
  return (
    <div className="space-y-2 text-sm">
      <div className="flex flex-wrap gap-2">
        <select value={id} onChange={(e) => setId(e.target.value)} className="rounded border border-neutral-300 px-2 py-1">
          {channels.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
        </select>
        <select value={cls} onChange={(e) => setCls(e.target.value as FacelessClass)} className="rounded border border-neutral-300 px-2 py-1">
          {(["A", "B", "C", "D", "E", "U"] as FacelessClass[]).map((c) => <option key={c}>{c}</option>)}
        </select>
        <label className="flex items-center gap-1"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} /> 영상을 직접 확인함(확정)</label>
      </div>
      <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="근거 메모 (예: 최근 영상 5개 확인, 모두 내레이션+자료 화면)" className="w-full rounded border border-neutral-300 px-2 py-1" />
      <div className="flex items-center gap-2">
        <button
          onClick={async () => {
            try {
              await post("/api/settings", { facelessOverride: { channelId: id, cls, confirmed, note } });
              setMsg("저장했습니다. 다음 수집부터 영상별 판정에도 반영됩니다.");
              router.refresh();
            } catch (e) {
              setMsg((e as Error).message);
            }
          }}
          className="rounded-lg bg-neutral-900 px-4 py-2 font-semibold text-white"
        >
          판정 저장
        </button>
        <span className="text-neutral-600">{msg}</span>
      </div>
      {Object.keys(overrides).length > 0 && (
        <ul className="mt-2 space-y-1 text-xs">
          {Object.entries(overrides).map(([cid, o]) => (
            <li key={cid} className="flex items-center gap-2">
              <span>{channels.find((c) => c.id === cid)?.title ?? cid}: {o.cls} {o.confirmed ? "(확정)" : "(추정)"} — {o.note}</span>
              <button
                className="underline"
                onClick={async () => {
                  await post("/api/settings", { facelessOverride: { channelId: cid, remove: true } });
                  router.refresh();
                }}
              >
                삭제
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function ChannelSearch({ apiKey }: { apiKey: boolean }) {
  const router = useRouter();
  const [q, setQ] = useState("경제 애니메이션");
  const [add, setAdd] = useState("");
  const [res, setRes] = useState<{ id: string; title: string; description: string }[]>([]);
  const [msg, setMsg] = useState("");
  return (
    <fieldset disabled={!apiKey} className="space-y-3 text-sm disabled:opacity-50">
      <div className="flex gap-2">
        <input value={add} onChange={(e) => setAdd(e.target.value)} placeholder="@핸들 또는 채널 ID(UC…) 또는 채널 URL" className="flex-1 rounded border border-neutral-300 px-2 py-1" />
        <button
          onClick={async () => {
            try {
              const j = await post("/api/settings", { addChannel: add });
              setMsg(`추가됨: ${j.added.title} (${j.added.id}). 다음 수집에 포함됩니다.`);
              router.refresh();
            } catch (e) {
              setMsg((e as Error).message);
            }
          }}
          className="rounded-lg px-3 py-1 ring-1 ring-neutral-300"
        >
          수집 대상에 추가 (1단위)
        </button>
      </div>
      <div className="flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} className="flex-1 rounded border border-neutral-300 px-2 py-1" />
        <button
          onClick={async () => {
            try {
              const j = await post("/api/search-channels", { q });
              setRes(j.results);
              setMsg(j.note);
            } catch (e) {
              setMsg((e as Error).message);
            }
          }}
          className="rounded-lg px-3 py-1 ring-1 ring-neutral-300"
        >
          교체 후보 검색 (100단위)
        </button>
      </div>
      {msg && <p className="text-neutral-600">{msg}</p>}
      {res.length > 0 && (
        <ul className="divide-y rounded border">
          {res.map((r) => (
            <li key={r.id} className="flex items-start justify-between gap-2 p-2">
              <div>
                <a href={`https://www.youtube.com/channel/${r.id}`} target="_blank" rel="noreferrer" className="font-medium underline">{r.title}</a>
                <div className="font-mono text-xs text-neutral-400">{r.id}</div>
                <div className="text-xs text-neutral-500">{r.description.slice(0, 120)}</div>
              </div>
              <button onClick={() => setAdd(r.id)} className="shrink-0 rounded px-2 py-0.5 text-xs ring-1 ring-neutral-300">선택</button>
            </li>
          ))}
        </ul>
      )}
    </fieldset>
  );
}
