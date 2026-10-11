import Link from "next/link";
import { Badge, Card, ClassBadge, PageTitle, ScoreBar, SourceBadge, Thumb } from "@/components/ui";
import { CANDIDATES, SLOT3, VERIFIED_AT, candidateById } from "@/lib/candidates";
import { getDataset, type Dataset } from "@/lib/dataset";
import { compact, pct } from "@/lib/format";
import type { CandidateChannel } from "@/lib/types";

export const dynamic = "force-dynamic";

function thumbFor(ds: Dataset, channelId: string | null): string | null {
  if (!channelId || ds.source === "demo") return null;
  const vids = ds.recent.filter((v) => v.channelId === channelId && v.thumbnailUrl);
  const best = vids.sort((a, b) => (ds.scoreMap.get(b.id)?.finalScore ?? -1) - (ds.scoreMap.get(a.id)?.finalScore ?? -1))[0];
  return best?.thumbnailUrl ?? ds.channelMap.get(channelId)?.thumbnailUrl ?? null;
}

export default function ChannelsPage() {
  const ds = getDataset();
  const pinned = ds.source === "real" ? ds.settings.pinnedTop3 : [];
  const slot3Id = pinned.find((id) => SLOT3.candidateIds.includes(id) && !candidateById(id)?.userPick) ?? null;

  // 카드 순서: 사용자 선정 2개 → 3번째 슬롯 → 나머지 최종 선정·보류 후보
  const picks = ["firstecon", "pilot"].map((k) => CANDIDATES.find((c) => c.key === k)!);
  const rest = CANDIDATES.filter((c) => !c.userPick && c.decision !== "excluded" && c.channelId !== slot3Id);
  const slotCand = slot3Id ? candidateById(slot3Id) : undefined;
  const cards: (CandidateChannel | "slot3")[] = [...picks, slotCand ?? ("slot3" as const), ...rest].slice(0, 10);

  return (
    <>
      <PageTitle title="채널 탐색" desc="채널은 이름이 아니라 채널 ID로 식별합니다. 동명·사칭 채널이 다수 존재합니다." />

      <Card title="페이스리스 후보 채널 10개" right={<span className="text-xs text-neutral-500">채널 ID 확인: {VERIFIED_AT} YouTube 공개 검색</span>}>
        <ul className="divide-y divide-neutral-100">
          {cards.map((c, i) => {
            if (c === "slot3")
              return (
                <li key="slot3" className="flex gap-4 py-4">
                  <div className="w-32 shrink-0 sm:w-36"><Thumb url={null} alt="" label="채널 미확정" /></div>
                  <div className="min-w-0">
                    <div className="font-bold">{i + 1}. {SLOT3.label}</div>
                    <div className="mt-1 flex flex-wrap gap-1"><Badge tone="green">우선 분석 후보</Badge><Badge tone="gray">채널명 확정 필요</Badge></div>
                    <p className="mt-1 text-sm leading-relaxed text-neutral-700">{SLOT3.description}</p>
                    <p className="mt-1 text-xs text-neutral-500">
                      검증 후보: {SLOT3.candidateIds.map((id) => candidateById(id)?.name).join(" · ")} → <Link href="/settings#top3" className="underline">설정에서 지정</Link>
                    </p>
                  </div>
                </li>
              );
            const cv = ds.source === "real" && c.channelId ? ds.channelViews.find((x) => x.channel.id === c.channelId) : undefined;
            const isSlot3 = c.channelId === slot3Id;
            return (
              <li key={c.key} className="flex gap-4 py-4">
                <div className="w-32 shrink-0 sm:w-36"><Thumb url={thumbFor(ds, c.channelId)} alt={c.name} label={c.name} /></div>
                <div className="min-w-0">
                  <div className="font-bold">
                    {i + 1}. {c.name}
                    {isSlot3 && <span className="ml-1 text-sm font-normal text-neutral-500">({SLOT3.label})</span>}
                  </div>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {(c.userPick || isSlot3) && <Badge tone="green">우선 분석 후보</Badge>}
                    {!c.userPick && !isSlot3 && c.decision === "pending" && <Badge tone="gray">확인 필요</Badge>}
                    {c.list === "replacement" && <Badge tone="violet">교체 후보</Badge>}
                    <ClassBadge cls={cv?.channel.faceless.cls ?? c.priorClass} confidence={cv?.channel.faceless.confidence ?? (c.priorClass === "U" ? "unverified" : "estimated")} />
                  </div>
                  <p className="mt-1 text-sm leading-relaxed text-neutral-700">{c.description}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-neutral-500">
                    {c.url && (
                      <a href={c.url} target="_blank" rel="noreferrer" className="rounded-full bg-neutral-100 px-2 py-0.5 hover:bg-neutral-200">
                        ▶ 유튜브 {c.handle}
                      </a>
                    )}
                    <span className="font-mono">{c.channelId}</span>
                    <span>{c.verifiedNote}</span>
                    {cv && <span>· 실제 구독자 {compact(cv.channel.subscriberCount)} · 최근 영상 {cv.recent.length}개</span>}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </Card>

      <Card title={<span className="flex items-center gap-2">수집 채널 현황 <SourceBadge source={ds.source} /></span>} className="mt-6">
        <div className="overflow-x-auto">
          <table className="tbl">
            <thead>
              <tr>
                <th>채널</th>
                <th>페이스리스 분류</th>
                <th className="num">구독자</th>
                <th className="num">최근 영상</th>
                <th className="num">평균 조회수</th>
                <th className="num">중앙 조회수</th>
                <th className="num">페이스리스 비중</th>
                <th>바이럴(중앙값)</th>
                <th>최종(중앙값)</th>
                <th>벤치마킹</th>
              </tr>
            </thead>
            <tbody>
              {[...ds.channelViews]
                .sort((a, b) => (b.score.medianFinal ?? -1) - (a.score.medianFinal ?? -1))
                .map((cv) => (
                  <tr key={cv.channel.id}>
                    <td>
                      <Link href={`/channels/${cv.channel.id}`} className="font-medium hover:underline">{cv.channel.title}</Link>
                      <div className="font-mono text-xs text-neutral-400">{cv.channel.id}</div>
                    </td>
                    <td><ClassBadge cls={cv.channel.faceless.cls} confidence={cv.channel.faceless.confidence} /></td>
                    <td className="num">{cv.channel.subscriberCount == null ? <span className="text-neutral-400">비공개</span> : compact(cv.channel.subscriberCount)}</td>
                    <td className="num">{cv.recent.length}</td>
                    <td className="num">{compact(cv.meanViews)}</td>
                    <td className="num">{compact(cv.medianViews)}</td>
                    <td className="num">{pct(cv.facelessRatio, 0)}</td>
                    <td><ScoreBar value={cv.score.medianViral} /></td>
                    <td><ScoreBar value={cv.score.medianFinal} /></td>
                    <td>{cv.eligible ? <Badge tone="green">대상</Badge> : <Badge tone="red">제외</Badge>}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        {ds.channelViews.length === 0 && <p className="text-sm text-neutral-500">수집된 채널이 없습니다. 설정에서 수집을 실행하세요.</p>}
      </Card>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card title="초기 후보 10개 (요청 목록)">
          <CandidateTable list={CANDIDATES.filter((c) => c.list === "initial")} />
        </Card>
        <Card title="교체 후보 (페이스리스 추정)">
          <CandidateTable list={CANDIDATES.filter((c) => c.list === "replacement")} />
          <p className="mt-3 text-xs text-neutral-500">
            초기 후보 중 진행자·출연자 노출(D 추정) 채널은 제외하고 교체 후보로 보충했습니다. 모든 분류는 영상 직접 확인 전 &lsquo;추정&rsquo;입니다.
            추가 후보는 설정 화면의 &lsquo;교체 후보 검색&rsquo;으로 찾을 수 있습니다(검색 결과는 관련도 정렬의 일부입니다).
          </p>
        </Card>
      </div>
    </>
  );
}

function CandidateTable({ list }: { list: CandidateChannel[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="tbl">
        <thead>
          <tr>
            <th>채널</th>
            <th>사전 분류</th>
            <th>판정</th>
            <th>사유</th>
          </tr>
        </thead>
        <tbody>
          {list.map((c) => (
            <tr key={c.key}>
              <td>
                {c.url ? <a href={c.url} target="_blank" rel="noreferrer" className="font-medium hover:underline">{c.name}</a> : c.name}
                <div className="font-mono text-xs text-neutral-400">{c.channelId}</div>
              </td>
              <td><ClassBadge cls={c.priorClass} /></td>
              <td>
                {c.decision === "selected" ? <Badge tone="green">선정</Badge> : c.decision === "excluded" ? <Badge tone="red">제외</Badge> : <Badge tone="gray">확인 필요</Badge>}
              </td>
              <td className="text-xs text-neutral-600">
                {c.decisionReason}
                <div className="text-neutral-400">근거: {c.priorReason}</div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
