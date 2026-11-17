import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({
  title: "궁합 결과",
  description: "두 사람의 사주로 본 궁합 점수와 항목별 풀이입니다.",
  path: "/match/result",
  noindex: true, // 사람마다 다른 결과라 검색에는 올리지 않음
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
