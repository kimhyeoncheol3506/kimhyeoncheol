import LegalPage from "@/components/LegalPage";
import { pageMeta } from "@/lib/site";

export const metadata = pageMeta({ title: "개인정보처리방침", description: "얼굴과 운명이 처리하는 정보와 보관 방법을 안내합니다. 얼굴 사진과 생년월일은 서버에 저장하지 않고 이용자 기기 안에서만 분석합니다.", path: "/privacy" });

export default function Page() {
  return (
    <LegalPage eyebrow="Privacy" title="개인정보처리방침" updated="2026년 11월 17일">
      <section className="rounded-2xl bg-accent-soft p-5">
        <p className="!mt-0 text-[17px] font-bold text-accent">사진과 생년월일은 서버에 저장되지 않습니다.</p>
        <p className="text-sub">
          얼굴 사진은 서버로 전송조차 되지 않습니다. 이용자의 기기(브라우저) 안에서만 분석되고, <b>분석이 끝나는 즉시 메모리에서 삭제</b>
          됩니다. 사진을 올리기 전에는 별도의 동의를 받습니다.
        </p>
      </section>

      <section>
        <h2>1. 처리하는 정보와 목적</h2>
        <ul>
          <li><b>얼굴 사진(선택)</b>: 관상 분석을 위해 브라우저 안에서 얼굴 랜드마크(점 좌표)를 추출하는 데만 사용합니다. 서버 전송·저장 없음.</li>
          <li><b>생년월일·태어난 시간·성별</b>: 사주 계산을 위해 브라우저 안에서만 사용합니다. 서버 전송·저장 없음.</li>
          <li><b>궁합 상대방의 이름(선택)·생년월일·사진(선택)</b>: 궁합 계산을 위해 브라우저 안에서만 사용합니다. 상대방 사진은 상대방의 동의를 받은 경우에만 올려 주세요.</li>
          <li><b>궁합 고민 글(선택)</b>: 브라우저 안에서 조언 문장을 고르는 데만 쓰고 서버로 보내지 않습니다.</li>
          <li><b>분석 결과</b>: 결과 화면을 보여 주기 위해 브라우저의 임시 저장소(sessionStorage)에만 보관합니다.</li>
          <li><b>운명첩 PDF의 표지 이름</b>: PDF를 만들 때만 결과 문장과 함께 서버로 보내고, 만든 직후 지웁니다.</li>
          <li><b>회원가입 시 이메일</b>: 로그인을 위해 인증 서비스(Supabase)에 저장합니다. 비밀번호는 암호화되어 저장됩니다.</li>
          <li><b>접속 기록·쿠키</b>: 호스팅 서버의 접속 로그와 광고·방문 분석 쿠키 (6항 참고)</li>
        </ul>
      </section>

      <section>
        <h2>2. 사진 처리 방식</h2>
        <ul>
          <li>사진을 고르기 전에 ‘얼굴 사진 분석 동의’를 따로 받습니다. 궁합에서 상대방 사진을 쓸 때는 ‘상대방에게 동의를 받았다’는 확인도 따로 받습니다.</li>
          <li>사진은 이용자의 기기 안에서 얼굴 비율을 재는 데만 쓰이고, 분석이 끝나면 즉시 메모리에서 지웁니다.</li>
          <li>사진은 서버·AI 제공사·광고 사업자 어디로도 보내지 않으며, 어떤 형태로도 저장하지 않습니다.</li>
        </ul>
      </section>

      <section>
        <h2>3. 보유 기간</h2>
        <ul>
          <li>얼굴 사진: <b>보관하지 않음</b> (분석 직후 기기 메모리에서 삭제)</li>
          <li>생년월일·궁합 입력값·분석 결과: 서버 보관 없음. 브라우저 임시 저장소에 있다가 <b>탭이나 창을 닫으면 삭제</b></li>
          <li>운명첩 PDF 생성 데이터(결과 문장·표지 이름): PDF를 만든 직후 서버 메모리에서 삭제</li>
          <li>목소리 낭독 요청 문장: 서비스는 저장하지 않음 (음성 제공사의 정책에 따른 처리만 있음)</li>
          <li>AI 해석 요청(결과 요약): 서비스는 저장하지 않음. AI 제공사는 자체 정책에 따라 남용 방지를 위해 단기간 보관할 수 있음</li>
          <li>회원 이메일: 탈퇴할 때까지 (탈퇴 요청 시 지체 없이 삭제)</li>
          <li>방문 분석(GA4) 데이터: 최대 14개월</li>
          <li>문의 메일: 문의 처리 후 1년</li>
          <li>앞으로 유료 결제가 생기면 결제·환불 기록: 「전자상거래법」에 따라 5년</li>
        </ul>
      </section>

      <section>
        <h2>4. 외부 서비스(처리 위탁)</h2>
        <ul>
          <li>Vercel: 웹사이트 호스팅, 운명첩 PDF 생성 (접속 로그가 일시적으로 기록될 수 있음)</li>
          <li>Supabase: 회원 인증 (이메일, 회원가입 기능을 켠 경우)</li>
          <li>Anthropic: AI 해석 문장 생성 (기능을 켠 경우, 결과 요약만 전송)</li>
          <li>Alibaba Cloud(Model Studio)·Microsoft: 결과 문장 목소리 낭독 (재생 버튼을 누를 때 결과 문장만 전송, 사진·생년월일 미전송)</li>
          <li>Google: AdSense 광고 게재, 애널리틱스 방문 분석(켠 경우), 글꼴 제공</li>
          <li>jsDelivr·Google Storage: 글꼴과 얼굴 분석 모델 파일 다운로드</li>
        </ul>
      </section>

      <section>
        <h2>5. 국외 처리(국외 이전) 고지</h2>
        <p>서비스를 제공하기 위해 아래와 같이 일부 정보가 국외에서 처리됩니다. 모두 이용자가 해당 기능을 쓸 때 인터넷(암호화된 HTTPS)으로 전송됩니다.</p>
        <ul>
          <li><b>Anthropic, PBC (미국)</b> — AI 해석이 켜진 경우 결과를 볼 때: 사주 간지·오행 개수·관상 특징 문장 등 결과 요약(사진·생년월일 제외). 목적: 풀이 문장 생성. 보유: 서비스는 저장하지 않으며 제공사 정책에 따른 단기 보관.</li>
          <li><b>Alibaba Cloud (싱가포르)</b> — ‘목소리로 듣기’를 누를 때: 읽어 줄 결과 문장. 목적: 음성 합성. 보유: 서비스는 저장하지 않음.</li>
          <li><b>Microsoft Corporation (미국)</b> — 보조 목소리를 쓸 때: 읽어 줄 결과 문장. 목적: 음성 합성. 보유: 서비스는 저장하지 않음.</li>
          <li><b>Vercel Inc. (미국)</b> — 사이트 접속과 PDF 받기를 할 때: 접속 기록, PDF용 결과 문장·표지 이름. 목적: 호스팅·PDF 생성. 보유: PDF 데이터는 생성 직후 삭제, 접속 기록은 호스팅사 정책 기간.</li>
          <li><b>Google LLC (미국)</b> — 사이트 접속 시: 광고·분석 쿠키, 익명 이용 통계. 목적: 광고 게재·방문 분석. 보유: 최대 14개월(분석).</li>
          <li><b>Supabase Inc. (미국)</b> — 회원가입 시: 이메일. 목적: 로그인. 보유: 탈퇴 시까지.</li>
        </ul>
        <p>
          국외 처리를 원하지 않으면 해당 기능(목소리 듣기, PDF 받기, 회원가입)을 쓰지 않거나 브라우저에서 쿠키를 차단할 수 있습니다. 이
          경우 일부 기능을 이용할 수 없습니다.
        </p>
      </section>

      <section>
        <h2>6. 쿠키: 구글 애드센스 광고와 방문 분석</h2>
        <p>
          이 사이트는 무료 서비스 운영을 위해 Google AdSense 광고를 게재합니다. Google을 포함한 제3자 광고 사업자는 쿠키를 사용하여 이용자가 이
          사이트나 다른 웹사이트를 방문한 기록을 바탕으로 광고를 게재할 수 있습니다. Google은 광고 쿠키를 사용하여 이용자의 방문 기록에 맞는
          광고를 보여 줍니다.
        </p>
        <p>
          이용자는{" "}
          <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer" className="underline">
            Google 광고 설정
          </a>
          에서 맞춤 광고를 끌 수 있고,{" "}
          <a href="https://www.aboutads.info/choices" target="_blank" rel="noopener noreferrer" className="underline">
            www.aboutads.info
          </a>
          에서 제3자 광고 사업자의 맞춤 광고 쿠키 사용을 거부할 수 있습니다. 브라우저 설정에서 쿠키를 차단할 수도 있습니다. 자세한 내용은{" "}
          <a href="https://policies.google.com/technologies/ads?hl=ko" target="_blank" rel="noopener noreferrer" className="underline">
            Google 광고 정책
          </a>
          을 확인해 주세요.
        </p>
        <p>
          운영자가 구글 애널리틱스(GA4)를 켠 경우, 방문 페이지·기기 종류·대략적인 지역과 ‘시작·결과 보기·공유·PDF 받기’ 같은 이용 단계만 익명
          통계로 수집합니다. 이름·생년월일·사진·결과 내용은 보내지 않으며, 브라우저의 쿠키 차단이나{" "}
          <a href="https://tools.google.com/dlpage/gaoptout?hl=ko" target="_blank" rel="noopener noreferrer" className="underline">
            구글 애널리틱스 차단 부가기능
          </a>
          으로 거부할 수 있습니다.
        </p>
        <p>얼굴 사진, 생년월일, 분석 결과는 광고 사업자나 분석 도구에 전달되지 않습니다.</p>
      </section>
      <section>
        <h2>7. 이용자의 권리</h2>
        <p>
          이용자는 언제든지 자신의 개인정보 열람·정정·삭제·처리 정지를 요청할 수 있고, 회원은 탈퇴와 이메일 삭제를 요청할 수 있습니다. 서비스는
          사진·생년월일·결과를 서버에 저장하지 않으므로, 이 정보는 브라우저 창을 닫는 것만으로 지워집니다. 만 14세 미만은 보호자 동의 없이 가입할
          수 없습니다.
        </p>
      </section>

      <section>
        <h2>8. 개인정보 보호책임자와 연락처</h2>
        <ul>
          <li>운영자: 얼굴과 운명 운영자 (개인정보 보호책임자 겸임)</li>
          <li>이메일: <b>no4angel1981@gmail.com</b></li>
        </ul>
        <p>
          개인정보 관련 문의·불만·피해 구제는 위 이메일로 보내 주시면 영업일 기준 3일 이내에 답변합니다. 개인정보침해 신고센터(국번 없이
          118), 개인정보 분쟁조정위원회(1833-6972)에도 도움을 요청할 수 있습니다.
        </p>
      </section>

      <section>
        <h2>9. 변경 안내</h2>
        <p>이 방침을 바꾸면 시행 7일 전부터 이 페이지에 알립니다. 이 방침은 2026년 11월 17일부터 적용합니다.</p>
      </section>
    </LegalPage>
  );
}
