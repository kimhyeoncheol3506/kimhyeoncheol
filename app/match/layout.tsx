import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({
  title: "궁합 보기 — 사주·관상 궁합 점수",
  description: "두 사람의 생년월일로 끌림·대화·채움·생활·앞날 다섯 가지 궁합 점수를 보고, 사진을 넣으면 관상 궁합까지 확인하세요. 짝사랑·썸·연인·부부 사이에 맞춘 좋은 달도 알려 드립니다.",
  path: "/match",
  ogTitle: "그 사람과 나, 궁합은 몇 점일까?",
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
