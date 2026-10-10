# 얼굴과 운명 — 무료 사주 × 관상 AI 웹사이트

생년월일과 얼굴 사진을 넣으면
1. **두 개의 사주 엔진**(ssaju, lunar-javascript)을 동시에 돌리고, 둘이 **같은 값을 낸 부분만** 채택합니다.
2. 얼굴 사진에서 **랜드마크 478점**을 뽑아(브라우저 안에서만) 전통 관상 규칙에 매핑합니다.
3. 사주와 관상이 **공통으로 가리키는 것**만 골라 ‘우리 의견’으로 정리합니다.
4. 성격 / 재물·직업 / 연애 / 건강 / 앞으로 3년 / 주의사항 / 당부까지 보여 주고,
5. **플레이 버튼**을 누르면 AI 목소리로 전체를 읽어 줍니다.

> 사진과 생년월일은 서버로 보내지 않고 저장하지도 않습니다.

---

## 🚀 런칭 가이드 (코딩 몰라도 됩니다 — 순서대로 클릭만)

준비물: 이 GitHub 저장소(이미 있음), 인터넷 브라우저. **돈은 들지 않습니다.**

### 1단계. 사이트 올리기 (Vercel, 무료) — 약 5분

1. https://vercel.com/signup 접속 → **Continue with GitHub** 클릭 → GitHub 계정으로 로그인
2. 화면의 **Add New… → Project** 클릭
3. 목록에서 **`kimhyeoncheol`** 저장소 옆의 **Import** 클릭
   (목록에 없으면 *Adjust GitHub App Permissions* 를 눌러 이 저장소를 허용)
4. 설정은 그대로 두고 **Deploy** 클릭
5. 1~2분 뒤 🎉 화면이 나오면 완료. `https://kimhyeoncheol-xxxx.vercel.app` 같은 주소가 생깁니다.
   → **이 주소를 휴대폰으로 열어 바로 테스트하세요.**

이 상태에서도 사이트는 **완전히 동작**합니다(로그인 없는 테스트 모드 + 규칙 기반 해석).
아래 2~4단계는 기능을 하나씩 켜는 선택 사항입니다.

> 이후 GitHub에 코드가 바뀌면 Vercel이 **자동으로 다시 배포**합니다.

### 2단계. 회원가입 켜기 (Supabase, 무료) — 약 10분

1. https://supabase.com → **Start your project** → GitHub로 로그인
2. **New project** → 이름 아무거나(예: `fate`), 데이터베이스 비밀번호 입력(메모해 두기), Region은 **Northeast Asia (Seoul)** → **Create**
3. 프로젝트가 만들어지면 왼쪽 아래 ⚙️ **Project Settings → API** (또는 **Data API / API Keys**) 에서 두 값을 복사
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** 키 → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. 왼쪽 메뉴 **Authentication → URL Configuration** 에서
   - **Site URL** 에 1단계에서 받은 Vercel 주소 입력 (예: `https://kimhyeoncheol-xxxx.vercel.app`)
   - **Redirect URLs** 에 `https://kimhyeoncheol-xxxx.vercel.app/**` 추가
5. Vercel로 돌아가서 프로젝트 → **Settings → Environment Variables** 에 3번의 두 값을 각각 추가 → **Save**
6. **Deployments** 탭 → 가장 위 배포의 `⋯` → **Redeploy**

이제 **분석/결과 페이지는 회원만** 볼 수 있습니다. 가입하면 확인 메일이 오고, 링크를 누르면 가입 완료.
(테스트할 때 메일 인증이 귀찮으면 Supabase **Authentication → Sign In / Providers → Email → Confirm email** 을 끄면 바로 가입됩니다.)
가입한 회원 목록은 Supabase **Authentication → Users** 에서 볼 수 있습니다.

### 3단계. AI 해석 켜기 (Claude, 유료·선택)

키가 없어도 규칙 기반으로 결과가 나옵니다. 더 자연스러운 문장을 원할 때만 켜세요.

1. https://console.anthropic.com 가입 → **Billing** 에서 크레딧 충전(소액 가능)
2. **API Keys → Create Key** → 키 복사 (`sk-ant-...`)
3. Vercel **Settings → Environment Variables** 에 `ANTHROPIC_API_KEY` = 복사한 키 → Save → **Redeploy**

결과 페이지 맨 아래에 “해석 문장: AI(Claude)가 … 작성” 이라고 나오면 켜진 것입니다.
기본 모델은 `claude-opus-5-5` 이고, 비용을 줄이고 싶으면 `ANTHROPIC_MODEL` 변수로 바꿀 수 있습니다.

### 3-1단계. ElevenLabs 목소리 켜기 (유료·선택) — 약 5분

키가 없으면 휴대폰/PC에 들어 있는 무료 목소리로 읽습니다. 더 자연스러운 한국어 목소리를 원하면:

1. https://elevenlabs.io 가입 → 요금제 선택 (무료 플랜도 월 일정 글자 수 제공, 상업적 이용은 유료 플랜 필요)
2. **Voices → Voice Library** 에서 언어를 **Korean** 으로 거른 뒤 마음에 드는 목소리의 **Add to My Voices**
3. 오른쪽 위 프로필 → **API Keys → Create API Key** → 키 복사
4. Vercel **Settings → Environment Variables** 에 `ELEVENLABS_API_KEY` = 복사한 키 → Save → **Redeploy**

- 목소리는 **내 목소리 목록에서 한국어 목소리를 자동으로** 고릅니다. 특정 목소리로 고정하려면 그 목소리의 ID를 `ELEVENLABS_VOICE_ID` 에 넣으세요.
- 모델은 최신 **Eleven v4** 를 먼저 쓰고, 계정에서 안 되면 v3 → Multilingual v2 로 자동 전환합니다.
- 비용: 결과 1회 전체 낭독이 약 2,000~4,000자입니다. 실제로 재생한 부분만 글자 수가 차감됩니다.
- 오류가 나거나 크레딧이 떨어지면 자동으로 무료 브라우저 목소리로 바뀝니다.

### 4단계. 카카오톡 공유 버튼 (선택)

키가 없어도 휴대폰에서는 기본 공유창(카톡 포함)이 뜹니다. 카카오 전용 공유 카드를 원하면:

1. https://developers.kakao.com → 로그인 → **내 애플리케이션 → 애플리케이션 추가하기**
2. **앱 키 → JavaScript 키** 복사
3. **플랫폼 → Web 플랫폼 등록** 에 Vercel 주소 입력
4. Vercel 환경변수 `NEXT_PUBLIC_KAKAO_JS_KEY` 추가 → Redeploy

### 5단계. 내 도메인 연결 (선택)

도메인(예: `myfate.kr`)을 가비아·카페24 등에서 구매 → Vercel **Settings → Domains → Add** → 안내대로 DNS 설정.
연결 후 환경변수 `NEXT_PUBLIC_SITE_URL` 에 새 주소를 넣고, Supabase **Site URL** 도 새 주소로 바꿔 주세요.

---

## ✅ 테스트 체크리스트

- [ ] 휴대폰으로 사이트 접속 → “지금 바로 무료로 보기”
- [ ] (2단계 했다면) 회원가입 → 메일 인증 → 로그인
- [ ] 생년월일·시간·성별 입력, **카메라 촬영**으로 얼굴 찍기 → 분석 시작
- [ ] 결과 페이지: 사주팔자 4기둥, 오행, 공통 의견, 6개 섹션, 당부
- [ ] 아래쪽 빨간 **플레이 버튼** → 목소리로 읽어 주는지 (휴대폰 무음 모드 해제!)
- [ ] 카카오톡 / 이미지 저장 / 링크 복사
- [ ] 음력, “시간 모름”으로도 한 번씩

얼굴을 못 찾으면: 정면, 밝은 곳, 얼굴이 화면의 1/3 이상 차도록 찍어 주세요. 그래도 안 되면 “사진 없이 사주만 보기” 버튼이 나옵니다.

---

## 🛠 내 컴퓨터에서 실행하기 (개발자용 / 선택)

```bash
# Node.js 20 이상 필요 (https://nodejs.org)
npm install          # 패키지 설치 (얼굴 분석 엔진 파일도 자동 복사)
cp .env.example .env.local   # 필요한 키만 채우기 (비워도 동작)
npm run dev          # http://localhost:3000 열기
npm run build        # 배포용 빌드 확인
```

## 📁 폴더 구조

```
app/
  page.tsx              랜딩 (/)
  analyze/page.tsx      입력 (/analyze) — 생년월일·성별·사진
  result/page.tsx       결과 (/result) — 사주판·공통 의견·섹션·낭독·공유
  login, signup/        회원가입·로그인 (Supabase)
  disclaimer, privacy, open-source/   면책조항·개인정보·오픈소스 고지
  api/interpret/route.ts   Claude 해석 API (키 없으면 꺼짐)
  api/tts/route.ts         ElevenLabs 목소리 API (키 없으면 꺼짐)
components/             헤더·푸터·히어로 그래픽·사주판·플레이어·공유 버튼
lib/
  saju/                 엔진 A(ssaju) · 엔진 B(lunar-javascript + 자체 규칙) · 공통 결과(consensus)
  face/                 랜드마크 추출(MediaPipe) · 비율 측정 · 관상 규칙
  reading/              공통 테마 · 규칙 기반 해석 문장
  tts.ts                낭독 (ElevenLabs → 실패 시 브라우저 목소리)
  auth/                 Supabase 로그인
public/models/          얼굴 분석 모델 파일
```

## 🎨 디자인 시스템

| 토큰 | 값 | 용도 |
|---|---|---|
| `ink` | `#0A0A0A` | 메인 검정 |
| `paper` | `#FFFFFF` | 메인 흰색 |
| `accent` | `#E11D48` | 포인트 컬러 (한 화면 1~2곳만) |
| `mute` / `line` / `smoke` | `#757575` / `#E5E5E5` / `#F5F5F5` | 보조 |
| 폰트 | Pretendard Variable | 제목은 900(Black), 자간 -4% |
| 버튼 | 모서리 0, 높이 60px 이상 | 날카롭고 큰 터치 영역 |

설정 위치: `tailwind.config.ts`, `app/globals.css`

## ⚖️ 라이선스·법적 주의

- **ssaju**(MIT), **lunar-javascript**(MIT), **MediaPipe**(Apache-2.0)를 사용합니다.
- **orrery(AGPL)** 코드는 복사하지 않았습니다. 신강·용신 판단과 공통 결과 선별은 이 프로젝트가 독자 구현했습니다.
- 모든 결과 페이지 하단에 면책조항이 표시됩니다: “본 서비스는 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다.”
- 광고(애드센스 등)를 붙일 때는 개인정보처리방침에 해당 광고사의 쿠키 사용을 추가해야 합니다.
