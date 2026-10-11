import { ChannelSearch, CollectButton, FacelessForm, SettingsForm, Top3Form } from "@/components/SettingsPanel";
import { Badge, Card, PageTitle, SourceBadge } from "@/components/ui";
import { CANDIDATES, SLOT3, candidateById } from "@/lib/candidates";
import { getDataset, targetChannelIds } from "@/lib/dataset";
import { kst } from "@/lib/time";
import { dailyQuota, quotaUsedToday } from "@/lib/youtube/client";

export const dynamic = "force-dynamic";

export default function SettingsPage() {
  const ds = getDataset();
  const s = ds.settings;
  const targets = targetChannelIds(s);
  const nameOf = (id: string) => ds.channelMap.get(id)?.title ?? candidateById(id)?.name ?? id;
  const channelOpts = targets.map((id) => ({ id, title: nameOf(id) }));
  const slot3 = SLOT3.candidateIds.map((id) => ({ id, title: nameOf(id) }));

  return (
    <>
      <PageTitle title="데이터 및 설정" />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="API 연결 상태">
          <ul className="space-y-1 text-sm">
            <li>YouTube Data API 키: {ds.apiKeyConfigured ? <Badge tone="green">설정됨 (값은 표시하지 않음)</Badge> : <Badge tone="red">없음</Badge>}</li>
            <li>오늘 추정 사용량: {quotaUsedToday().toLocaleString()} / {dailyQuota().toLocaleString()} 단위 (태평양 시간 자정 초기화)</li>
            <li>현재 표시 데이터: <SourceBadge source={ds.source} /></li>
            <li>수집 대상 채널: {targets.length}개 (초기·교체 후보 전체 + 고정·추가 채널)</li>
          </ul>
          {!ds.apiKeyConfigured && (
            <ol className="mt-3 list-decimal space-y-1 pl-5 text-sm text-neutral-700">
              <li>Google Cloud Console에서 프로젝트 생성 → &lsquo;YouTube Data API v3&rsquo; 사용 설정</li>
              <li>사용자 인증 정보 → API 키 만들기 (가능하면 키 제한: YouTube Data API v3만)</li>
              <li>프로젝트 폴더의 <code>.env.example</code>을 <code>.env.local</code>로 복사하고 <code>YOUTUBE_API_KEY=</code> 뒤에 키 붙여넣기</li>
              <li>개발 서버를 껐다가 다시 실행 (<code>npm run dev</code>)</li>
            </ol>
          )}
        </Card>

        <Card title="데이터 수집 실행">
          <CollectButton apiKey={ds.apiKeyConfigured} />
          <p className="mt-3 text-xs text-neutral-500">
            채널 정보 → 업로드 플레이리스트(최근 {s.peerWindowDays}일) → 영상 상세 순으로 수집하고, 같은 시각의 조회수 스냅샷을 저장합니다.
            매일 비슷한 시각에 한 번씩 실행하면 24시간·72시간·7일·14일 비교와 채널 내 상대 성과가 계산됩니다. 터미널에서 <code>npm run collect</code>로도 실행할 수 있습니다.
          </p>
          {ds.runs.length > 0 && (
            <div className="mt-3 max-h-64 overflow-y-auto">
              <table className="tbl">
                <thead><tr><th>시작(KST)</th><th>상태</th><th className="num">영상</th><th className="num">할당량</th><th>메시지</th></tr></thead>
                <tbody>
                  {ds.runs.slice(0, 10).map((r) => (
                    <tr key={r.id}>
                      <td className="text-xs">{kst(r.startedAt)}</td>
                      <td><Badge tone={r.status === "success" ? "green" : r.status === "partial" ? "amber" : "red"}>{r.status}</Badge></td>
                      <td className="num">{r.videosCollected}</td>
                      <td className="num">{r.quotaUsed}</td>
                      <td className="text-xs">
                        <details>
                          <summary>{r.messages.filter((m) => m.level !== "info").length}건 경고·오류</summary>
                          <ul>{r.messages.map((m, i) => <li key={i} className={m.level === "error" ? "text-rose-700" : m.level === "warn" ? "text-amber-700" : ""}>{m.text}</li>)}</ul>
                        </details>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <Card title="가중치 · 분석 기간 · 데이터 모드">
          <SettingsForm settings={s} />
        </Card>

        <Card title={<span id="top3">정밀 분석 대상 3개 채널</span>}>
          <p className="mb-3 text-sm text-neutral-600">
            사용자 선정: 경제의 시작, 재테크읽어주는 파일럿, {SLOT3.label}(미확정). 3번째는 후보 채널의 영상을 직접 확인한 뒤 지정하세요:{" "}
            {slot3.map((x) => x.title).join(" · ")}.
          </p>
          <Top3Form settings={s} channels={channelOpts} slot3={slot3} />
        </Card>

        <Card title={<span id="faceless">페이스리스 수동 판정</span>}>
          <p className="mb-3 text-sm text-neutral-600">자동 판정은 최대 &lsquo;추정&rsquo;입니다. 영상 화면을 직접 확인한 경우에만 &lsquo;확정&rsquo;으로 저장하세요.</p>
          <FacelessForm channels={channelOpts} overrides={s.facelessOverrides} />
        </Card>

        <Card title="채널 추가 · 교체 후보 검색">
          <ChannelSearch apiKey={ds.apiKeyConfigured} />
          {s.extraChannelIds.length > 0 && <p className="mt-2 text-xs text-neutral-500">사용자 추가 채널: {s.extraChannelIds.map(nameOf).join(", ")}</p>}
        </Card>

        <Card title="JSON · CSV 내보내기">
          <div className="flex flex-wrap gap-2 text-sm">
            <a className="rounded-lg px-3 py-1.5 ring-1 ring-neutral-300 hover:bg-neutral-50" href="/api/export?type=videos">영상·점수 CSV</a>
            <a className="rounded-lg px-3 py-1.5 ring-1 ring-neutral-300 hover:bg-neutral-50" href="/api/export?type=channels">채널 CSV</a>
            <a className="rounded-lg px-3 py-1.5 ring-1 ring-neutral-300 hover:bg-neutral-50" href="/api/export?type=snapshots">스냅샷 CSV</a>
            <a className="rounded-lg px-3 py-1.5 ring-1 ring-neutral-300 hover:bg-neutral-50" href="/api/export?format=json">전체 JSON</a>
          </div>
          <p className="mt-2 text-xs text-neutral-500">CSV는 UTF-8(BOM 포함)로 Excel에서 바로 열립니다. 각 영상의 원본 값·정규화 값·사용 가중치·결측 사유가 포함됩니다. 데모 데이터는 파일명에 DEMO_가 붙습니다.</p>
        </Card>

        <Card title="데이터 출처와 한계" className="xl:col-span-2">
          <ul className="list-disc space-y-1 pl-5 text-sm text-neutral-700">
            <li>출처: YouTube Data API v3 (channels, playlistItems, videos). 교체 후보 검색만 search.list를 사용하며, 관련도 정렬의 일부 결과일 뿐 전체 모집단이 아닙니다.</li>
            <li>최근 영상은 업로드 플레이리스트로 수집해 검색보다 누락이 적지만, 멤버십 전용·예약 공개 등 일부 영상은 빠질 수 있어 &lsquo;전수&rsquo;로 단정하지 않습니다.</li>
            <li>YouTube API는 과거 시점의 조회수를 제공하지 않습니다. 과거 비교는 이 앱이 직접 저장한 스냅샷으로만 하며, 없는 시점의 값은 역산하지 않습니다.</li>
            <li>구독자 수는 YouTube가 반올림해 공개한 값입니다. 비공개 채널은 구독자 대비 지표를 계산하지 않습니다.</li>
            <li>좋아요·댓글이 비공개·비활성인 영상은 해당 지표를 결측 처리하고 0점으로 보지 않습니다.</li>
            <li>쇼츠 여부는 API가 직접 제공하지 않아 영상 길이·#shorts 표기·/shorts/ 주소 응답으로 판별합니다(근거를 함께 저장).</li>
            <li>페이스리스 판정은 제목·설명·라이브 여부 등 간접 근거에 의한 추정이며, 확정은 사용자의 직접 확인으로만 가능합니다.</li>
            <li>썸네일·영상 구성·자막 분석은 자동으로 수행하지 않습니다(이미지·영상을 상상해 분석하지 않음). 영상 정밀 분석 화면에서 직접 확인 후 입력합니다.</li>
            <li>영상 다운로드, 비공개 자막 접근, 타 채널 대본·썸네일 복제 기능은 제공하지 않습니다. 썸네일은 원본 링크와 함께 분석 목적으로만 표시합니다.</li>
            <li>초기 후보 채널 ID는 2026-10-11 YouTube 공개 검색 결과에서 확인했습니다. 채널 정보는 수집 시 API 값으로 갱신됩니다. 후보 {CANDIDATES.length}개.</li>
          </ul>
        </Card>
      </div>
    </>
  );
}
