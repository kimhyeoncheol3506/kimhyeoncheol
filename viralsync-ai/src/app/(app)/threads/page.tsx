import { requireCtx } from "@/lib/auth/current";
import { can } from "@/lib/auth/permissions";
import { listQuickPosts, threadsStatus } from "@/lib/services/threads";
import { dateOnly, dateTime } from "@/lib/format";
import { Card, CardBody, CardHeader, PageHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, EmptyState, Forbidden } from "@/components/ui/misc";
import { ThreadsComposer } from "@/components/threads/composer";
import { DisconnectForm, TokenConnectForm } from "@/components/threads/connect-forms";

export const metadata = { title: "스레드 바로 올리기" };

const ERR: Record<string, string> = {
  denied: "Threads 로그인이 취소되었습니다.",
  state: "보안 확인(state)에 실패했습니다. 다시 시도하세요.",
  connect: "Threads 계정 연결에 실패했습니다. 앱 ID·시크릿·리디렉션 주소를 확인하세요.",
  not_configured: "THREADS_APP_ID / THREADS_REDIRECT_URI 가 설정되지 않았습니다.",
  forbidden: "계정 연결은 관리자만 할 수 있습니다.",
};

export default async function ThreadsPage({ searchParams }: { searchParams: Promise<{ connected?: string; error?: string }> }) {
  const ctx = await requireCtx();
  if (!can(ctx.role, "publication:execute")) return <Forbidden message="게시 권한이 없습니다." />;
  const sp = await searchParams;
  const [st, posts] = await Promise.all([threadsStatus(ctx), listQuickPosts(ctx)]);
  const isAdmin = can(ctx.role, "account:manage");

  return (
    <>
      <PageHeader title="스레드 바로 올리기" description="사진이나 스크린샷 한 장을 붙여넣고 문구를 쓰면 내 Threads 계정에 바로 게시합니다 (Threads 공식 API)." />
      {sp.connected && <div className="mb-4"><Alert tone="success">Threads 계정이 연결되었습니다.</Alert></div>}
      {sp.error && ERR[sp.error] && <div className="mb-4"><Alert tone="error">{ERR[sp.error]}</Alert></div>}

      <Card className="mb-6">
        <CardHeader
          title="연결 상태"
          action={st.canPublishLive ? <Badge tone="green">실제 게시 가능</Badge> : <Badge tone="amber">모의 게시만 가능</Badge>}
        />
        <CardBody className="space-y-4 text-sm">
          {st.account ? (
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-semibold">{st.account.username}</span>
              <code className="text-xs text-slate-400">{st.account.tokenHint}</code>
              <span className="text-xs text-slate-500">토큰 만료: {st.account.expiresAt ? dateOnly(st.account.expiresAt) : "확인 불가 (직접 붙여넣은 토큰)"}</span>
              {st.account.lastError && <Badge tone="red">{st.account.lastError}</Badge>}
              {isAdmin && <DisconnectForm />}
            </div>
          ) : isAdmin ? (
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="mb-2 font-medium">방법 1. Threads 로그인으로 연결</p>
                {st.oauthReady ? (
                  <a href="/api/threads/connect" className="inline-flex rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800">Threads 로 로그인해서 연결</a>
                ) : (
                  <p className="text-xs text-slate-500">THREADS_APP_ID · THREADS_APP_SECRET · THREADS_REDIRECT_URI · TOKEN_ENCRYPTION_KEY 를 설정하면 버튼이 나타납니다 (README 참고).</p>
                )}
              </div>
              <div>
                <p className="mb-2 font-medium">방법 2. 액세스 토큰 붙여넣기</p>
                <TokenConnectForm />
              </div>
            </div>
          ) : (
            <p className="text-slate-500">Threads 계정이 연결되지 않았습니다. 관리자에게 연결을 요청하세요.</p>
          )}
          {!st.publicBaseUrl && (
            <Alert tone="info" title="이미지 공개 주소가 필요합니다">
              Threads 는 이미지를 인터넷 주소에서 가져가므로, 이 앱이 외부에서 접속 가능한 https 주소로 열려 있어야 합니다. 배포된 주소나 터널 주소를 <code>PUBLIC_BASE_URL</code> 에 넣으세요 (README ‘스레드 바로 올리기’ 참고).
            </Alert>
          )}
        </CardBody>
      </Card>

      <Card className="mb-6">
        <CardHeader title="새 게시물" />
        <CardBody>
          <ThreadsComposer canLive={st.canPublishLive} liveProblems={st.problems} accountName={st.account?.username ?? null} />
        </CardBody>
      </Card>

      <Card>
        <CardHeader title={`게시 기록 (${posts.length})`} />
        <CardBody>
          {posts.length === 0 ? (
            <EmptyState title="아직 게시한 내용이 없습니다" />
          ) : (
            <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {posts.map((p) => (
                <li key={p.id} className="overflow-hidden rounded-xl border border-slate-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={`/media/${p.imageFile}`} alt="" className="h-40 w-full bg-slate-50 object-contain" />
                  <div className="space-y-1 p-3 text-xs">
                    <div className="flex flex-wrap gap-1">
                      {p.mode === "SIMULATED" ? <Badge tone="purple">모의</Badge> : <Badge tone="blue">실제</Badge>}
                      {p.status === "PUBLISHED" ? <Badge tone="green">게시됨</Badge> : p.status === "FAILED" ? <Badge tone="red">실패</Badge> : <Badge tone="amber">게시 중</Badge>}
                      {p.isAd && <Badge tone="amber">광고</Badge>}
                    </div>
                    {p.caption && <p className="line-clamp-3 whitespace-pre-wrap text-slate-700">{p.caption}</p>}
                    {p.permalink && <a href={p.permalink} target="_blank" rel="noreferrer noopener" className="link block break-all">스레드에서 보기 ↗</a>}
                    {p.errorMessage && <p className="text-rose-600">[{p.errorCode}] {p.errorMessage}</p>}
                    <p className="text-slate-400">{dateTime(p.createdAt)} · {p.createdBy?.name ?? "-"}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </>
  );
}
