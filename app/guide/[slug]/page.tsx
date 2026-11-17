import Link from "next/link";
import { notFound } from "next/navigation";
import GuideNotice from "@/components/GuideNotice";
import { GUIDES, guideBySlug } from "@/lib/guide";
import { ILGAN } from "@/lib/guide/ilgan";
import { SITE_NAME, SITE_URL, pageMeta } from "@/lib/site";

export const dynamicParams = false;
export const generateStaticParams = () => GUIDES.map((g) => ({ slug: g.slug }));
export function generateMetadata({ params }: { params: { slug: string } }) {
  const g = guideBySlug(params.slug);
  return g ? pageMeta({ title: g.title, description: g.description, path: `/guide/${g.slug}` }) : {};
}

export default function GuideArticle({ params }: { params: { slug: string } }) {
  const g = guideBySlug(params.slug);
  if (!g) notFound();
  const related = g.related.map((s) => guideBySlug(s)).filter(Boolean);
  const url = `${SITE_URL}/guide/${g.slug}`;
  const jsonLd = [
    {
      "@context": "https://schema.org",
      "@type": "Article",
      headline: g.title,
      description: g.description,
      inLanguage: "ko",
      mainEntityOfPage: url,
      author: { "@type": "Organization", name: SITE_NAME },
      publisher: { "@type": "Organization", name: SITE_NAME },
    },
    {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "홈", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "해설", item: `${SITE_URL}/guide` },
        { "@type": "ListItem", position: 3, name: g.title, item: url },
      ],
    },
  ];

  return (
    <article className="px-5 pb-10 pt-6">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <nav className="text-[13px] text-mute" aria-label="위치">
        <Link href="/" className="underline-offset-2 hover:underline">홈</Link> ›{" "}
        <Link href="/guide" className="underline-offset-2 hover:underline">해설</Link>
      </nav>
      {g.ilgan && <p className="mt-4 font-serif text-[44px] font-bold leading-none text-accent">{g.ilgan.stem}</p>}
      <h1 className="mt-3 font-serif text-[26px] font-bold leading-snug">{g.title}</h1>
      <p className="mt-4 text-[17px] leading-[1.8] text-sub">{g.lead}</p>

      <div className="mt-8 space-y-8">
        {g.sections.map((s) => (
          <section key={s.h}>
            <h2 className="font-serif text-[20px] font-bold">{s.h}</h2>
            {s.body.map((p, i) => (
              <p key={i} className="mt-3 text-[16px] leading-[1.85] text-ink/90">
                {p}
              </p>
            ))}
            {s.list && (
              <ul className="mt-3 space-y-2">
                {s.list.map((li) => (
                  <li key={li} className="flex gap-2 text-[16px] leading-[1.7] text-ink/90">
                    <span className="mt-[11px] h-1.5 w-1.5 shrink-0 rounded-full bg-accent" aria-hidden />
                    <span>{li}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>

      {g.slug === "ilgan-overview" && (
        <ul className="mt-6 grid grid-cols-2 gap-2">
          {ILGAN.map((il) => (
            <li key={il.slug}>
              <Link href={`/guide/${il.slug}`} className="card block h-full !p-4">
                <span className="font-serif text-[20px] font-bold text-accent">{il.stem}</span>{" "}
                <span className="text-[15px] font-semibold">{il.ko}</span>
                <span className="mt-1 block text-[13px] leading-snug text-mute">{il.summary}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-10">
        <GuideNotice />
      </div>

      <div className="card mt-6 text-center">
        <p className="font-serif text-[18px] font-bold">내 사주로 직접 확인해 보세요</p>
        <p className="mt-1 text-[14px] text-mute">생일만 넣으면 3분, 사진은 내 폰에서만 분석해요.</p>
        <div className="mt-4 grid grid-cols-2 gap-2">
          <Link href="/analyze" className="btn-primary">사주·관상 보기</Link>
          <Link href="/match" className="btn-ghost">궁합 보기</Link>
        </div>
        {g.slug === "newyear-2027" && (
          <Link href="/newyear" className="btn-primary mt-2 w-full">
            2027 신년운세 무료로 보기
          </Link>
        )}
      </div>

      {related.length > 0 && (
        <section className="mt-10">
          <h2 className="font-serif text-[18px] font-bold">함께 읽으면 좋은 글</h2>
          <ul className="mt-3 divide-y divide-line border-y border-line">
            {related.map((r) => (
              <li key={r!.slug}>
                <Link href={`/guide/${r!.slug}`} className="flex items-center justify-between gap-3 py-3.5 text-[15px] font-medium">
                  <span>{r!.title}</span>
                  <span className="text-accent" aria-hidden>›</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link href="/guide" className="mt-4 inline-block text-[14px] font-semibold text-accent">해설 전체 보기 ›</Link>
        </section>
      )}
    </article>
  );
}
