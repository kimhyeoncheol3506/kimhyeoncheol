# 사실 확인 자료 — 「정말 쉽게 설명하는 SVB(실리콘밸리은행) 뱅크런」

- **확인 날짜:** 2026-11-21 (아래 URL은 모두 이날 직접 열어 본 페이지. 예외는 메모에 적음)
- **한 줄 요약:** 2020~2021년에 예금이 약 3배로 불어난 SVB는 그 돈을 장기 국채·MBS에 넣었다. 금리가 오르자 미실현 손실이 쌓였고, 2023-03-08 손실 매각·증자 발표 다음 날 하루에 420억 달러가 빠져나가는 뱅크런이 났다. SVB는 2023-03-10 폐쇄됐고, 03-12 당국이 예금 전액 보호를 발표했다. 그 비용은 은행들이 내는 특별 예금보험료로 메웠다.

> 표기 원칙: 금액은 미국 달러(USD), "B" = 10억 달러. 직접 연 공식 문서에서 확인한 숫자만 적었다. 출처마다 숫자가 다른 경우에는 각각의 기준을 메모에 밝혔다.

---

## 1. 핵심 사실 표

| # | 사실(한 문장) | 수치 | 날짜/기준 | 출처 URL(실제로 연 페이지) | 메모 |
|---|---|---|---|---|---|
| 1 | SVB(은행 법인)의 총자산은 약 2,090억 달러였다. | 약 $209.0B 총자산 / 약 $175.4B 총예금 | 2022-12-31 | https://www.fdic.gov/news/press-releases/2023/pr23016.html | 지주사 SVBFG 기준은 약 $212B(연준), 10-K 연결 기준은 $211.8B. 영상에서는 "약 2,090억 달러(은행 기준)"가 무난하다. |
| 2 | SVB는 미국 16위 은행이었다. | 16위(자산 기준) | 2023-03-10 보도 | https://www.pbs.org/newshour/economy/silicon-valley-bank-seized-by-fdic-after-largest-failure-since-the-great-recession (AP, Ken Sweet) | 공식 기관 문서에서는 "16위"라는 표현을 찾지 못했다. AP 보도와 위키피디아(NYT 인용)만 있으므로 "미국 16위 은행으로 꼽히던" 정도로 쓴다. |
| 3 | 예금의 약 94%가 보호 한도(25만 달러)를 넘는 비보호 예금이었다. | 약 94% (연준) / 88% (FDIC) | 2022-12-31 | https://www.federalreserve.gov/publications/files/svb-review-20230428.pdf (21쪽, 표1) / https://www.fdic.gov/news/speeches/2023/spmar2723.html | **기준이 다르다.** 연준(지주사 SVBFG, 총예금 대비)은 94%, FDIC 의장 증언(은행 보고 기준)은 88%다. 10-K에는 미국 내 추정 비보호 예금 $151.5B와 해외 예금 $13.9B(미국 예금보험 대상 아님)가 나온다. 영상에서는 "약 90% 안팎(연준 94%)"으로 쓰고, 출처는 연준으로 단다. 비교 대상인 대형은행 평균은 41%(연준 표1). |
| 4 | 예금이 2019년 말부터 2021년 말까지 약 3배로 늘었다. | $61.8B(2019) → $102.0B(2020) → $189.2B(2021) → $173.1B(2022) | 각 연말 | SEC XBRL(SVBFG 10-K 예금): https://data.sec.gov/api/xbrl/companyconcept/CIK0000719739/us-gaap/Deposits.json / 10-K 2022: https://www.sec.gov/Archives/edgar/data/719739/000071973923000021/sivb-20221231.htm | 연준 보고서에도 "2019~2021년 SVBFG 규모가 3배"라는 문장이 있다. 2022년에는 예금이 $16.1B 줄었다(10-K). |
| 5 | 자산은 2019~2022년 사이 710억 달러에서 2,110억 달러 넘게 커졌다. | $71B → $211B+ | 2019→2022 | 연준 보고서 PDF(위와 같음) | 2018년 말~2021년 말 자산 증가율은 271%(업계 평균 29%). |
| 6 | 늘어난 예금의 상당 부분을 만기보유(HTM) 증권, 주로 장기 MBS에 넣었다. | HTM 장부가 $91.3B / 시가 $76.2B | 2022-12-31 | 10-K 2022(위 URL) | HTM 가운데 정부기관 MBS가 $57.7B. 연준에 따르면 HTM 가중평균 듀레이션은 6.2년이고, 대부분 만기 10년 이상인 MBS다. HTM은 증권의 78%(대형은행 평균 42%). |
| 7 | 금리 인상으로 HTM 증권에 약 151억 달러의 미실현 손실이 생겼다. | HTM 미실현 손실 $15.16B (+ AFS 미실현 손실 $2.53B) | 2022-12-31 | 10-K 2022 HTM 표: https://www.sec.gov/Archives/edgar/data/719739/000071973923000021/sivb-20221231.htm | 같은 날 SVBFG 자기자본 총계는 $16.3B(지주사 주주지분 $16.0B)였다. "손실이 자본 거의 전부와 맞먹었다"는 비교는 가능하다. FDIC 증언에는 "증권 가치 하락분이 총자본의 104%"라는 표현이 있다. |
| 8 | 미국 기준금리는 2022-03 첫 인상 뒤 2023-02에 4.50~4.75%까지 올랐다. | 0.25~0.50%(2022-03-16) → 4.50~4.75%(2023-02-01) | 해당 FOMC 일자 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20220316a.htm / https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm | 배경 설명용 수치다. |
| 9 | 2023-03-08 SVB는 매도가능증권(AFS) 210억 달러를 팔아 세후 약 18억 달러 손실을 확정했다고 발표했다. | $21B 매각(수익률 1.79%, 듀레이션 3.6년) / 세후 손실 약 $1.8B | 2023-03-08 | 8-K 부속 99.2: https://www.sec.gov/Archives/edgar/data/719739/000119312523064680/d430920dex992.htm | 매각 대상은 미 국채·정부기관 증권이다. 연준 보고서도 같은 수치를 쓴다. |
| 10 | 같은 날 22.5억 달러 증자 계획과 차입 확대(150억→300억 달러)도 발표했다. | 공모 약 $1.75B + General Atlantic $0.5B = $2.25B | 2023-03-08 | 8-K 부속 99.3(주주 서한): https://www.sec.gov/Archives/edgar/data/719739/000119312523064680/d430920dex993.htm | 8-K 본문 기준 공모 구성은 보통주 $1.25B와 강제전환우선주 $0.5B다. 증자는 결국 완료되지 못했다. |
| 11 | 2023-03-09 하루 동안 약 420억 달러 인출이 몰렸다. | $42B | 2023-03-09 하루(종가 기준) | DFPI 명령문: https://dfpi.ca.gov/wp-content/uploads/sites/337/2023/03/DFPI-Orders-Silicon-Valley-Bank-03102023.pdf / FDIC 증언(spmar2723) | 연준 보고서는 "over $40 billion"이라고 쓴다. Becker 전 CEO 증언은 "10시간 동안 420억 달러, 초당 약 100만 달러"다. DFPI는 3/9 마감 때 은행 현금 잔고가 **약 -9억 5,800만 달러(마이너스)**였다고 적었다. |
| 12 | 3월 10일 하루에 1,000억 달러가 넘는 추가 인출이 예상됐다. | 1,000억 달러 이상 ("over $100 billion") | 2023-03-09 저녁~03-10 아침 SVB가 당국에 통보 | 연준 보고서 PDF(23쪽) / Becker 증언: https://www.banking.senate.gov/imo/media/doc/Becker%20Testimony%205-16-23.pdf | 연준은 실제 인출과 예상 인출을 합하면 예금 기반의 **약 85%**라고 했다. Becker 증언은 합계 약 1,420억 달러, 예금의 약 80%라고 했다. |
| 13 | 이 인출 속도는 2008년 대형 파산 사례와 비교가 안 될 만큼 빨랐다. | 와코비아 8일간 약 $10B, 워싱턴뮤추얼 16일간 $19B | 2008 비교 | 연준 보고서 PDF(3쪽) | "역대급 속도"라는 근거로 쓴다. |
| 14 | 3월 9일 SVB 지주사 주가가 약 60% 급락했다. | -60% | 2023-03-09 | PBS/AP(위 #2 URL), FDIC 증언(spmar2723) | |
| 15 | 2023-03-10 캘리포니아 DFPI가 SVB를 폐쇄하고 FDIC를 관재인으로 지정했다. | 오전 11:15(미 동부 기준 "EST") | 2023-03-10(금) | DFPI 명령문(위) / FDIC 증언: https://www.fdic.gov/news/speeches/2023/spmar2723.html | 폐쇄 사유: 유동성 부족, 지급불능(insolvent), 불안전 영업. FDIC 연혁 페이지는 "영업시간 중 폐쇄된 매우 이례적 사례"라고 적었다. 처음에는 부보 예금만 DINB(산타클라라 예금보험국립은행)로 옮겼다(pr23016). |
| 16 | 2023-03-12 재무부·연준·FDIC가 시스템 리스크 예외를 적용해 비보호 예금까지 전액 보호한다고 발표했다. | 예금 전액, 3/13(월)부터 인출 가능 | 2023-03-12 (연준 보도 오후 6:15 EDT) | 공동성명: https://home.treasury.gov/news/press-releases/jy1337 / https://www.fdic.gov/news/press-releases/2023/pr23017.html | "납세자가 손실을 부담하지 않는다", "손실은 법에 따라 은행 대상 특별 예금보험료로 회수한다", "주주와 일부 무담보 채권자는 보호하지 않는다", "경영진은 해임됐다"고 밝혔다. |
| 17 | 연준은 같은 날 은행기간대출프로그램(BTFP)을 만들었다. | 최장 1년 대출, 담보 국채·MBS를 **액면가(par)**로 평가, 재무부 외환안정기금 최대 $25B 보강 | 2023-03-12 | https://www.federalreserve.gov/newsevents/pressreleases/monetary20230312a.htm | 신규 대출은 2024-03-11에 예정대로 끝났다(https://www.federalreserve.gov/newsevents/pressreleases/monetary20240124a.htm, 2024-01-24 발표). |
| 18 | 2023-03-13 FDIC는 예금 전부와 거의 모든 자산을 가교은행(Silicon Valley Bridge Bank, N.A.)으로 옮겼다. | 전 예금 이전, CEO Tim Mayopoulos | 2023-03-13 | https://www.fdic.gov/news/press-releases/2023/pr23019.html | |
| 19 | 시그니처은행(뉴욕)이 2023-03-12 폐쇄됐고 같은 예외가 적용됐다. | 총자산 $110.4B, 총예금 $88.6B, 비보호 약 90% | 폐쇄 2023-03-12(일) / 수치 2022-12-31 | 공동성명(위), FDIC 증언(spmar2723) | 3/10 몇 시간 만에 예금 20%가 빠졌다. 2023-03-19 Flagstar(뉴욕커뮤니티 계열)와 인수 계약을 맺었다. FDIC 추정 비용은 약 $2.5B(당시). FDIC 자체 검토(2023-04-28)의 결론은 "근본 원인은 부실 경영"(pr23033). |
| 20 | 2023-03-19 스위스 당국 승인 아래 UBS가 크레디트스위스를 인수했다. | AT1 채권 약 CHF 160억 전액 상각 | 2023-03-19 | https://www.finma.ch/en/news/2023/03/20230319-mm-cs-ubs/ | 스위스중앙은행 유동성 지원과 연방정부 보증이 붙었다. SVB와 직접 연결된 사건은 아니고 "신뢰 위기의 연쇄"로 묶어 설명한다. |
| 21 | 2023-03-26 퍼스트시티즌스가 SVB 가교은행을 인수하는 계약이 발표됐다. | 자산 약 $72B를 $16.5B 할인 매입, 약 $90B는 관재인에 남김, FDIC가 최대 $500M 가치의 주식평가권 받음, 상업대출 손실 분담 | 2023-03-26 발표, 3/27 17개 지점 영업 재개 | https://www.fdic.gov/news/press-releases/2023/pr23023.html | 3/10 당시 총예금은 약 $119B(같은 보도자료). 인수자가 떠안은 예금액은 보도자료에 없다. |
| 22 | FDIC는 SVB 파산이 예금보험기금에 약 200억 달러 비용을 낸다고 처음 추정했다. | 약 $20B (그중 약 $18B·88%가 비보호 예금 보호 몫) | 2023-03-26 / 2023-03-27 | pr23023 / spmar2723 | **추정치라 계속 바뀌었다** → #23 참조. 2025-01 FDIC 소송 보도(Banking Dive)는 "예금보험기금 손실 약 $23B"라고 인용했다. 이 수치는 FDIC 원문을 직접 확인하지 못했다. |
| 23 | 비보호 예금 보호 비용(SVB+시그니처)의 추정치는 계속 수정됐다. | $15.8B(2023-05) → $16.3B(2023-11) → $20.4B(2023 연말 기준) → 약 $16.7B(2025-09-30 기준) | 각 날짜 | https://www.fdic.gov/news/speeches/2023/spnov1623b.html / https://fdic.gov/history/2020-present / https://www.fdic.gov/news/press-releases/2025/fdic-board-directors-issues-interim-final-rule-amend-collection-special | $15.8B는 검색 요약에서만 봤다(원문 미확인). "SVB 한 곳 비용"과 "두 은행의 시스템 리스크 예외 비용"은 다른 숫자이니 섞지 말 것. |
| 24 | 그 비용은 은행에 매긴 특별 예금보험료로 거뒀다. | 연 약 13.4bp(분기 3.36bp), 8분기, 2022년 말 비보호 예금에서 처음 $5B는 빼고 부과 | 2023-11-16 확정 / 2024 1분기~2025 4분기, 마지막 납부 2026-03-30(8분기째 2.97bp로 인하) | https://www.fdic.gov/deposit/insurance/assessments/specialassessment-psrd.html (페이지 최종 갱신 2026-11-02) / spnov1623b | 2023-11 기준 약 114개 은행그룹 대상이었다. 최신 페이지 기준 110개 은행그룹(141개 기관). 총자산 50억 달러 미만 은행은 사실상 제외됐다. 남은 정산(과다 징수분 상계 또는 일회성 부족분 부과)은 관재 종료와 SVB Financial Trust 소송 결과에 달렸다(2025-12-16 FDIC). |
| 25 | 퍼스트리퍼블릭은행이 2023-05-01 폐쇄됐고 JP모건체이스가 인수했다. | 총자산 약 $229.1B, 총예금 $103.9B(2023-04-13 기준), 예금보험기금 추정 비용 약 $13B | 2023-05-01 | https://www.fdic.gov/news/press-releases/2023/pr23034.html | 폐쇄 주체는 캘리포니아 DFPI다. 자산 규모로 SVB보다 컸다. FDIC 연혁에 따르면 SVB는 FDIC 역사상 3번째로 큰 파산(1위 워싱턴뮤추얼, 2위 퍼스트리퍼블릭)이고, 시그니처는 4번째. 2023-03-10 당시 보도의 "역대 2번째"는 퍼스트리퍼블릭 이전 기준이다. |
| 26 | 연준(Barr 보고서)은 원인을 4가지로 진단했다: ① 이사회·경영진의 위험관리 실패 ② 감독당국이 취약성을 충분히 파악 못 함 ③ 파악하고도 신속히 고치게 하지 못함 ④ 2018년 규제완화법(EGRRCPA) 이후 '맞춤형 규제'와 감독 기조 약화. | 폐쇄 시점 미해결 감독 지적 31건(동급 평균의 약 3배) | 2023-04-28 | https://www.federalreserve.gov/newsevents/pressreleases/bcreg20230428a.htm / 보고서 PDF | Barr 서문 표현: "a textbook case of mismanagement(교과서적인 경영 실패)". 금리가 오르는데도 헤지를 적극적으로 걷어 냈다고 지적했다. 2022년 말 기준 고유동성자산(HQLA) 약 9% 부족, 2023-02 추정 약 17% 부족. |
| 27 | 연준은 소셜미디어와 기술이 뱅크런 속도를 근본적으로 바꿨을 수 있다고 했다. | — | 2023-04-28 | 연준 보고서 PDF(서문 2쪽, 3쪽) | 원문 요지: "소셜미디어가 불안을 순식간에 퍼뜨렸고, 기술이 즉시 인출을 가능하게 했다." VC 중심으로 촘촘히 연결된 고객층이 "조직적으로" 인출했다고도 썼다. |
| 28 | SVB 지주사(SVB Financial Group)는 2023-03-17 뉴욕 남부 파산법원에 챕터11을 신청했다. | — | 신청 2023-03-17, 회생계획 인가 2024-08(8-K 사건일 2024-08-02), 효력 발생 2024-11-07 | SEC 8-K(2024-08-02): https://www.sec.gov/Archives/edgar/data/719739/000119312524206174/d227280d8k.htm / https://www.davispolk.com/experience/svb-financial-group-chapter-11-plan-becomes-effective | 은행(SVB)은 "파산 신청"이 아니라 "당국 폐쇄"다. 챕터11은 지주사 이야기이니 구분할 것. 자산은 청산신탁(SVB Financial Trust)과 MNSN Holdings로 넘어갔다. |
| 29 | FDIC는 2025-01-16 전 CEO Greg Becker 등 전직 임원 6명·이사 11명, 모두 17명을 중과실·신인의무 위반으로 고소했다. | 17명. 쟁점에는 2022-12 모회사에 준 $294M 배당 포함 | 제소 2025-01-16(캘리포니아 연방지법) | https://www.bankingdive.com/news/fdic-sues-17-ex-svb-executives-in-alleged-gross-negligence/737712/ | "수십억 달러" 배상을 청구했다. **2026-11-21 기준 이 소송의 판결은 확인 못 함**(진행 중으로 보임). |
| 30 | 2026-08 연방법원은 SVB 옛 모회사 측(SVB Financial Trust)이 FDIC에 낸 17.1억 달러 청구를 기각했다. | $1.71B 청구 불인정 | 판결 2026-08 말(금요일), Reuters 보도 2026-08-31 | https://www.spokesman.com/stories/2026/aug/31/fdic-defeats-171-billion-claim-over-silicon-valley/ (Reuters, Jonathan Stempel 기사 전재) | Beth Labson Freeman 판사(새너제이), 12일간 비배심 재판 뒤 판결했다. 판결은 전 경영진이 과도한 금리·유동성 위험을 진 것을 과실로 봤다. 항소 여부는 확인 못 함. |
| 31 | Becker 전 CEO는 2023-05-16 상원 은행위원회에서 증언하며 원인을 "전례 없는 사건들"과 SNS 소문으로 돌렸다. | "10시간에 420억 달러" | 2023-05-16 | Becker 서면 증언 PDF(위 #12) | "그런 속도와 규모의 뱅크런을 버틸 은행은 없었을 것"이라고 말했다. **경영진 형사 기소, SEC 제재, 성과급 환수의 최종 결과는 확인 못 함.** |
| 32 | 한국 예금보호 한도는 2025-09-01부터 1인당·금융회사별 1억 원이다(기존 5천만 원). | 5천만 원 → 1억 원, 2001년 이후 24년 만의 상향 | 2025-09-01 시행 | 금융위원회 보도(2025-05-15 입법예고): https://www.fsc.go.kr/po010101/84579 / 금융위 Q&A(2025-07-22): https://fsc.go.kr/po020201/84975 / 예금보험공사: https://www.kdic.or.kr/sp/dpstrprot/ProtSystProtLmts/selectScrn.do | 원금과 소정이자를 합쳐 계산한다. 외화예금도 포함된다. 시행 전에 가입한 예금도 1억 원까지 보호된다(예보 홈). 신협·농협·수협·산림조합·새마을금고도 똑같이 1억 원으로 올랐다. 퇴직연금(DC·IRP), 연금저축, 사고보험금은 일반 예금과 따로 각각 1억 원까지 보호된다. |
| 33 | 보호되는 것은 원금 지급이 보장되는 상품(예금·적금 등)이고, 실적배당형(펀드 등)은 보호되지 않는다. | — | 2025 기준 공식 안내 | 예보 보호대상 상품: https://www.kdic.or.kr/sp/dpstrprot/selectProtSystProtTrgtPrdctSumr.do / 금융위 Q&A(위) | 은행 보호: 보통·정기예금, 적금, 외화예금, 예금으로 운용하는 DC·IRP 적립금, 원본보전 금전신탁 등. 은행 비보호: CD, RP, 펀드(수익증권·뮤추얼펀드·MMF), 은행 발행채권, 주택청약저축·주택청약종합저축(정부가 주택도시기금으로 별도 관리), DB형 퇴직연금, 실적배당형 신탁. 금융위 Q&A는 증권사 CMA, 후순위채권도 비보호로 적었다. |

---

## 2. 사건 연표

| 날짜(현지) | 시각 | 사건 | 근거 |
|---|---|---|---|
| 2019~2021 | — | 예금 $61.8B → $189.2B, 총자산 3배. VC 투자 붐과 초저금리 시기 | 10-K/XBRL, 연준 보고서 |
| 2021-06 | — | SVBFG 평균 총자산 1,000억 달러 돌파(대형은행 감독 대상 진입) | 연준 보고서 |
| 2022-03-16 | — | 연준 첫 금리 인상(0.25~0.50%) | 연준 FOMC |
| 2022-12-31 | — | 총자산 $209B(은행) / 비보호 예금 94%(연준) / HTM 미실현 손실 $15.2B | FDIC, 연준, 10-K |
| 2023-02-01 | — | 기준금리 4.50~4.75% | 연준 FOMC |
| 2023-03-08(수) | 장 마감 후 | AFS $21B 매각, 세후 손실 $1.8B, $2.25B 증자 계획 발표. 같은 날 실버게이트 자진 청산 발표 | SEC 8-K, 연준 보고서 |
| 2023-03-09(목) | 종일 | 주가 약 -60%, 예금 $42B 인출, 마감 때 현금 약 -$958M | DFPI, FDIC 증언, AP |
| 2023-03-09 저녁~03-10 아침 | — | SVB가 감독당국에 "3/10에 $100B 넘게 더 빠질 것"이라고 통보 | 연준 보고서 |
| 2023-03-10(금) | 11:15 a.m. (미 동부) | 캘리포니아 DFPI가 폐쇄, FDIC 관재인 지정. 부보 예금은 DINB로 | DFPI 명령문, FDIC 증언, FDIC pr23016 |
| 2023-03-12(일) | 6:15 p.m. EDT(연준 보도 시각) | 재무부·연준·FDIC 공동성명: SVB·시그니처 예금 전액 보호(시스템 리스크 예외), BTFP 신설. 같은 날 시그니처은행 폐쇄 | 재무부 jy1337, 연준, FDIC pr23017 |
| 2023-03-13(월) | 아침 | 가교은행 영업 시작, 예금 전액 인출 가능 | FDIC pr23019 |
| 2023-03-17 | — | SVB Financial Group 챕터11 신청 | SEC 8-K |
| 2023-03-19 | — | UBS가 크레디트스위스 인수(FINMA 승인). 시그니처은행 인수 계약(Flagstar) | FINMA, FDIC 증언 |
| 2023-03-26 | — | 퍼스트시티즌스가 SVB 가교은행 인수 발표($72B를 $16.5B 할인 매입). FDIC 비용 추정 약 $20B | FDIC pr23023 |
| 2023-03-27 | — | 17개 지점 퍼스트시티즌스로 영업 재개 / Gruenberg FDIC 의장 상원 증언 | FDIC |
| 2023-04-28 | 11:00 a.m. EDT | 연준 Barr 보고서와 FDIC 시그니처 보고서 공개 | 연준, FDIC pr23033 |
| 2023-05-01 | — | 퍼스트리퍼블릭 폐쇄, JP모건체이스 인수(비용 약 $13B 추정) | FDIC pr23034 |
| 2023-05-16 | — | Becker 전 CEO 상원 은행위원회 증언 | 상원 서면 증언 |
| 2023-11-16 | — | FDIC 이사회, 특별 예금보험료 확정(연 약 13.4bp, 8분기, $16.3B 회수 목표) | FDIC spnov1623b |
| 2023 연말 기준 | — | 시스템 리스크 예외 손실 추정 $16.3B → $20.4B로 상향 | FDIC 연혁 |
| 2024-03-11 | — | BTFP 신규 대출 종료 | 연준 2024-01-24 |
| 2024-06-28 | — | 특별 예금보험료 첫 납부 | FDIC 특별보험료 페이지 |
| 2024-08 / 2024-11-07 | — | SVBFG 회생계획 인가(8월), 효력 발생(11-07) | SEC 8-K, Davis Polk |
| 2025-01-16 | — | FDIC, 전직 임원·이사 17명 제소 | Banking Dive |
| 2025-09-01 | — | (한국) 예금보호 한도 1억 원 시행 | 금융위, 예보 |
| 2025-12-16 | — | FDIC, 특별보험료 징수 조정 임시 최종규칙(손실 추정 약 $16.7B, 2025-09-30 기준) | FDIC 2025 보도자료 |
| 2026-03-30 | — | 특별 예금보험료 8분기째(마지막) 납부일 | FDIC 특별보험료 페이지 |
| 2026-08 말 | — | 법원, SVB Financial Trust의 FDIC 상대 $1.71B 청구 기각 | Reuters(Spokesman 전재) |
| 2026-11-21 | — | FDIC 대 전직 경영진 소송 결과: **확인 못 함** | — |

---

## 3. 쓰면 안 되는 주장 (퍼졌지만 틀리거나 확인 안 되는 것)

1. **"SVB가 파산 신청을 했다"** → 틀림. 은행(SVB)은 캘리포니아 DFPI가 폐쇄하고 FDIC가 관재인이 됐다. 챕터11 파산 신청은 지주사(SVB Financial Group)가 2023-03-17에 했다.
2. **"정부가 세금으로 SVB를 구제(bailout)했다"** → 틀림. 주주와 일부 채권자는 보호받지 못했고 경영진은 해임됐다. 비보호 예금을 지킨 비용은 예금보험기금이 냈고, 은행들이 내는 특별 예금보험료로 메웠다. 공동성명에도 "납세자가 손실을 부담하지 않는다"고 적혀 있다. "예금자는 전액 보호, 회사는 구제 안 됨"이 정확하다.
3. **"SVB는 위험한 코인·주식에 투자해서 망했다"** → 틀림. 주된 투자처는 신용위험이 낮은 미 국채와 정부기관 MBS였다. 문제는 **금리 위험**(장기채 가격 하락)과 **비보호 예금 쏠림**이었다. 코인 은행은 실버게이트와 시그니처(디지털자산 예금 약 20%) 쪽 이야기다.
4. **"예금의 94%가 보호 안 됐다"를 모든 출처의 공통 수치처럼 쓰기** → 주의. 연준(지주사 기준)은 94%, FDIC 의장 증언(은행 보고 기준)은 88%다. 출처를 밝히거나 "약 90% 안팎"으로 쓴다.
5. **"하루에 420억 달러가 실제로 빠졌고, 다음 날 1,000억 달러도 빠졌다"** → 틀림. 1,000억 달러는 3/10 인출 **요청·예상**분이다. 은행이 3/10 오전에 폐쇄돼 실제로 나가지 않았다.
6. **"SVB는 미국 역사상 두 번째로 큰 은행 파산"** → 당시(2023-03-10)에는 맞았다. 2023-05-01 퍼스트리퍼블릭이 폐쇄된 뒤로는 **세 번째**다(FDIC 연혁 기준). 시점을 밝혀서 쓴다.
7. **"트윗 한 줄 때문에 망했다"** → 과장. 연준은 SNS를 **속도**를 키운 요인으로 봤다. 근본 원인은 경영 실패(금리·유동성 위험관리)와 감독 지연이라고 했다.
8. **"FDIC 손실은 정확히 OO억 달러로 확정됐다"** → 확정되지 않았다. 계속 수정되는 추정치다($20B → 시스템 리스크 몫 $16.3B → $20.4B → $16.7B). 최종 금액은 관재 종료와 소송 결과에 달렸다(FDIC 2025-12-16).
9. **"Becker 전 CEO가 유죄 판결·형사 처벌을 받았다"** → 확인 못 함. 확인된 것은 FDIC 민사소송 제기(2025-01)뿐이고 결과는 확인 못 함. 위키피디아에는 SEC·DOJ가 "조사를 시작했다고 보도됐다"는 정도만 있다.
10. **"SVB 붕괴로 미국 예금보호 한도가 올랐다"** → 확인 못 함. 이 조사에서는 미국 예금보호 한도(25만 달러)가 바뀌었다는 공식 근거를 찾지 못했다.
11. **"한국 예금자보호 1억 원 상향이 SVB 때문"** → 인과관계는 확인 못 함. 공식 자료는 "2001년 이후 24년 만의 상향"이라고만 한다. "SVB 같은 일을 보면서 한국에서도 한도 논의가 이어졌다"처럼 느슨하게 쓰거나 연결 고리를 빼는 편이 안전하다.
12. **"펀드·CMA·주택청약종합저축도 1억 원까지 보호된다"** → 틀림. 펀드, 증권사 CMA, 후순위채, CD, RP는 예금자보호 대상이 아니다. 주택청약종합저축은 예금보험이 아니라 정부(주택도시기금)가 따로 관리한다.
13. **"1억 원은 은행 지점마다 / 상품마다 따로"** → 틀림. 금융회사별로 1인당 원금과 이자를 합쳐 1억 원이다. 같은 은행의 예금을 모두 합산한다(예외: 퇴직연금·연금저축·사고보험금은 따로).

---

## 4. 확인 못 한 항목

- 공식 기관(연준·FDIC) 문서에 "미국 16위 은행"이라는 순위 문구: 확인 못 함 (AP 보도만 직접 확인).
- 퍼스트시티즌스가 떠안은 예금 총액(흔히 "약 560억 달러"로 인용됨): FDIC 보도자료에 없음. 확인 못 함.
- 2023-05의 $15.8B 추정치: 검색 요약에만 있고 원문 미확인.
- FDIC의 "SVB 한 곳 기준" 최신 손실 추정(2024~2026): 확인 못 함. 두 은행 시스템 리스크 몫($16.7B, 2025-09-30 기준)만 확인.
- FDIC 대 Becker 등 17명 소송의 판결·합의(2026-11-21 기준): 확인 못 함.
- SEC·법무부 조사 결과, 경영진 성과급 환수: 확인 못 함.
- SVB Financial Trust 판결(2026-08)에 대한 항소 여부: 확인 못 함.

---

## 5. 출처 목록 (직접 연 페이지)

**연준(Federal Reserve)**
- Review of the Federal Reserve's Supervision and Regulation of Silicon Valley Bank (2023-04-28, Barr 보고서 PDF) — https://www.federalreserve.gov/publications/files/svb-review-20230428.pdf
- 보고서 공개 보도자료 (2023-04-28) — https://www.federalreserve.gov/newsevents/pressreleases/bcreg20230428a.htm
- BTFP 신설 보도자료 (2023-03-12) — https://www.federalreserve.gov/newsevents/pressreleases/monetary20230312a.htm
- BTFP 신규 대출 종료 예고 (2024-01-24) — https://www.federalreserve.gov/newsevents/pressreleases/monetary20240124a.htm
- FOMC 성명 (2022-03-16) — https://www.federalreserve.gov/newsevents/pressreleases/monetary20220316a.htm
- FOMC 성명 (2023-02-01) — https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm

**FDIC**
- FDIC Creates a Deposit Insurance National Bank of Santa Clara (2023-03-10, pr23016) — https://www.fdic.gov/news/press-releases/2023/pr23016.html
- Joint Statement by Treasury, Federal Reserve, and FDIC (2023-03-12, pr23017) — https://www.fdic.gov/news/press-releases/2023/pr23017.html
- FDIC Acts to Protect All Depositors of the former Silicon Valley Bank (2023-03-13, pr23019) — https://www.fdic.gov/news/press-releases/2023/pr23019.html
- First–Citizens 인수 발표 (2023-03-26, pr23023) — https://www.fdic.gov/news/press-releases/2023/pr23023.html
- Gruenberg 의장 상원 증언 "Recent Bank Failures and the Federal Regulatory Response" (2023-03-27) — https://www.fdic.gov/news/speeches/2023/spmar2723.html
- FDIC Releases Report Detailing Supervision of the Former Signature Bank (2023-04-28, pr23033) — https://www.fdic.gov/news/press-releases/2023/pr23033.html
- First Republic / JPMorgan Chase (2023-05-01, pr23034) — https://www.fdic.gov/news/press-releases/2023/pr23034.html
- Gruenberg 의장 특별보험료 최종규칙 성명 (2023-11-16) — https://www.fdic.gov/news/speeches/2023/spnov1623b.html
- Special Assessment 안내 페이지 (최종 갱신 2026-11-02) — https://www.fdic.gov/deposit/insurance/assessments/specialassessment-psrd.html
- 특별보험료 징수 조정 임시 최종규칙 (2025-12-16) — https://www.fdic.gov/news/press-releases/2025/fdic-board-directors-issues-interim-final-rule-amend-collection-special
- FDIC 연혁 2020-present — https://fdic.gov/history/2020-present
- Failed Bank List: Silicon Valley Bank — https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/silicon-valley.html

**캘리포니아 DFPI**
- Order Taking Possession of Property and Business — Silicon Valley Bank (2023-03-10) — https://dfpi.ca.gov/wp-content/uploads/sites/337/2023/03/DFPI-Orders-Silicon-Valley-Bank-03102023.pdf

**미 재무부**
- Joint Statement by Treasury, Federal Reserve, and FDIC (2023-03-12, jy1337) — https://home.treasury.gov/news/press-releases/jy1337

**SEC 공시 (SVB Financial Group)**
- Form 10-K FY2022 — https://www.sec.gov/Archives/edgar/data/719739/000071973923000021/sivb-20221231.htm
- XBRL 연말 예금 시계열 — https://data.sec.gov/api/xbrl/companyconcept/CIK0000719739/us-gaap/Deposits.json
- 8-K 부속 99.2 Mid-Quarter Update (2023-03-08) — https://www.sec.gov/Archives/edgar/data/719739/000119312523064680/d430920dex992.htm
- 8-K 부속 99.3 Message to Stakeholders (2023-03-08) — https://www.sec.gov/Archives/edgar/data/719739/000119312523064680/d430920dex993.htm
- 8-K 회생계획 인가 (2024-08-02) — https://www.sec.gov/Archives/edgar/data/719739/000119312524206174/d227280d8k.htm

**미 상원**
- Gregory Becker 서면 증언 (2023-05-16) — https://www.banking.senate.gov/imo/media/doc/Becker%20Testimony%205-16-23.pdf

**스위스 FINMA**
- FINMA approves takeover of Credit Suisse by UBS (2023-03-19) — https://www.finma.ch/en/news/2023/03/20230319-mm-cs-ubs/

**한국 (금융위원회·예금보험공사)**
- 금융위원회 「예금보호한도 상향을 위한 6개 법령의 일부개정에 관한 대통령령안」 입법예고 (2025-05-15) — https://www.fsc.go.kr/po010101/84579
- 금융위원회 「예금보호한도 상향 관련 주요 Q&A」 (2025-07-22) — https://fsc.go.kr/po020201/84975
- 예금보험공사 보호한도 안내 — https://www.kdic.or.kr/sp/dpstrprot/ProtSystProtLmts/selectScrn.do
- 예금보험공사 보호대상 금융상품 — https://www.kdic.or.kr/sp/dpstrprot/selectProtSystProtTrgtPrdctSumr.do
- 예금보험공사 홈 — https://www.kdic.or.kr/

**언론·기타 (보조)**
- AP(PBS 전재), Ken Sweet, "Silicon Valley Bank seized by FDIC…" (2023-03-10) — https://www.pbs.org/newshour/economy/silicon-valley-bank-seized-by-fdic-after-largest-failure-since-the-great-recession
- Banking Dive, "FDIC sues 17 ex-SVB executives in alleged 'gross negligence'" (2025-01-17) — https://www.bankingdive.com/news/fdic-sues-17-ex-svb-executives-in-alleged-gross-negligence/737712/
- Reuters(Spokesman-Review 전재), "FDIC defeats $1.71 billion claim over Silicon Valley Bank collapse" (2026-08-31) — https://www.spokesman.com/stories/2026/aug/31/fdic-defeats-171-billion-claim-over-silicon-valley/
- Davis Polk, "SVB Financial Group chapter 11 plan becomes effective" — https://www.davispolk.com/experience/svb-financial-group-chapter-11-plan-becomes-effective
- Wikipedia, "Collapse of Silicon Valley Bank" (보조) — https://en.wikipedia.org/wiki/Collapse_of_Silicon_Valley_Bank
