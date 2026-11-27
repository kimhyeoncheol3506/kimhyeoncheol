import Link from "next/link";
import GuideNotice from "@/components/GuideNotice";
import { GUIDES } from "@/lib/guide";
import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({
  title: "사주·관상 해설 — 쉽게 읽는 명리학과 관상 입문",
  description: "사주팔자, 오행, 띠와 입춘, 열 가지 별, 10년 흐름, 일간 10종, 관상 부위별 의미, 궁합 보는 법까지. 사주와 관상을 처음 접하는 사람도 이해할 수 있게 쉬운 말로 정리한 해설 모음입니다.",
  path: "/guide",
});

export default function GuideIndex() {
  const topics = GUIDES.filter((g) => g.kind === "topic");
  const ilgan = GUIDES.filter((g) => g.kind === "ilgan");
  return (
    <div className="px-5 pb-10 pt-6">
      <p className="eyebrow">Guide</p>
      <h1 className="mt-2 font-serif text-[28px] font-bold leading-tight">사주·관상 해설</h1>
      <p className="mt-3 text-[16px] leading-relaxed text-sub">
        결과 화면에 나오는 말들이 어디서 왔는지 궁금하셨나요? 사주와 관상의 기본 개념을 쉬운 말로 풀어 정리했습니다.
      </p>
      <div className="mt-5">
        <GuideNotice />
      </div>

      <h2 className="mt-9 font-serif text-[20px] font-bold">기초 개념</h2>
      <ul className="mt-3 space-y-2">
        {topics.map((g) => (
          <li key={g.slug}>
            <Link href={`/guide/${g.slug}`} className="card block !p-4">
              <span className="block text-[16px] font-semibold leading-snug">{g.title}</span>
              <span className="mt-1 line-clamp-2 block text-[14px] text-mute">{g.description}</span>
            </Link>
          </li>
        ))}
      </ul>

      <h2 className="mt-9 font-serif text-[20px] font-bold">일간 10종</h2>
      <ul className="mt-3 grid grid-cols-2 gap-2">
        {ilgan.map((g) => (
          <li key={g.slug}>
            <Link href={`/guide/${g.slug}`} className="card block h-full !p-4">
              <span className="block font-serif text-[22px] font-bold text-accent">{g.ilgan!.stem}</span>
              <span className="mt-1 block text-[15px] font-semibold">{g.ilgan!.ko}</span>
              <span className="mt-0.5 block text-[13px] leading-snug text-mute">{g.ilgan!.image}</span>
            </Link>
          </li>
        ))}
      </ul>

      <Link href="/analyze" className="btn-primary mt-10 w-full">
        내 사주·관상 무료로 보기
      </Link>
    </div>
  );
}
