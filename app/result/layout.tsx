import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({
  title: "나의 사주·관상 결과",
  description: "사주와 관상이 공통으로 말하는 성격·재물·연애·건강과 앞으로의 흐름입니다.",
  path: "/result",
  noindex: true, // 사람마다 다른 결과라 검색에는 올리지 않음
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
