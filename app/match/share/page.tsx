import Link from "next/link";
import MatchScoreCard from "@/components/MatchScoreCard";
import { SCORE_LABELS, fromShareQuery, relationLabel } from "@/lib/match/share";
import { pageMeta } from "@/lib/site";

type SP = { [k: string]: string | string[] | undefined };
const getter = (sp: SP) => (k: string) => {
  const v = sp[k];
  return typeof v === "string" ? v : null;
};

export function generateMetadata({ searchParams }: { searchParams: SP }) {
  const d = fromShareQuery(getter(searchParams));
  const q = new URLSearchParams(Object.entries(searchParams).filter((e): e is [string, string] => typeof e[1] === "string")).toString();
  return pageMeta({
    title: d ? `${d.names[0]} × ${d.names[1]} 궁합 ${d.total}점` : "궁합 결과 공유",
    ogTitle: d ? `우리 궁합은 ${d.total}점 — ${d.headline}` : "그 사람과 나, 궁합은 몇 점일까?",
    description: d
      ? `${SCORE_LABELS.map((l, i) => `${l} ${d.scores[i]}`).join(" · ")}. 사주로 보는 궁합, 너도 무료로 확인해 보세요.`
      : "두 사람의 생년월일로 보는 사주 궁합 점수. 무료로 확인해 보세요.",
    path: "/match/share",
    image: d ? `/api/og/match?${q}` : undefined,
    noindex: true, // 사람마다 다른 결과
  });
}

export default function MatchSharePage({ searchParams }: { searchParams: SP }) {
  const d = fromShareQuery(getter(searchParams));
  return (
    <div className="px-5 pb-16 pt-6">
      <p className="eyebrow text-center">Shared Result</p>
      <h1 className="mt-2 text-center font-serif text-[24px] font-bold">친구가 궁합 결과를 보냈어요</h1>
      <div className="mt-6">
        {d ? (
          <MatchScoreCard names={d.names} relation={relationLabel(d.relation)} total={d.total} headline={d.headline} scores={d.scores} leader={d.leader} />
        ) : (
          <p className="card text-center text-[15px] text-mute">결과 링크가 올바르지 않아요. 아래에서 직접 궁합을 봐 주세요.</p>
        )}
      </div>
      {d?.bestMonth && <p className="mt-4 text-center text-[15px] text-sub">두 사람에게 가장 좋은 달은 <b>{d.bestMonth}</b>이에요.</p>}
      <Link href="/match" className="btn-primary mt-8 w-full">
        나도 궁합 보기 (무료)
      </Link>
      <Link href="/analyze" className="btn-ghost mt-2 w-full">
        내 사주·관상 보기
      </Link>
      <p className="mt-6 text-center text-[13px] leading-relaxed text-mute">
        공유 링크에는 이름과 점수만 담기며 생년월일·사진은 포함되지 않습니다. 궁합은 재미와 참고용이에요.{" "}
        <Link href="/guide/gunghap" className="underline">궁합 보는 법</Link>
      </p>
    </div>
  );
}
