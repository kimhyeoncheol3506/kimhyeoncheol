/** 면책조항·개인정보처리방침 같은 문서 페이지 레이아웃 */
export default function LegalPage({ eyebrow, title, updated, children }: { eyebrow: string; title: string; updated: string; children: React.ReactNode }) {
  return (
    <div className="px-5 pb-16 pt-4">
      <p className="label">{eyebrow}</p>
      <h1 className="mt-2 text-headline font-bold">{title}</h1>
      <p className="mt-2 text-[13px] text-mute">최종 수정일 {updated}</p>
      <div className="mt-8 space-y-8 text-[15px] leading-[1.75] text-sub [&_b]:text-ink [&_h2]:text-[17px] [&_h2]:font-bold [&_h2]:text-ink [&_li]:ml-5 [&_li]:list-disc [&_p]:mt-2 [&_ul]:mt-2 [&_ul]:space-y-1.5">
        {children}
      </div>
    </div>
  );
}
