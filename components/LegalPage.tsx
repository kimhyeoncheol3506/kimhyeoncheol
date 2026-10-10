/** 면책조항·개인정보처리방침 같은 문서 페이지 레이아웃 */
export default function LegalPage({ eyebrow, title, updated, children }: { eyebrow: string; title: string; updated: string; children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-page px-5 pb-28 pt-14 md:px-10 md:pt-24">
      <p className="label">{eyebrow}</p>
      <h1 className="mt-4 text-headline font-black">{title}</h1>
      <p className="mt-4 text-sm text-mute">최종 수정일 {updated}</p>
      <div className="mt-14 max-w-3xl space-y-10 text-[17px] leading-[1.8] [&_h2]:text-2xl [&_h2]:font-black [&_h2]:tracking-tight [&_li]:ml-5 [&_li]:list-disc [&_ul]:mt-3 [&_ul]:space-y-2 [&_p]:mt-3">
        {children}
      </div>
    </div>
  );
}
