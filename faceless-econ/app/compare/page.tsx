import Link from "next/link";
import { DurationScatter } from "@/components/charts";
import { Badge, Card, ClassBadge, Kind, PageTitle } from "@/components/ui";
import { channelProfile, extractPatterns } from "@/lib/analysis/patterns";
import { analyzeTitle } from "@/lib/analysis/title";
import { getDataset } from "@/lib/dataset";
import { pct } from "@/lib/format";
import { rankScores } from "@/lib/scoring/viral";

export const dynamic = "force-dynamic";

export default function ComparePage() {
  const ds = getDataset();
  const ids = ds.pinnedTop3;
  const vids = ds.recent.filter((v) => ids.includes(v.channelId));
  const findings = extractPatterns(vids, ds.scoreMap, ds.annotations);
  const profiles = ids.map((id) => ({ id, ch: ds.channelMap.get(id)!, p: channelProfile(id, ds.recent, ds.scoreMap, ds.settings.periodDays) })).filter((x) => x.ch);

  const scatter = profiles.map(({ id, ch }) => ({
    name: ch.title,
    points: vids
      .filter((v) => v.channelId === id && v.format === "long" && v.durationSec != null && ds.scoreMap.get(v.id)?.viralScore != null)
      .map((v) => ({ x: v.durationSec! / 60, y: ds.scoreMap.get(v.id)!.viralScore!, title: v.title })),
  }));

  return (
    <>
      <PageTitle title="상위 3개 채널 비교" desc="공통점과 차이점을 분리하고, 각 결론에 근거 영상·표본 수·신뢰 수준을 연결합니다. 상관관계를 인과관계로 해석하지 않습니다." />
      {profiles.length < 3 && (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          분석 대상이 {profiles.length}개입니다. 3번째 채널(경제·기업사 애니메이션)을 <Link href="/settings#top3" className="underline">설정</Link>에서 지정하세요.
        </div>
      )}

      <Card title="채널별 성공 패턴 · 제작 방식">
        <div className="overflow-x-auto">
          <table className="tbl">
            <thead>
              <tr>
                <th>항목</th>
                {profiles.map(({ ch }) => <th key={ch.id}><Link href={`/channels/${ch.id}`} className="hover:underline">{ch.title}</Link></th>)}
              </tr>
            </thead>
            <tbody>
              <tr><td>페이스리스 제작 방식</td>{profiles.map(({ ch }) => <td key={ch.id}><ClassBadge cls={ch.faceless.cls} confidence={ch.faceless.confidence} /></td>)}</tr>
              <tr><td>최근 영상 수 (롱폼/쇼츠)</td>{profiles.map(({ id, p }) => <td key={id}>{p.n} ({p.longCount}/{p.shortsCount})</td>)}</tr>
              <tr><td>주당 업로드</td>{profiles.map(({ id, p }) => <td key={id}>{p.uploadsPerWeek.toFixed(1)}개</td>)}</tr>
              <tr><td>롱폼 길이 중앙값</td>{profiles.map(({ id, p }) => <td key={id}>{p.medianDurationMin?.toFixed(1) ?? "-"}분</td>)}</tr>
              <tr><td>제목 길이 중앙값</td>{profiles.map(({ id, p }) => <td key={id}>{p.medianTitleLen ?? "-"}자</td>)}</tr>
              <tr><td>숫자 포함 제목</td>{profiles.map(({ id, p }) => <td key={id}>{pct(p.numberTitleShare, 0)}</td>)}</tr>
              <tr><td>질문형 제목</td>{profiles.map(({ id, p }) => <td key={id}>{pct(p.questionShare, 0)}</td>)}</tr>
              <tr><td>주요 주제 키워드</td>{profiles.map(({ id, p }) => <td key={id} className="text-xs">{p.topKeywords.join(", ") || "-"}</td>)}</tr>
              <tr>
                <td>성과 상위 영상 제목</td>
                {profiles.map(({ id }) => (
                  <td key={id} className="text-xs">
                    <ol className="list-decimal space-y-1 pl-4">
                      {rankScores(ds.scores.filter((s) => s.channelId === id && s.format === "long" && s.finalScore != null)).slice(0, 3).map((s) => {
                        const v = ds.videoMap.get(s.videoId)!;
                        return (
                          <li key={s.videoId}>
                            <Link href={`/videos/${v.id}`} className="hover:underline">{v.title}</Link>
                            <div className="text-neutral-400">{analyzeTitle(v.title).types.join("·")}</div>
                          </li>
                        );
                      })}
                    </ol>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="길이와 성과 (롱폼)" className="mt-6">
        {scatter.some((s) => s.points.length) ? <DurationScatter series={scatter} /> : <p className="text-sm text-neutral-500">점수가 계산된 롱폼이 없습니다.</p>}
        <p className="mt-2 text-xs text-neutral-500">바이럴 점수는 형식 그룹 내 백분위입니다. 길이와 점수의 관계는 주제 복잡도와 섞여 있어 길이의 효과로 해석하지 않습니다.</p>
      </Card>

      <div className="mt-6 space-y-4">
        {findings.map((f) => (
          <Card key={f.question} title={f.question} right={<span className="flex gap-1"><Kind kind={f.kind} /><Badge tone="gray">표본 {f.n}</Badge><Badge tone={f.confidence === "높음" ? "green" : f.confidence === "중간" ? "blue" : "amber"}>신뢰 {f.confidence}</Badge></span>}>
            <p className="text-sm">{f.answer}</p>
            {f.details && f.details.length > 0 && <ul className="mt-2 list-disc pl-5 text-xs text-neutral-600">{f.details.map((d) => <li key={d}>{d}</li>)}</ul>}
            {f.alternatives && f.alternatives.length > 0 && (
              <div className="mt-2 text-xs text-neutral-600">
                <span className="font-semibold">대안 가설:</span> {f.alternatives.join(" / ")}
              </div>
            )}
            {f.evidence.length > 0 && (
              <div className="mt-2 text-xs">
                <span className="font-semibold">근거 영상:</span>
                <ul className="mt-1 space-y-0.5">
                  {f.evidence.map((e) => (
                    <li key={e.videoId}>
                      <Link href={`/videos/${e.videoId}`} className="hover:underline">{e.title}</Link> <span className="text-neutral-400">({e.value})</span>
                      {e.url !== "#demo" && <> · <a href={e.url} className="underline" target="_blank" rel="noreferrer">{e.url}</a></>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        ))}
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <Card title="따라 할 요소 (구조 원리)">
          <ul className="list-disc space-y-1 pl-5 text-sm">
            <li>제목에서 질문·숫자로 약속하고, 도입 30초 안에 답의 방향(결론)을 먼저 제시</li>
            <li>경제지표를 &lsquo;내 대출·월급·집값&rsquo; 같은 개인 결과로 번역</li>
            <li>근거마다 공식 출처와 기준일을 화면에 표시</li>
            <li>단계 구조(①②③)로 정보 순서를 시각화 — 도식·차트로 제작 가능</li>
            <li>롱폼 1개에서 계산·핵심 한 줄을 쇼츠 2개로 파생</li>
          </ul>
        </Card>
        <Card title="피할 요소">
          <ul className="list-disc space-y-1 pl-5 text-sm">
            <li>타 채널의 대본 문장, 캐릭터, 썸네일 디자인, 시리즈명 복제</li>
            <li>근거 없는 폭락·급등 단정, 수익 보장 표현</li>
            <li>영상 내용과 맞지 않는 과장 썸네일 (시청 지속률·신뢰 하락 위험 — 가설)</li>
            <li>실시간 시세에 의존해 금방 틀린 정보가 되는 주제를 첫 영상으로 선택</li>
            <li>상위 채널의 구독자 규모 효과를 신규 채널에서도 기대하는 것</li>
          </ul>
        </Card>
      </div>
    </>
  );
}
