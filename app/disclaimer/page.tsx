import LegalPage from "@/components/LegalPage";

export const metadata = { title: "면책조항" };

export default function Page() {
  return (
    <LegalPage eyebrow="Disclaimer" title="면책조항" updated="2026년 10월 10일">
      <section className="border-l-4 border-accent pl-5">
        <p className="!mt-0 text-xl font-bold">
          본 서비스는 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다. 중요한 결정은 전문가와 상담하세요.
        </p>
      </section>
      <section>
        <h2>1. 서비스의 성격</h2>
        <p>
          ‘얼굴과 운명’(이하 서비스)은 전통 명리학(사주)과 관상학의 일반적인 해석 규칙을 컴퓨터로 자동 적용해 재미로 보는
          콘텐츠입니다. 결과는 과학적으로 검증된 사실이 아니며, 개인의 미래를 예언하거나 보장하지 않습니다.
        </p>
      </section>
      <section>
        <h2>2. 결과의 한계</h2>
        <ul>
          <li>사주는 오픈소스 엔진 기반으로 두 엔진의 공통 결과를 도출하지만, 계산 방식에 따라 전문가의 해석과 다를 수 있습니다.</li>
          <li>관상 분석은 사진의 각도·조명·표정·화장·안경 등에 따라 크게 달라질 수 있습니다.</li>
          <li>AI가 작성한 문장은 사실과 다르거나 부정확할 수 있습니다.</li>
          <li>건강 관련 내용은 질병의 진단·예방·치료와 무관합니다. 몸에 이상이 있으면 의료기관을 찾으세요.</li>
        </ul>
      </section>
      <section>
        <h2>3. 책임의 제한</h2>
        <p>
          이용자가 결과를 근거로 내린 결정(투자, 진로, 결혼, 계약, 치료 등)과 그로 인한 손해에 대해 서비스는 책임을 지지 않습니다.
          결과를 타인을 평가·차별하거나 비방하는 용도로 사용해서는 안 됩니다.
        </p>
      </section>
      <section>
        <h2>4. 타인의 사진</h2>
        <p>다른 사람의 사진은 반드시 본인의 동의를 받은 경우에만 분석하세요. 무단 사용에 따른 책임은 이용자에게 있습니다.</p>
      </section>
    </LegalPage>
  );
}
