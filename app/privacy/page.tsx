import LegalPage from "@/components/LegalPage";

export const metadata = { title: "개인정보처리방침" };

export default function Page() {
  return (
    <LegalPage eyebrow="Privacy" title="개인정보처리방침" updated="2026년 10월 10일">
      <section className="rounded-2xl bg-accent-soft p-5">
        <p className="!mt-0 text-[17px] font-bold text-accent">사진과 생년월일은 서버에 저장되지 않습니다.</p>
        <p className="text-sub">
          얼굴 사진은 서버로 전송조차 되지 않습니다. 이용자의 기기(브라우저) 안에서만 분석되고, 분석이 끝나는 즉시 메모리에서
          삭제됩니다.
        </p>
      </section>
      <section>
        <h2>1. 처리하는 정보</h2>
        <ul>
          <li><b>얼굴 사진</b>: 브라우저 안에서 얼굴 랜드마크(점 좌표)를 추출하는 데만 사용하고, 즉시 삭제합니다. 서버 전송·저장 없음.</li>
          <li><b>생년월일·태어난 시간·성별</b>: 브라우저 안에서 사주를 계산하는 데만 사용합니다. 서버 저장 없음.</li>
          <li><b>분석 결과</b>: 결과 화면을 보여 주기 위해 이용자 브라우저의 임시 저장소(sessionStorage)에만 보관되며, 탭을 닫으면 사라집니다.</li>
          <li><b>회원가입 시 이메일</b>: 로그인을 위해 인증 서비스(Supabase)에 저장됩니다. 비밀번호는 암호화되어 저장됩니다.</li>
        </ul>
      </section>
      <section>
        <h2>2. AI 해석 시 전송되는 정보</h2>
        <p>
          AI 해석 기능이 켜져 있는 경우, 사진과 생년월일이 아닌 <b>계산된 결과 요약</b>(사주 기둥의 간지, 오행 개수, 십신, 관상 부위별
          특징 문장 등)만 AI 제공사(Anthropic)의 API로 전송되어 문장을 만든 뒤 응답됩니다. 서비스는 이 내용을 저장하지 않습니다.
        </p>
      </section>
      <section>
        <h2>3. 외부 서비스</h2>
        <ul>
          <li>Vercel: 웹사이트 호스팅 (접속 로그가 일시적으로 기록될 수 있음)</li>
          <li>Supabase: 회원 인증 (이메일)</li>
          <li>Anthropic: AI 해석 문장 생성 (결과 요약만 전송)</li>
          <li>운명첩 PDF: 받기 버튼을 누를 때 결과 문장과 표지 이름만 서버에서 PDF로 만들고 즉시 지웁니다 (사진·생년월일 미전송, 저장 없음)</li>
          <li>Microsoft(Azure·Edge 음성): 결과 문장 낭독 (재생 버튼을 누를 때 결과 문장만 전송, 사진·생년월일 미전송)</li>
          <li>jsDelivr·Google Storage: 글꼴과 얼굴 분석 모델 파일 다운로드</li>
        </ul>
      </section>
      <section>
        <h2>4. 이용자의 권리</h2>
        <p>
          회원은 언제든 탈퇴와 이메일 삭제를 요청할 수 있습니다. 문의는 사이트 운영자 이메일로 보내 주세요. 만 14세 미만은 보호자 동의
          없이 가입할 수 없습니다.
        </p>
      </section>
    </LegalPage>
  );
}
