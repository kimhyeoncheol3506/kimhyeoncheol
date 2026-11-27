// 사이트 공통 정보와 페이지별 메타데이터(제목·설명·OG·canonical) 도우미
import type { Metadata } from "next";

export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL || "https://faceandfate.vercel.app").replace(/\/$/, "");
export const SITE_NAME = "얼굴과 운명";
export const OG_IMAGE = { url: "/og.png", width: 1440, height: 756, alt: "얼굴과 운명 — 사주 × 관상" };

type PageMetaInput = {
  title: string; // 탭 제목 (뒤에 ' | 얼굴과 운명' 이 붙음)
  description: string;
  path: string; // "/guide/ohaeng" 처럼 앞에 / 포함
  ogTitle?: string;
  image?: string; // OG 이미지 경로 (없으면 기본)
  noindex?: boolean; // 사람마다 다른 결과 화면처럼 검색에 올리지 않을 페이지
  absoluteTitle?: boolean; // 제목 뒤에 사이트 이름을 붙이지 않음
};

/** 페이지마다 고유한 제목·설명·OG·canonical 을 만든다 */
export function pageMeta({ title, description, path, ogTitle, image, noindex, absoluteTitle }: PageMetaInput): Metadata {
  const url = `${SITE_URL}${path === "/" ? "" : path}`;
  return {
    // 중첩 레이아웃에서도 제목 형식이 같도록 항상 완성된 제목을 넣음
    title: { absolute: absoluteTitle ? title : `${title} | ${SITE_NAME}` },
    description,
    alternates: { canonical: path },
    openGraph: {
      title: ogTitle ?? title,
      description,
      url,
      siteName: SITE_NAME,
      type: "website",
      locale: "ko_KR",
      images: [image ? { url: image, width: 1200, height: 630 } : OG_IMAGE],
    },
    twitter: { card: "summary_large_image", title: ogTitle ?? title, description, images: [image ?? OG_IMAGE.url] },
    ...(noindex ? { robots: { index: false, follow: true } } : {}),
  };
}

/** sitemap 에 넣을 고정 페이지 (해설 글·신년운세는 각 모듈에서 더함) */
export const STATIC_ROUTES: { path: string; priority: number; changeFrequency: "daily" | "weekly" | "monthly" | "yearly" }[] = [
  { path: "/", priority: 1, changeFrequency: "weekly" },
  { path: "/analyze", priority: 0.9, changeFrequency: "monthly" },
  { path: "/match", priority: 0.9, changeFrequency: "monthly" },
  { path: "/newyear", priority: 0.9, changeFrequency: "weekly" },
  { path: "/terms", priority: 0.3, changeFrequency: "yearly" },
  { path: "/privacy", priority: 0.3, changeFrequency: "yearly" },
  { path: "/disclaimer", priority: 0.3, changeFrequency: "yearly" },
  { path: "/open-source", priority: 0.2, changeFrequency: "yearly" },
];
