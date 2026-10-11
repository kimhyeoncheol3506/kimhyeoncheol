import Link from "next/link";
import { notFound } from "next/navigation";
import { AnnotationForm } from "@/components/AnnotationForm";
import { SnapshotChart } from "@/components/charts";
import { Badge, Card, ClassBadge, Kind, NA, PageTitle, ScoreBar, SourceBadge, Stat, Thumb } from "@/components/ui";
import { analyzeTitle } from "@/lib/analysis/title";
import { getDataset } from "@/lib/dataset";
import { FORMAT_LABELS, compact, num, pct } from "@/lib/format";
import { METRIC_LABELS, MILESTONES, VIRAL_METRICS } from "@/lib/scoring/viral";
import { fmtAge, fmtDuration, kst } from "@/lib/time";

export const dynamic = "force-dynamic";

export default function VideoDetail({ params }: { params: { id: string } }) {
  const ds = getDataset();
  const v = ds.videoMap.get(decodeURIComponent(params.id));
  if (!v) notFound();
  const ch = ds.channelMap.get(v.channelId);
  const s = ds.scoreMap.get(v.id);
  const ta = analyzeTitle(v.title.replace("[데모] ", ""));
  const ann = ds.annotations[v.id] ?? null;
  const pub = v.publishedAt ? Date.parse(v.publishedAt) : null;
  const points = ds.snapshots
    .filter((x) => x.videoId === v.id && x.viewCount != null && pub != null)
    .map((x) => ({ label: x.collectedAt, ageH: (Date.parse(x.collectedAt) - pub!) / 3_600_000, views: x.viewCount! }))
    .sort((a, b) => a.ageH - b.ageH);
  const isDemo = v.source === "demo";

  return (
    <>
      <PageTitle title={v.title} desc={`${ch?.title ?? v.channelId} · ${FORMAT_LABELS[v.format]} (${v.formatEvidence})`}>
        <div className="flex items-center gap-2">
          <SourceBadge source={v.source} />
          {!isDemo && (
            <a href={v.url} target="_blank" rel="noreferrer" className="rounded-lg bg-neutral-900 px-3 py-1.5 text-sm font-semibold text-white">
              원본 영상 바로가기 ↗
            </a>
          )}
        </div>
      </PageTitle>
      {v.status === "unavailable" && <div className="mb-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-800">이 영상은 최근 수집에서 조회되지 않았습니다 (삭제 또는 비공개 전환). 마지막 관측값을 표시합니다.</div>}

      <div className="grid gap-6 xl:grid-cols-3">
        <Card title="영상 정보" right={<Kind kind="관측" />}>
          <Thumb url={v.thumbnailUrl} alt={v.title} label={isDemo ? "데모 영상 — 썸네일 없음" : "썸네일 수집 불가"} />
          {v.thumbnailUrl && (
            <p className="mt-1 text-xs text-neutral-500">
              썸네일 출처: <a className="underline" href={v.url} target="_blank" rel="noreferrer">{ch?.title} 원본 영상</a> (분석 목적 표시, 복제 금지)
            </p>
          )}
          <dl className="mt-3 grid grid-cols-[auto,1fr] gap-x-3 gap-y-1 text-sm">
            <dt className="text-neutral-500">영상 ID</dt><dd className="font-mono">{v.id}</dd>
            <dt className="text-neutral-500">게시</dt><dd>{kst(v.publishedAt)}</dd>
            <dt className="text-neutral-500">경과</dt><dd>{fmtAge(s?.ageHours ?? null)}</dd>
            <dt className="text-neutral-500">길이</dt><dd>{fmtDuration(v.durationSec)}</dd>
            <dt className="text-neutral-500">조회수</dt><dd>{num(v.viewCount)}</dd>
            <dt className="text-neutral-500">좋아요</dt><dd>{v.likeCount == null ? <NA>비공개/수집 불가</NA> : num(v.likeCount)}</dd>
            <dt className="text-neutral-500">댓글</dt><dd>{v.commentCount == null ? <NA>비활성/수집 불가</NA> : num(v.commentCount)}</dd>
            <dt className="text-neutral-500">구독자(당시)</dt><dd>{v.channelSubscriberCount == null ? <NA>비공개/수집 불가</NA> : num(v.channelSubscriberCount)}</dd>
            <dt className="text-neutral-500">수집 시각</dt><dd>{kst(v.collectedAt)}</dd>
            <dt className="text-neutral-500">페이스리스</dt><dd><ClassBadge cls={v.faceless.cls} confidence={v.faceless.confidence} /></dd>
          </dl>
          <ul className="mt-2 list-disc pl-5 text-xs text-neutral-500">{v.faceless.evidence.map((e, i) => <li key={i}>{e}</li>)}</ul>
        </Card>

        <Card title="점수 산출 내역" className="xl:col-span-2" right={<Kind kind="관측" />}>
          {!s ? (
            <p className="text-sm text-neutral-500">최근 {ds.settings.periodDays}일 게시 영상이 아니어서 순위 계산 대상이 아닙니다 (참고 목록).</p>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                <Stat label="바이럴 성과 점수" value={<ScoreBar value={s.viralScore} />} sub={s.holdReason ?? `지표 반영률 ${(s.weightCoverage * 100).toFixed(0)}%`} />
                <Stat label="페이스리스 적합성" value={s.facelessScore == null ? "확인 불가" : s.facelessScore} />
                <Stat label="최종 벤치마킹 우선순위" value={<ScoreBar value={s.finalScore} />} sub={`바이럴 ${s.finalWeightsUsed.viral.toFixed(0)}% · 페이스리스 ${s.finalWeightsUsed.faceless.toFixed(0)}%`} />
              </div>
              <table className="tbl mt-4">
                <thead>
                  <tr><th>지표</th><th className="num">원본 값</th><th className="num">정규화(백분위)</th><th className="num">설정 가중치</th><th className="num">실제 사용 가중치</th><th>비고</th></tr>
                </thead>
                <tbody>
                  {VIRAL_METRICS.map((m) => {
                    const r = s.metrics[m];
                    const raw = r.raw == null ? null : m === "likeRate" || m === "commentRate" ? pct(r.raw) : m === "velocity" ? `${compact(r.raw)}/시간` : `${r.raw.toFixed(3)}배`;
                    return (
                      <tr key={m}>
                        <td>{METRIC_LABELS[m]}</td>
                        <td className="num">{raw ?? <NA>결측</NA>}</td>
                        <td className="num">{r.norm == null ? <NA>제외</NA> : r.norm.toFixed(1)}</td>
                        <td className="num">{ds.settings.weights[m]}</td>
                        <td className="num">{s.weightsUsed[m] != null ? `${s.weightsUsed[m]}%` : <NA>0 (제외)</NA>}</td>
                        <td className="text-xs text-neutral-500">{r.note ?? ""}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              <p className="mt-2 text-xs text-neutral-500">
                정규화: 같은 형식({FORMAT_LABELS[s.format]}) {s.groupSize}개 영상 안의 백분위 순위. 결측 지표는 0점이 아니라 계산에서 제외했습니다.
              </p>
              {s.warnings.length > 0 && <div className="mt-2 flex flex-wrap gap-1">{s.warnings.map((w) => <Badge key={w} tone="amber">{w}</Badge>)}</div>}
            </>
          )}
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card title="성과 차트 (실제 스냅샷만)" right={<Kind kind="관측" />}>
          <SnapshotChart points={points} />
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
            {MILESTONES.map((m) => (
              <div key={m.key} className="rounded-md bg-neutral-50 p-2">
                <div className="text-xs text-neutral-500">게시 후 {m.label}</div>
                <div className="font-semibold tabular-nums">{s?.milestones[m.key] == null ? <NA>스냅샷 없음</NA> : compact(s.milestones[m.key])}</div>
              </div>
            ))}
          </div>
          <p className="mt-2 text-xs text-neutral-500">
            조회수 증가 속도(최근 두 스냅샷): {s?.growthPerHour == null ? "스냅샷 2개 미만 — 계산하지 않음" : `${compact(s.growthPerHour)}회/시간`}
          </p>
        </Card>

        <Card title="제목 분석" right={<Kind kind="관측" />}>
          <dl className="grid grid-cols-[auto,1fr] gap-x-3 gap-y-1 text-sm">
            <dt className="text-neutral-500">길이</dt><dd>{ta.length}자 (공백 제외 {ta.lengthNoSpace}자)</dd>
            <dt className="text-neutral-500">앞부분 키워드</dt><dd>{ta.frontKeywords.join(", ") || "-"}</dd>
            <dt className="text-neutral-500">전체 키워드</dt><dd>{v.keywords.join(", ") || "-"}</dd>
            <dt className="text-neutral-500">숫자 사용</dt><dd>{ta.hasNumber ? ta.numbers.join(", ") : "없음"}</dd>
            <dt className="text-neutral-500">유형</dt><dd className="flex flex-wrap gap-1">{ta.types.map((t) => <Badge key={t} tone="blue">{t}</Badge>)}</dd>
            <dt className="text-neutral-500">프레임</dt><dd className="flex flex-wrap gap-1">{ta.frames.length ? ta.frames.map((t) => <Badge key={t} tone="violet">{t}</Badge>) : "감지 안 됨"}</dd>
            <dt className="text-neutral-500">말머리·기호</dt><dd>{ta.hasBracket ? "말머리 있음" : "없음"}{ta.hasEmojiOrSymbol ? " · 이모지 있음" : ""}</dd>
          </dl>
          <div className="mt-3 rounded-md bg-neutral-50 p-2 text-xs text-neutral-600">
            <Kind kind="검증되지 않음" /> 제목과 실제 내용의 일치 여부는 영상을 시청해야 판단할 수 있어 자동 판정하지 않습니다.
            유형·프레임은 단어 규칙으로 감지한 결과입니다.
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card title="썸네일·구성·시각 전달 — 확인 현황">
          <ul className="space-y-3 text-sm">
            <li>
              <div className="flex items-center gap-2 font-semibold">썸네일 {ann?.thumbnail.verified ? <Kind kind="관측" /> : <Kind kind="검증되지 않음" />}</div>
              {ann?.thumbnail.verified ? (
                <p className="text-neutral-700">
                  문구 &ldquo;{ann.thumbnail.text}&rdquo; ({[...ann.thumbnail.text.replace(/\s/g, "")].length}자) · 얼굴 {ann.thumbnail.faceVisible === "yes" ? "있음" : ann.thumbnail.faceVisible === "no" ? "없음" : "미확인"} · 대비 {ann.thumbnail.contrast} · 요소 {ann.thumbnail.elements.join(", ") || "-"} · 배치 {ann.thumbnail.layout || "-"}
                  {ann.thumbnail.text && <> · 제목과 문구 중복: {ann.thumbnail.text.split(/\s+/).filter((w) => w.length > 1 && v.title.includes(w)).length}개 단어</>}
                </p>
              ) : (
                <p className="text-neutral-500">썸네일 이미지를 직접 보고 입력하기 전에는 문구·색상·배치를 분석하지 않습니다.{v.thumbnailUrl ? " 왼쪽 위 이미지를 보고 아래 양식에 입력하세요." : " (이미지 미확보)"}</p>
              )}
            </li>
            <li>
              <div className="flex items-center gap-2 font-semibold">영상 구성·스토리텔링 {ann?.structure.verified ? <Kind kind="관측" /> : <Kind kind="검증되지 않음" />}</div>
              {ann?.structure.verified ? (
                <p className="text-neutral-700">도입: {ann.structure.hook || "-"} / 첫 핵심 정보: {ann.structure.firstInfoSec ?? "-"}초 / 흐름: {ann.structure.flow || "-"} / CTA: {ann.structure.cta || "-"}</p>
              ) : (
                <p className="text-neutral-500">영상·대본을 확인하지 않았으므로 도입부 문장, 장면 전환 시점, 대본을 만들어내지 않습니다.</p>
              )}
            </li>
            <li>
              <div className="flex items-center gap-2 font-semibold">시각적 전달 방식 {ann?.visual.verified ? <Kind kind="관측" /> : <Kind kind="검증되지 않음" />}</div>
              {ann?.visual.verified ? (
                <p className="text-neutral-700">{ann.visual.style || "-"} · 분당 전환 {ann.visual.cutsPerMinute ?? "-"} · 자막 밀도 {ann.visual.subtitleDensity} · {ann.visual.notes}</p>
              ) : (
                <p className="text-neutral-500">영상 프레임·자막을 확보하지 않았습니다. 채널 분류(<ClassBadge cls={v.faceless.cls} />)는 간접 근거에 의한 추정입니다.</p>
              )}
            </li>
            <li>
              <div className="flex items-center gap-2 font-semibold">분석자 가설 <Kind kind="가설" /></div>
              <p className="text-neutral-700">
                {s?.viralScore != null && s.viralScore >= 70
                  ? `같은 형식 영상 대비 상위권(바이럴 ${s.viralScore.toFixed(0)})입니다. 제목의 ${ta.types.join("·")} 구조${ta.frames.length ? `와 ${ta.frames.join("·")} 프레임` : ""}이 클릭에 기여했을 수 있으나, 게시 시점 이슈·알고리즘 노출·썸네일 효과와 분리되지 않습니다.`
                  : "성과가 상위권이 아니거나 판정 보류된 영상입니다. 상위 영상과 비교할 때 대조군으로 활용하세요."}
              </p>
            </li>
          </ul>
        </Card>
        <Card title="직접 확인 입력">
          <AnnotationForm videoId={v.id} initial={ann} disabled={isDemo} />
        </Card>
      </div>

      {v.description && (
        <Card title="설명란 (수집 원문 일부)" className="mt-6">
          <p className="whitespace-pre-wrap text-sm text-neutral-700">{v.description.slice(0, 1200)}{v.description.length > 1200 ? "…" : ""}</p>
        </Card>
      )}
      <p className="mt-4 text-sm"><Link href={`/channels/${v.channelId}`} className="underline">← 채널 영상 목록</Link></p>
    </>
  );
}
