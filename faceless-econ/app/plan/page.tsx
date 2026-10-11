import { Schedule } from "@/components/Schedule";
import { Badge, Card, PageTitle } from "@/components/ui";
import { AREAS, CRITERIA_LABELS, FINAL_REASON, FINAL_TOPIC_ID, TOPICS, areaTotal } from "@/lib/planner/topics";
import { AUDIO_DIRECTION, CTA, DESCRIPTION, FINAL_VIDEO, SCENES } from "@/lib/planner/script";
import { PHASES } from "@/lib/planner/schedule";

export const dynamic = "force-dynamic";

export default function PlanPage() {
  const final = TOPICS.find((t) => t.id === FINAL_TOPIC_ID)!;
  const criteria = Object.keys(CRITERIA_LABELS) as (keyof typeof CRITERIA_LABELS)[];
  return (
    <>
      <PageTitle title="내 첫 영상 제작" desc="얼굴을 공개하지 않는 한국어 경제·재테크 채널의 첫 영상 기획. 자극적 제목이 아니라 내용으로 입증할 수 있는 주제만 선택했습니다." />

      <Card title="콘텐츠 영역 평가 (1~5점, 높을수록 유리)">
        <div className="overflow-x-auto">
          <table className="tbl">
            <thead>
              <tr>
                <th>영역</th>
                {criteria.map((c) => <th key={c} className="num">{CRITERIA_LABELS[c]}</th>)}
                <th className="num">합계</th>
                <th>공식 자료 / 메모</th>
              </tr>
            </thead>
            <tbody>
              {[...AREAS].sort((a, b) => areaTotal(b) - areaTotal(a)).map((a) => (
                <tr key={a.area}>
                  <td className="font-medium">{a.area}</td>
                  {criteria.map((c) => <td key={c} className="num">{a.scores[c]}</td>)}
                  <td className="num font-bold">{areaTotal(a)}</td>
                  <td className="text-xs text-neutral-600">{a.officialSources.join(" · ")}<div className="text-neutral-400">{a.note}</div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-neutral-500">검색 수요는 추정치입니다. 네이버 데이터랩·Google 트렌드로 확인하고, 수집한 벤치마킹 데이터의 주제 키워드(비교 화면)와 대조하세요.</p>
      </Card>

      <Card title="첫 영상 후보 10개" className="mt-6">
        <div className="space-y-2">
          {TOPICS.map((t) => (
            <details key={t.id} className="rounded-lg border border-neutral-200 p-3 open:bg-neutral-50" open={t.id === FINAL_TOPIC_ID}>
              <summary className="cursor-pointer">
                <span className="font-semibold">{t.id}. {t.titles[0]}</span>{" "}
                <span className="ml-1 inline-flex gap-1 align-middle">
                  <Badge tone="gray">{t.area}</Badge>
                  <Badge tone={t.difficulty === "하" ? "green" : t.difficulty === "중" ? "amber" : "red"}>난이도 {t.difficulty}</Badge>
                  {t.needsLiveData && <Badge tone="amber">최신 수치 의존</Badge>}
                  {t.id === FINAL_TOPIC_ID && <Badge tone="green">최종 추천</Badge>}
                </span>
              </summary>
              <div className="mt-3 grid gap-3 text-sm md:grid-cols-2">
                <Field label="제목 후보">{t.titles.map((x) => <div key={x}>· {x}</div>)}</Field>
                <Field label="썸네일 문구">{t.thumbnails.map((x) => <div key={x}>· {x}</div>)}</Field>
                <Field label="핵심 시청자">{t.audience}</Field>
                <Field label="영상이 답할 질문">{t.question}</Field>
                <Field label="차별화 포인트">{t.differentiation}</Field>
                <Field label="주요 근거 자료">{t.sources.join(" · ")}</Field>
                <Field label="권장 구성 (6~10분)">{t.structure.map((x) => <div key={x}>· {x}</div>)}</Field>
                <Field label="필요한 시각 자료">{t.visuals.join(" · ")}</Field>
                <Field label="파생 쇼츠">{t.shorts.map((x) => <div key={x}>· {x}</div>)}</Field>
                <Field label="선정 근거 / 불확실성">{t.rationale}<div className="mt-1 text-neutral-500">불확실성: {t.uncertainty}</div></Field>
              </div>
            </details>
          ))}
        </div>
      </Card>

      <Card title={<>최종 추천: {FINAL_VIDEO.title}</>} className="mt-6">
        <ul className="list-disc space-y-1 pl-5 text-sm">{FINAL_REASON.map((r) => <li key={r}>{r}</li>)}</ul>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="rounded-xl bg-[#14213d] p-5 text-[#ffd60a] md:col-span-1">
            <div className="whitespace-pre-line text-2xl font-black leading-tight">{FINAL_VIDEO.thumbnail.main}</div>
            <div className="mt-3 text-sm font-semibold text-white/90">{FINAL_VIDEO.thumbnail.sub}</div>
            <div className="mt-3 text-xs text-white/50">썸네일 시안 (텍스트 배치 예시)</div>
          </div>
          <div className="space-y-2 text-sm md:col-span-2">
            <Field label="핵심 주장 한 문장">{FINAL_VIDEO.claim}</Field>
            <Field label="대체 제목">{FINAL_VIDEO.altTitles.join(" / ")}</Field>
            <Field label="대체 썸네일 문구">{FINAL_VIDEO.thumbnail.alternatives.join(" / ")}</Field>
            <Field label="썸네일 디자인">{FINAL_VIDEO.thumbnail.design}</Field>
            <Field label="분량">{FINAL_VIDEO.runtime}</Field>
          </div>
        </div>
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          <div className="font-semibold">녹음 전 반드시 확인할 수치 (지어내지 않고 비워 둠)</div>
          <ul className="mt-1 list-disc pl-5">{FINAL_VIDEO.checkBeforeRecording.map((c) => <li key={c}>{c}</li>)}</ul>
        </div>
      </Card>

      <Card title="도입부 0~30초 대본" className="mt-6">
        <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{SCENES[0].narration}</p>
      </Card>

      <Card title="타임코드별 장면 구성표 · 전체 대본" className="mt-6">
        <div className="overflow-x-auto">
          <table className="tbl">
            <thead>
              <tr>
                <th>장면</th>
                <th className="min-w-[340px]">내레이션</th>
                <th>화면 자막</th>
                <th>차트·자료 화면</th>
                <th>전환</th>
                <th>음향</th>
              </tr>
            </thead>
            <tbody>
              {SCENES.map((s) => (
                <tr key={s.no}>
                  <td className="whitespace-nowrap">
                    <div className="font-semibold">#{s.no} {s.time}</div>
                    <div className="text-xs text-neutral-500">{s.section}</div>
                  </td>
                  <td className="leading-relaxed">{s.narration}</td>
                  <td className="text-xs font-semibold">{s.caption}</td>
                  <td className="text-xs text-neutral-600">{s.visual}</td>
                  <td className="text-xs text-neutral-600">{s.transition}</td>
                  <td className="text-xs text-neutral-600">{s.audio}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-neutral-500">
          전체 대본 {SCENES.reduce((a, s) => a + s.narration.replace(/\s/g, "").length, 0).toLocaleString()}자(공백 제외). 타 채널 대본을 사용하지 않은 독립 대본이며, 구조 원리(결론 먼저 → 단계별 근거 → 내 생활의 의미 → 행동)만 차용했습니다.
        </p>
      </Card>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <Card title="음향 및 배경음악 방향">
          <ul className="list-disc space-y-1 pl-5 text-sm">{AUDIO_DIRECTION.map((a) => <li key={a}>{a}</li>)}</ul>
        </Card>
        <Card title="시청자 행동 유도 문구">
          <ul className="space-y-1 text-sm">
            <li><strong>댓글:</strong> {CTA.comment}</li>
            <li><strong>구독:</strong> {CTA.subscribe}</li>
            <li><strong>고정 댓글:</strong> {CTA.pinnedComment}</li>
          </ul>
        </Card>
      </div>

      <Card title="영상 설명란과 출처 목록" className="mt-6">
        <pre className="whitespace-pre-wrap rounded-lg bg-neutral-50 p-3 text-sm">{DESCRIPTION}</pre>
      </Card>

      <Card title="30일 제작 일정" className="mt-6">
        <div className="mb-3 flex flex-wrap gap-2 text-xs">
          {PHASES.map((p) => <Badge key={p.range} tone="gray">{p.range}: {p.name}</Badge>)}
        </div>
        <Schedule />
      </Card>
    </>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs font-semibold text-neutral-500">{label}</div>
      <div className="mt-0.5">{children}</div>
    </div>
  );
}
