import NewYearClient from "@/components/newyear/NewYearClient";
import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({
  title: "2027 정미년 신년운세 — 무료 총운·월별 운세",
  ogTitle: "2027 정미년, 나의 한 해는?",
  description: "생년월일로 보는 2027년 정미년(붉은 양의 해) 신년운세. 한 해 총운과 2월부터 이듬해 1월까지 달마다 한 줄 운세를 무료로 보고, 월별 상세·재물·연애·직장·건강 리포트까지 확인하세요.",
  path: "/newyear",
});

// NEWYEAR_PAID=true 이면 상세 리포트를 '12월 오픈 예정'으로 잠그고, 아니면(기본) 지금 무료로 모두 공개
const PAID = process.env.NEWYEAR_PAID === "true";

export default function NewYearPage() {
  return <NewYearClient locked={PAID} />;
}
