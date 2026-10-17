# AIMAX OS — Claude Code 작업 규칙

사용자는 **비개발자 CEO**입니다. 설명은 쉬운 한국어로, 무엇을 바꿨는지 짧게 알려 주세요.

## 기술 스택
- Next.js 14 (App Router) + TypeScript + Tailwind CSS 3. 외부 UI 라이브러리 없음.
- 데이터: `lib/store.tsx` (React Context + localStorage). 모든 화면은 `useStore()` 로만 데이터를 읽고 씁니다.
- 실행: `npm run dev` (포트 3100). 검사: `npm run typecheck`, `npm run build`.

## 구조 규칙
- 데이터 모양은 `lib/types.ts` → 예시 데이터 `lib/seed.ts` → 한글 표시 `lib/labels.ts` 순서로 추가.
  새 컬렉션은 `Collections` 타입과 `seed` 양쪽에 추가하면 `add/update/remove` 를 그대로 쓸 수 있습니다.
- 새 메뉴: `app/<이름>/page.tsx` 생성 + `components/Sidebar.tsx` 의 `MENU` 에 한 줄 추가.
- 페이지 파일(`page.tsx`)에서는 default export 외의 컴포넌트를 export 하지 말 것 (빌드 오류). 공용 부품은 `components/`.
- 공통 스타일 클래스: `card`, `btn`, `btn-primary`, `input`, `label`, `th`, `td` (`app/globals.css`).
  색은 `brand`, `ink`, `sub`, `mute`, `line`, `canvas` 토큰만 사용 (`tailwind.config.ts`).
- 상태 표시는 `components/Badge.tsx` + `lib/labels.ts` 의 라벨을 사용.
- 날짜는 `lib/format.ts` 의 `nowStamp()/today()` 문자열로 저장 (시간대 차이로 인한 화면 불일치 방지).
- 외부 서비스 연동은 `lib/integrations/<서비스>.ts` (서버 전용) + `app/api/<서비스>/.../route.ts`.
  비밀 키는 `.env.local` 에만 두고 `NEXT_PUBLIC_` 접두사를 붙이지 말 것.

## 오류 처리 원칙
- 실패할 수 있는 작업(외부 API 등)은 try/catch 후 `logError({ title, message, page, severity })` 로
  오류 센터에 남기고, 화면에는 쉬운 안내 문구를 보여 줍니다.
- 처리되지 않은 오류는 `components/ErrorCatcher.tsx` 와 `app/error.tsx` 가 자동 기록합니다.
- CEO가 붙여넣는 "[AIMAX OS 오류 보고]" 텍스트를 받으면: 원인 파일을 찾고, 최소한으로 고치고,
  `npm run build` 로 확인한 뒤 결과를 쉬운 말로 설명합니다.

## 변경 후 확인
`npm run typecheck && npm run build` 가 통과해야 합니다.
