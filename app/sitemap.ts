import type { MetadataRoute } from "next";
import { SITE_URL, STATIC_ROUTES } from "@/lib/site";
import { GUIDES } from "@/lib/guide";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  const routes = [
    ...STATIC_ROUTES,
    { path: "/guide", priority: 0.8, changeFrequency: "weekly" as const },
    ...GUIDES.map((g) => ({ path: `/guide/${g.slug}`, priority: 0.7, changeFrequency: "monthly" as const })),
  ];
  return routes.map((r) => ({
    url: `${SITE_URL}${r.path === "/" ? "" : r.path}`,
    lastModified: now,
    changeFrequency: r.changeFrequency,
    priority: r.priority,
  }));
}
