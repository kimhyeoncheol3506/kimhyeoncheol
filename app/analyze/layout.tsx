import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({
  title: "사주·관상 무료로 보기",
  description: "생일·태어난 시간·성별과 얼굴 사진(선택)만 넣으면 3분 안에 사주와 관상을 함께 풀어 드립니다. 사진은 내 폰 안에서만 분석하고 서버에 저장하지 않습니다.",
  path: "/analyze",
  ogTitle: "사주 × 관상, 3분이면 끝나요",
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
