import { z } from "zod";
import { checkUrl } from "./url";

const list = z
  .string()
  .optional()
  .transform((v) =>
    (v ?? "")
      .split(/[,\n]/)
      .map((s) => s.trim())
      .filter(Boolean),
  );

const optionalUrl = z
  .string()
  .trim()
  .optional()
  .transform((v) => (v ? v : undefined))
  .refine((v) => !v || checkUrl(v).valid, { message: "올바른 http(s) URL 을 입력하세요. (내부망 주소 불가)" });

const optionalDate = z
  .string()
  .optional()
  .transform((v) => (v ? new Date(v) : undefined))
  .refine((d) => !d || !Number.isNaN(d.getTime()), { message: "날짜 형식이 올바르지 않습니다." });

const money = z.coerce.number({ invalid_type_error: "숫자를 입력하세요." }).int().min(0, "0 이상이어야 합니다.").max(10_000_000_000);

export const clientSchema = z
  .object({
    name: z.string().trim().min(1, "고객명을 입력하세요.").max(100),
    contactName: z.string().trim().min(1, "담당자명을 입력하세요.").max(50),
    contactEmail: z
      .string()
      .trim()
      .optional()
      .transform((v) => v || undefined)
      .refine((v) => !v || z.string().email().safeParse(v).success, { message: "이메일 형식이 올바르지 않습니다." }),
    contactPhone: z.string().trim().max(30).optional(),
    promoUrl: optionalUrl,
    companyIntro: z.string().trim().max(2000).optional().default(""),
    productDescription: z.string().trim().max(3000).optional().default(""),
    coreTarget: z.string().trim().max(500).optional().default(""),
    bannedPhrases: list,
    requiredPhrases: list,
    toneOfVoice: z.string().trim().max(500).optional().default(""),
    budget: money,
    contractStart: optionalDate,
    contractEnd: optionalDate,
    managerId: z
      .string()
      .optional()
      .transform((v) => v || undefined),
  })
  .refine((v) => !v.contractStart || !v.contractEnd || v.contractStart <= v.contractEnd, {
    message: "계약 종료일은 시작일 이후여야 합니다.",
    path: ["contractEnd"],
  });

export type ClientInput = z.infer<typeof clientSchema>;

export const TARGET_TYPES = ["BLOG", "YOUTUBE", "SHORTS", "REELS", "APP", "PRODUCT", "OTHER"] as const;
export const GOALS = ["VIEWS", "CLICKS", "VISITS", "INSTALLS", "INQUIRIES", "PURCHASES"] as const;
export const PLATFORM_KEYS = ["INSTAGRAM", "TIKTOK", "X", "FACEBOOK", "YOUTUBE", "BLOG"] as const;

export const briefSchema = z
  .object({
    clientId: z.string().min(1, "고객을 선택하세요."),
    title: z.string().trim().min(2, "의뢰 제목을 2자 이상 입력하세요.").max(120),
    targetUrl: optionalUrl,
    targetType: z.enum(TARGET_TYPES, { errorMap: () => ({ message: "홍보 대상 유형을 선택하세요." }) }),
    goal: z.enum(GOALS, { errorMap: () => ({ message: "주요 목표를 선택하세요." }) }),
    coreTarget: z.string().trim().max(500).optional().default(""),
    budget: money,
    startDate: optionalDate,
    endDate: optionalDate,
    desiredPlatforms: z.array(z.enum(PLATFORM_KEYS)).min(1, "희망 SNS 를 하나 이상 선택하세요."),
    keywords: list,
    bannedKeywords: list,
    description: z.string().trim().max(5000).optional().default(""),
  })
  .refine((v) => !v.startDate || !v.endDate || v.startDate <= v.endDate, {
    message: "종료일은 시작일 이후여야 합니다.",
    path: ["endDate"],
  });

export type BriefInput = z.infer<typeof briefSchema>;

export const candidateSchema = z.object({
  platform: z.enum(PLATFORM_KEYS),
  accountName: z.string().trim().min(1, "계정명을 입력하세요.").max(100),
  profileUrl: optionalUrl,
  postUrl: z
    .string()
    .trim()
    .min(1, "게시물 URL 을 입력하세요.")
    .refine((v) => checkUrl(v).valid, { message: "올바른 게시물 URL 을 입력하세요." }),
  title: z.string().trim().min(1, "게시물 제목을 입력하세요.").max(200),
  summary: z.string().trim().max(2000).optional().default(""),
});

export type CandidateInput = z.infer<typeof candidateSchema>;

export const policySchema = z.object({
  platform: z.enum(PLATFORM_KEYS),
  policyUrl: z
    .string()
    .trim()
    .refine((v) => checkUrl(v).valid, { message: "공식 정책 URL 을 입력하세요." }),
  status: z.enum(["NOT_REVIEWED", "IN_PROGRESS", "COMPLETED"]),
  lastReviewedAt: optionalDate,
  nextReviewAt: z
    .string()
    .min(1, "다음 검토 예정일을 입력하세요.")
    .transform((v) => new Date(v)),
  changeSummary: z.string().trim().max(3000).optional().default(""),
  affectedFeatures: list,
  riskLevel: z.enum(["LOW", "MEDIUM", "HIGH"]),
  ownerId: z
    .string()
    .optional()
    .transform((v) => v || undefined),
  actionItems: z.string().trim().max(3000).optional().default(""),
  result: z.string().trim().max(3000).optional().default(""),
});

export type PolicyInput = z.infer<typeof policySchema>;

export const userSchema = z.object({
  name: z.string().trim().min(1, "이름을 입력하세요.").max(50),
  email: z.string().trim().toLowerCase().email("이메일 형식이 올바르지 않습니다."),
  role: z.enum(["ADMIN", "CAMPAIGN_MANAGER", "CONTENT_WRITER", "REVIEWER", "VIEWER"]),
  password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다.").max(100),
});

/** FormData → 평범한 객체 (다중 값 필드는 배열) */
export function formToObject(fd: FormData, arrayFields: string[] = []): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const key of new Set(fd.keys())) {
    if (key.startsWith("$ACTION")) continue;
    out[key] = arrayFields.includes(key) ? fd.getAll(key).map(String) : String(fd.get(key) ?? "");
  }
  for (const k of arrayFields) if (!(k in out)) out[k] = [];
  return out;
}

export function zodErrors(err: z.ZodError): Record<string, string> {
  const out: Record<string, string> = {};
  for (const issue of err.issues) {
    const k = issue.path.join(".") || "_form";
    if (!out[k]) out[k] = issue.message;
  }
  return out;
}
