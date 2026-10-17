import type { InquirySource } from "@prisma/client";
import { won } from "@/lib/format";
import { BUSINESS_TYPE_LABEL, LINK_KIND_LABEL, type ParsedInquiry } from "./parser";
import type { MediaPlan, TierKey } from "./planner";

/**
 * 고객 답변 초안 (템플릿). 담당자가 검토·수정 후 발송한다.
 * 성과 보장·상위노출 보장 표현을 쓰지 않고, 플랫폼 밖 직접 결제를 유도하지 않는다.
 */
export function buildReply(
  input: { customerName: string; source: InquirySource; parsed: ParsedInquiry; plan: MediaPlan; selectedTier?: TierKey | null; senderName?: string },
): string {
  const { parsed, plan } = input;
  const subject = parsed.brand ? `‘${parsed.brand}’ ` : "";
  const lines: string[] = [];
  lines.push(`${input.customerName}님 안녕하세요, 문의 감사합니다!`);
  lines.push("");

  // 1) 문의 내용 확인
  const confirm: string[] = [];
  confirm.push(`업종: ${BUSINESS_TYPE_LABEL[parsed.businessType]}`);
  if (parsed.links.length) confirm.push(`확인할 채널: ${parsed.links.map((l) => LINK_KIND_LABEL[l.kind]).join(", ")}`);
  if (parsed.keywords.length) confirm.push(`희망 키워드: ${parsed.keywords.join(", ")}`);
  lines.push(`보내주신 ${subject}내용 확인했습니다.`);
  for (const c of confirm) lines.push(`- ${c}`);
  lines.push("");

  // 2) 진행 가능 여부
  const requested = plan.channels.filter((c) => c.requested);
  if (requested.length) {
    const ok = requested.filter((c) => c.available).map((c) => c.label);
    const no = requested.filter((c) => !c.available).map((c) => c.label);
    if (ok.length) lines.push(`요청하신 ${ok.join(", ")} 진행 가능합니다 :)`);
    if (no.length) lines.push(`${no.join(", ")}은(는) 현재 저희가 직접 제공하지 않는 상품이라 별도로 안내드리겠습니다.`);
    if (parsed.keywords.length) lines.push("키워드별 검색량·경쟁 정도를 확인한 뒤 키워드 구성을 최종 제안드리겠습니다.");
    lines.push("");
  }

  // 3) 추천 매체
  const rec = plan.channels.filter((c) => c.available).slice(0, 5);
  if (rec.length) {
    lines.push(`[${BUSINESS_TYPE_LABEL[parsed.businessType]} 기준 추천 광고 구성]`);
    rec.forEach((c, i) => lines.push(`${i + 1}. ${c.label} — ${c.reason.replace(/^고객 요청 · /, "")}`));
    lines.push("");
  }

  // 4) 견적
  lines.push("[예상 견적]");
  for (const t of plan.tiers) {
    if (!t.items.length) continue;
    const mark = t.key === (input.selectedTier ?? plan.recommendedTier) ? " (추천)" : "";
    lines.push(`■ ${t.label}${mark}: ${won(t.total)}`);
    for (const it of t.items) lines.push(`  · ${it.name} ${it.quantity > 1 ? `× ${it.quantity}` : ""} (${it.unit} 기준)`.replace(/\s+\(/, " ("));
    if (t.mediaSpend) lines.push(`  · 광고 매체비 별도 — 월 ${won(t.mediaSpend.min)} ~ ${won(t.mediaSpend.max)} 권장`);
  }
  if (plan.fullPackage) lines.push(`※ 여러 매체를 한 번에 맡기시는 ‘${plan.fullPackage.name}’ 상품은 ${won(plan.fullPackage.unitPrice)}/${plan.fullPackage.unit}입니다.`);
  if (parsed.questions.includes("BUDGET")) {
    lines.push("");
    lines.push("예산은 처음 1~2개월은 실속형·표준형으로 시작해 반응을 확인한 뒤 성과가 좋은 매체에 늘리는 방식을 권해 드립니다.");
  }
  lines.push("");

  // 5) 진행 절차와 요청 자료
  lines.push("[진행 절차]");
  lines.push("상담·구성 확정 → 자료 전달 → 원고·소재 제작 및 고객 검수 → 집행 → 결과 리포트 전달");
  if (parsed.missingInfo.length) {
    lines.push("");
    lines.push("정확한 견적을 위해 아래 내용을 알려주시면 감사하겠습니다.");
    for (const m of parsed.missingInfo) lines.push(`- ${m}`);
  }
  lines.push("");

  // 6) 고지
  lines.push("※ 모든 홍보 콘텐츠에는 광고·협찬 표시를 하며, 상위노출이나 매출 등 특정 성과를 보장해 드리지는 않습니다.");
  if (parsed.referencesCompetitor) lines.push("※ 참고하신 업체의 광고는 방향만 참고하고, 콘텐츠는 새로 제작합니다.");
  if (input.source === "KMONG") lines.push("※ 결제는 크몽 안전결제를 통해 진행됩니다.");
  lines.push("");
  lines.push(`편하게 문의 주세요. 감사합니다!${input.senderName ? `\n${input.senderName} 드림` : ""}`);
  return lines.join("\n");
}
