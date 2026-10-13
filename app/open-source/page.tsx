import LegalPage from "@/components/LegalPage";

export const metadata = { title: "오픈소스 고지" };

const LIBS = [
  ["ssaju", "MIT", "사주 엔진 A (만세력·십성·대운·용신)", "https://github.com/golbin/ssaju"],
  ["lunar-javascript", "MIT", "사주 엔진 B (만세력·십신·대운)", "https://github.com/6tail/lunar-javascript"],
  ["MediaPipe Tasks Vision", "Apache-2.0", "얼굴 랜드마크 추출 (브라우저 내 실행)", "https://github.com/google-ai-edge/mediapipe"],
  ["Next.js", "MIT", "웹 프레임워크", "https://github.com/vercel/next.js"],
  ["Tailwind CSS", "MIT", "스타일", "https://github.com/tailwindlabs/tailwindcss"],
  ["Framer Motion", "MIT", "애니메이션", "https://github.com/motiondivision/motion"],
  ["Pretendard", "OFL-1.1", "글꼴", "https://github.com/orioncactus/pretendard"],
  ["Supabase JS", "MIT", "회원 인증", "https://github.com/supabase/supabase-js"],
  ["html-to-image", "MIT", "결과 이미지 저장", "https://github.com/bubkoo/html-to-image"],
];

export default function Page() {
  return (
    <LegalPage eyebrow="Open source" title="오픈소스 고지" updated="2026년 10월 10일">
      <section>
        <p className="!mt-0">
          이 서비스는 오픈소스 엔진을 기반으로 두 사주 엔진의 공통 결과를 도출합니다. 신강·신약 및 용신 판단 규칙, 공통 결과 선별,
          관상 규칙 매핑은 이 서비스가 독자적으로 구현했습니다. AGPL 라이선스 프로젝트(예: orrery)의 코드는 포함하지 않았습니다.
        </p>
      </section>
      <section>
        <div className="border-t border-line">
          {LIBS.map(([n, l, d, u]) => (
            <a key={n} href={u} target="_blank" rel="noreferrer" className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line py-4 active:bg-smoke">
              <span className="font-bold">{n}</span>
              <span className="text-sm text-mute">{d} · {l}</span>
            </a>
          ))}
        </div>
      </section>
    </LegalPage>
  );
}
