# Cloudflare 배포 안내 (무료로 시작 → 수익 생기면 유료)

구성: **Cloudflare Workers**(앱) + **Neon**(PostgreSQL DB, 무료) + **Cloudflare R2**(스레드 게시용 사진, 무료 한도)
로그인·가입·결제수단·비밀값 입력은 모두 캡틴이 각 서비스의 **공식 화면에서 직접** 합니다.

## ⚠ 먼저 알아 둘 것 — 무료 플랜의 CPU 한도
- Workers 무료 플랜은 **요청 1번당 CPU 10ms** 까지입니다 (유료 $5/월 플랜은 기본 30초).
- 이 앱의 **로그인 1번(비밀번호 확인)에 CPU 약 80ms** 가 듭니다 (이 개발 환경에서 측정). 그래서 무료 플랜에서는 **로그인이 오류(1102 등)로 막힐 가능성이 높습니다.** 실제로 막히는지는 배포 후에만 확인할 수 있습니다.
- 막히면 Cloudflare 대시보드 → Workers → **Workers Paid($5/월)** 로 바꾸면 됩니다. **코드 수정은 필요 없습니다.**
- 완전 무료가 꼭 필요하면 대안: 캡틴 PC 에서 앱을 켜고 **Cloudflare Tunnel** 로 외부에 여는 방법 (PC 가 켜져 있을 때만 접속, 코드 수정 없음).

## 이미 해 둔 것 (코드)
- Workers 실행 환경(workerd)에서 동작하도록 수정: DB 는 요청마다 연결(`src/lib/db.ts`), 사진은 R2 저장(`src/lib/threads/storage.ts`)
- 배포 설정: `wrangler.jsonc`, `open-next.config.ts`
- 같은 E2E 16개를 workerd 에서 실행해 통과: `npm run test:e2e:cf`
- 데모 계정 없이 실제 관리자 만들기: `npm run admin:create`

---

## 1단계. Neon 에 DB 만들기 (무료)
1. https://neon.tech 가입 → **New Project** (Region: 가까운 곳, 예: AWS Asia Pacific (Singapore) / Tokyo)
2. 대시보드 **Connect** 에서 연결 주소 2개를 복사해 메모장에만 둡니다 (채팅·문서에 붙여넣지 마세요)
   - **Pooled connection** (주소에 `-pooler` 포함) → 앱(Cloudflare)용
   - **Direct connection** → 캡틴 PC 에서 표 만들기용
   - 둘 다 끝에 `?sslmode=require` 가 있어야 합니다

## 2단계. 캡틴 PC 에서 표 만들기 + 관리자 계정 만들기
PowerShell 에서 `viralsync-ai` 폴더로 이동한 뒤:
```powershell
git pull
npm install
$env:DATABASE_URL="여기에 Direct connection 주소"
npx prisma db push
npm run admin:create      # 회사 이름 · 관리자 이름 · 이메일 · 비밀번호(10자 이상) 입력
Remove-Item Env:DATABASE_URL
```
> 운영 DB 에는 `npm run db:seed` / `db:reset`(데모 데이터)을 실행하지 마세요. 데모 계정 비밀번호는 공개된 값입니다.

## 3단계. Cloudflare 준비
1. https://dash.cloudflare.com 가입
2. 왼쪽 **R2 Object Storage** → 사용 시작 → **Create bucket** → 이름 `viralsync-media`
   (R2 를 처음 켤 때 결제수단 등록을 요구할 수 있습니다. 무료 한도 안에서는 청구되지 않습니다.)

## 4단계. GitHub 저장소로 자동 배포 (Workers Builds — 윈도우에서 빌드할 필요 없음)
1. **Workers & Pages → Create → Import a repository** → GitHub 연결 → `kimhyeoncheol` 저장소 선택
2. 설정
   | 항목 | 값 |
   |---|---|
   | Project name | `viralsync-ai` (wrangler.jsonc 의 name 과 같아야 함) |
   | Production branch | 배포할 브랜치 (예: `claude/viralsync-ai-mvp`, 나중에 main 으로 합치면 main) |
   | Root directory | `viralsync-ai` |
   | Build command | `npx prisma generate && npx opennextjs-cloudflare build` |
   | Deploy command | `npx opennextjs-cloudflare deploy` |
3. 첫 배포가 끝나면 주소가 나옵니다: `https://viralsync-ai.<계정이름>.workers.dev`

## 5단계. 비밀값 넣기
Worker → **Settings → Variables and Secrets → Add** — 종류는 모두 **Secret** 으로 (배포 때 덮어써지지 않음)

| 이름 | 값 |
|---|---|
| `DATABASE_URL` | Neon **Pooled** 연결 주소 |
| `SESSION_SECRET` | 임의 문자열 32자 이상 (아래 명령으로 생성) |
| `TOKEN_ENCRYPTION_KEY` | 임의 문자열 32자 이상 (SESSION_SECRET 과 다르게) |
| `PUBLIC_BASE_URL` | 4단계에서 받은 `https://viralsync-ai.….workers.dev` |
| `ANTHROPIC_API_KEY` | (선택) 실제 AI 문구 생성 시. 함께 `AI_PROVIDER` 를 `anthropic` 으로 바꾸려면 wrangler.jsonc 의 vars 수정 |
| `THREADS_APP_ID`·`THREADS_APP_SECRET`·`THREADS_REDIRECT_URI` | (선택) 스레드 로그인 연결 시. REDIRECT 는 `https://…workers.dev/api/threads/callback` |

임의 문자열 만들기 (PowerShell):
```powershell
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```
저장 후 **Deployments → 최신 배포 → Retry/Redeploy** 로 한 번 다시 배포합니다.

## 6단계. 확인
1. 주소로 접속 → 2단계에서 만든 관리자 이메일·비밀번호로 로그인
   - 오류 1102(CPU 한도) 등으로 막히면 → Workers Paid($5/월) 로 변경 후 다시 시도
2. **AI 회사 조직도 → 회사 운영 규칙** 에서 월 AI 운영비 상한 정하기
3. **서비스 상품** 에서 샘플 가격을 실제 가격으로 고치기
4. **직원·권한** 에서 함께 일할 사람 계정 만들기

## 다음에 유료로 바꿀 때
| 상황 | 바꿀 것 | 코드 수정 |
|---|---|---|
| 로그인·화면이 CPU 한도로 막힘 / 하루 요청 10만 회 초과 | Workers Paid ($5/월) | 없음 |
| DB 용량·속도 부족 | Neon 유료 플랜 | 없음 |
| DB 접속을 더 빠르게 | Cloudflare Hyperdrive 연결 (`HYPERDRIVE` 바인딩) | 없음 — `src/lib/db.ts` 가 이미 지원 |
| 내 도메인 사용 | Cloudflare 에 도메인 연결 → Worker 에 Custom Domain, `PUBLIC_BASE_URL` 변경 | 없음 |

## 로컬에서 Cloudflare 실행 환경으로 시험하기 (선택, 개발자용)
```bash
npm run test:e2e:cf          # OpenNext 빌드 → wrangler dev(workerd) 로 E2E 16개 실행
```
윈도우에서 OpenNext 빌드가 실패하면 WSL 에서 실행하거나 4단계(Workers Builds)를 사용하세요.
