# 「구글의 새 기술 발표에 왜 반도체 주가가 흔들렸나」 사실 확인 자료

- **확인 날짜:** 2026-11-26 (아래 URL은 이날 직접 열어 확인함. 검색 요약으로만 본 것은 메모에 적거나 '확인 못 한 항목'으로 뺌)
- **한 줄 요약:** 구글 리서치는 2026-03-24 AI 모델의 KV 캐시 메모리를 최소 6배 줄이는 압축 기술 '터보퀀트(TurboQuant)'를 블로그로 공개했다. 이틀 뒤(03-26) SK하이닉스 -6.23%, 삼성전자 -4.71%, 코스피 -3.22%. "메모리를 덜 쓰면 메모리 수요가 준다"는 걱정이 이유였지만, 연구 단계 기술이었고 증권가는 제번스의 역설(효율↑→총수요↑)을 들어 반박했다. 실제로 SK하이닉스는 6월 22일 291만9천 원으로 3월 말(87만3천 원)의 3배를 넘었다가, 11월 초 미국 중간선거 뒤 데이터센터 규제 우려·차익실현 매도로 다시 급락했다. 한국 반도체 수출은 2025년 총수출의 약 24%였으나 2026년 9~10월엔 약 절반을 차지했고, 6월 말 삼성전자·SK하이닉스 두 종목이 코스피 시총의 57%를 넘었다.

> 표기 원칙: 등락률은 종가 기준(한국거래소 기사). 비중(%) 가운데 '계산'이라 적은 것은 기사 수치로 직접 나눈 값이다.

---

## 1. 사실 표

### G. 구글 '터보퀀트' 발표와 시장 반응 (2026년 3월)

| # | 사실 | 수치 | 날짜·기준 | 실제로 연 URL | 메모 |
|---|---|---|---|---|---|
| G1 | 구글 리서치가 블로그로 압축 기술 터보퀀트를 공개했다. KV 캐시(대화 중 계산 결과를 저장하는 메모리)를 줄인다. | KV 메모리 **최소 6배** 감소, 3비트까지 양자화(추가 학습 불필요) | 2026-03-24 | https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/ | 저자 Amir Zandieh·Vahab Mirrokni. ICLR 2026 발표 예정 논문. Gemma·Mistral 공개 모델로 실험. "정확도 손실 0"은 저자 주장. |
| G2 | H100 GPU에서 어텐션 계산(attention logit) 속도가 빨라졌다. | 4비트 기준 **최대 8배** | 2026-03-24 | 위와 같음 | 전체 추론 속도가 8배라는 뜻이 아니다(커널 단위 수치). 영상에서는 "일부 계산이 최대 8배"로만. |
| G3 | 발표 이틀 뒤 한국에서 SK하이닉스와 삼성전자가 급락했다. | SK하이닉스 **-6.23%(93만3천 원)**, 삼성전자 **-4.71%(18만100원)** | 2026-03-26 종가 | https://www.tradingkey.com/analysis/stocks/us-stocks/261722379-samsung-hk-hynix-memory-hbm-dram-google-turboquant-semi-conductor-tradingkey · https://www.newsis.com/view/NISX20260327_0003567479 | 종가 금액은 검색 결과의 한경 기사 요약에서 확인(SBS 애프터마켓 가격은 18만1,100원·94만1천 원으로 종가 아님). |
| G4 | 같은 날 코스피도 크게 내렸다. | **-3.22%, 5,460선** | 2026-03-26 | tradingkey(위) · https://biz.sbs.co.kr/amp/article/20000300112 | SBS: "3%대 하락, 5460선 마감", 코스닥 1136선. 종가 5,460.46은 한경 기사 검색 요약. |
| G5 | 해외 메모리주도 함께 내렸다. | 키옥시아 **약 -6%**(03-26), 마이크론·샌디스크 03-25 미국장 하락 | 2026-03-25~26 | https://www.cnbc.com/2026/03/26/google-ai-turboquant-memory-chip-stocks-samsung-micron.html | CNBC는 마이크론·샌디스크 하락률 미기재. |
| G6 | 그 직전 1년 메모리주는 이미 크게 올라 있었다. | 삼성전자 **약 +200%**, 마이크론·SK하이닉스 **+300% 이상**(지난 1년) | 2026-03-26 기준 | CNBC(위) | 차익실현 명분이 됐다는 해석(키움 한지영, 뉴시스 G7). |
| G7 | 이틀 누적 하락률. | 삼성전자 **-4.92%**, SK하이닉스 **-7.34%** | 03-26~27 | https://www.newsis.com/view/NISX20260327_0003567479 | 기사에 '제번스의 역설' 언급. KB증권 김동원: 인터넷 보급 때 종이 사용량이 오히려 늘었던 사례. |
| G8 | 그다음 거래일에도 하락이 이어졌다. | 삼성전자 **-1.89%(17만6,300원)**, SK하이닉스 **-5.31%(87만3천 원)** | 2026-03-30 | https://www.newsis.com/view/NISX20260330_0003569857 | 미·이란 긴장, 마이크론 실적 뒤 '사이클 정점' 우려도 겹침. KB 강다현: "효율 혁신은 수요 감소가 아닌 수요 확대를 유발해왔다". 키움 박유악: 터보퀀트·엔비디아 KVTC는 2027~2029년 서버 D램·eSSD 수요엔 부정적. |
| G9 | 시장 반응에 대한 대표 평가 | 클라우드플레어 CEO "구글의 딥시크", 퀼터 체비엇 "혁명이 아니라 진화" | 2026-03 | CNBC(위) | 세미애널리시스 Ray Wang: 모델 성능이 오르면 메모리 사용 증가는 피하기 어렵다. |

### D. 효율 기술이 반도체를 흔든 앞선 사례

| # | 사실 | 수치 | 날짜 | 실제로 연 URL | 메모 |
|---|---|---|---|---|---|
| D1 | 중국 딥시크의 저비용 AI 모델 충격으로 엔비디아 주가가 하루에 급락했다. | **약 -17%**, 시총 약 **6천억 달러**(포천) / 5,890억 달러(블룸버그 제목, 원문 미열람) | 2025-01-27 | https://fortune.com/2025/01/27/nvidia-deepseek-rout-tech-stocks/ · (블룸버그 제목) https://www.bloomberg.com/news/articles/2025-01-27/asml-sinks-as-china-ai-startup-triggers-panic-in-tech-stocks | "the worst one-day fall for any company in history"(InvestmentNews https://www.investmentnews.com/equities/nvidia-stock-slumps-17-amid-deepseek-shock-but-rival-shows-cracks/259082). 나스닥 -3% 넘게. 딥시크는 "600만 달러 미만"으로 개발했다고 주장(포천, 검증 불가한 회사 주장). |
| D2 | 같은 날 마이크로소프트 CEO가 제번스의 역설을 언급했다. | "Jevons paradox strikes again!" | 2025-01-27 | https://fortune.com/2025/01/27/microsoft-ceo-satya-nadella-deepseek-optimism-jevons-paradox/ | "AI가 효율적이고 쉬워질수록 사용량은 폭증할 것" |
| D3 | 제번스의 역설: 1865년 『석탄 문제』. 와트 증기기관 뒤 영국 석탄 소비가 오히려 급증. | 1865년 | — | https://en.wikipedia.org/wiki/Jevons_paradox | "연료를 아껴 쓰는 것이 소비 감소와 같다고 보는 것은 혼동" |
| T1 | 메타가 구글 TPU 도입을 협상한다는 보도에 엔비디아가 내렸다. | 엔비디아 **-2.6%**, 구글 **+1.6%** (종가) | 2025-11-25 | https://siliconangle.com/2025/11/25/nvidia-shares-drop-report-meta-may-buy-tpus-google/ | 디 인포메이션 보도. 2026년 임차, 2027년 자체 데이터센터 도입 검토. 확정 계약 아님. '자체 칩' 이야기는 메모리가 아니라 GPU 경쟁 이슈. |

### K. 한국 반도체 쏠림

| # | 사실 | 수치 | 날짜·기준 | 실제로 연 URL | 메모 |
|---|---|---|---|---|---|
| K1 | 2025년 반도체 수출 역대 최대 | **1,734억 달러(+22.2%)**, 총수출 7,097억 달러 → 비중 **약 24%**(계산) | 2025년 연간(2026-01-01 발표) | https://www.newsis.com/view/NISX20260101_0003462013 | 12월 반도체 208억 달러(+43.2%). |
| K2 | 2026년 9월 반도체 수출 | **603억 달러(+262.8%)**, 총수출의 **49.9%** | 2026-09(10-01 발표) | https://news.mtn.co.kr/news-detail/2026100111035751735 | |
| K3 | 2026년 10월 반도체 수출 | **564.4억 달러(+259.4%)**, 총수출 1,152.8억 달러(+93.7%) → 약 **49%**(계산) | 2026-10(11-01 발표, 잠정) | https://newsis.com/view/NISX20261101_0003849625 | 1~10월 누적 총수출 9,300억 달러. 관세청 확정치(1,154.1억 달러)와 약간 다름. |
| K4 | 코스피 사상 최고 종가권, SK하이닉스 시총 1위 | 코스피 **9,114.55**, SK하이닉스 **291만9천 원**(시총 2,080조 원) | 2026-06-22 | https://v.daum.net/v/20260622170019577?f=p | 삼성전자 보통주를 제치고 약 25년 7개월 만의 1위 교체(우선주 합치면 삼성이 큼). 3/30 종가 87만3천 원 대비 약 3.3배(계산). |
| K5 | 11월 초 급락: 코스피 이틀간 -10.98% | 11-06 코스피 **-6.02%, 5,059.69**, 서킷브레이커 09:03:33(역대 가장 빠름) | 2026-11-06 | https://supple.kr/news/cmw4qhoejp4tral9p6xvbmwcm (연합뉴스 기사 전재) | 원인: 미국 중간선거 뒤 데이터센터 규제 강화 우려, AI 투자 수익성 의구심, 외국인 6거래일 연속 11.99조 원 순매도. |
| K6 | 두 종목 시총과 비중 | 합산 **1,930조 원**, 6/25 최고(약 4,175조 원) 대비 **-53.77%**, 코스피 비중 **57.11% → 46%대** | 2026-11-06 | 위와 같음 · https://biz.sbs.co.kr/amp/article/20000344721 | 삼성전자 -6.35%(18만8,700원), SK하이닉스 -10.44%. |
| K7 | 미국 반도체지수(SOX) 하루 -12.25% | 9,011.14, 기록상 두 번째 큰 하루 낙폭, 6/22 최고치 대비 -38.4% | 2026-11-05 | https://247wallst.com/investing/2026/11/06/chip-stocks-just-had-their-second-worst-day-on-record/ | 마이크론 -17.46%. |

## 2. 사건 연표

- 1865 — 제번스 『석탄 문제』 (D3)
- 2025-01-27 — 딥시크 충격, 엔비디아 -17% (D1), 나델라 "제번스의 역설" (D2)
- 2025-11-25 — 메타-구글 TPU 협상 보도, 엔비디아 -2.6% (T1)
- 2026-03-24 — 구글 리서치 터보퀀트 공개 (G1)
- 2026-03-26 — SK하이닉스 -6.23%, 삼성전자 -4.71%, 코스피 -3.22% (G3, G4)
- 2026-03-30 — SK하이닉스 87만3천 원 (G8)
- 2026-06-22 — 코스피 9,114.55, SK하이닉스 291만9천 원·시총 1위 (K4)
- 2026-06-25 — 두 종목 합산 시총 최고, 코스피 비중 57.11% (K6)
- 2026-09~10 — 반도체 수출이 총수출의 약 절반 (K2, K3)
- 2026-11-05 — SOX -12.25% (K7)
- 2026-11-06 — 코스피 -6.02%, 두 종목 비중 46%대 (K5, K6)

## 3. 쓰면 안 되는 주장

- "구글이 메모리 반도체를 필요 없게 만들었다" — 터보퀀트는 추론 때 KV 캐시만 줄이는 연구 단계 기술이다. 모델 가중치·학습용 메모리는 그대로.
- "AI 속도가 8배 빨라졌다" — 8배는 H100에서 어텐션 일부 계산 기준(G2).
- "11월 반도체 폭락은 구글 때문" — 11월 급락 원인으로 보도된 것은 중간선거 뒤 데이터센터 규제 우려·차익실현 등이며 구글 발표가 아니다(K5).
- "구글이 TPU를 메타에 판다(계약 체결)" — 2025-11 보도는 '협상 중'(T1).
- "딥시크가 600만 달러로 AI를 만들었다(사실)" — 회사 주장일 뿐, 검증되지 않음.
- 제번스의 역설이 '항상' 성립한다는 단정 — 수요가 가격에 얼마나 민감한지에 따라 다르다.

## 4. 확인 못 한 항목

- 3월 25~26일 마이크론·샌디스크의 정확한 하락률(검색 요약에 샌디스크 약 -11%, 웨스턴디지털 약 -7%가 있었으나 원문 미확인 → 사용 안 함).
- 2026-11-25 기준 코스피·두 종목 최신 종가와 시총 비중(11-06 기사 이후 수치 미확인 → 영상에서는 "11월 초" 기준으로만 말함).
- 터보퀀트 공식 코드 공개·상용 적용 여부.
- 2026년 1월 D램·낸드 계약가격 인상률(트레이딩키 기사에만 있음 → 사용 안 함).

## 출처 목록

- Google Research Blog, "TurboQuant: Redefining AI efficiency with extreme compression" (2026-03-24) — https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
- CNBC, "A Google AI breakthrough is pressuring memory chip stocks from Samsung to Micron" (2026-03-26) — https://www.cnbc.com/2026/03/26/google-ai-turboquant-memory-chip-stocks-samsung-micron.html
- TradingKey, "Samsung, SK Hynix Routed as Google 'TurboQuant' Rattles Chip Sector" (2026-03-26) — https://www.tradingkey.com/analysis/stocks/us-stocks/261722379-samsung-hk-hynix-memory-hbm-dram-google-turboquant-semi-conductor-tradingkey
- SBS Biz, 「[애프터마켓 브리핑] 구글 '터보퀀트' 충격…코스피 5500선 반납」 (2026-03-26) — https://biz.sbs.co.kr/amp/article/20000300112
- 뉴시스, 「직격탄 맞은 삼전·하닉 주가…증권가는 우려·기대 공존[터보퀀트 쇼크③]」 (2026-03-27) — https://www.newsis.com/view/NISX20260327_0003567479
- 뉴시스, 「삼전 1.89%↓·SK하닉 5.31%↓마감…증권가 "매수기회"」 (2026-03-30) — https://www.newsis.com/view/NISX20260330_0003569857
- Fortune, Nvidia DeepSeek rout (2025-01-27) — https://fortune.com/2025/01/27/nvidia-deepseek-rout-tech-stocks/
- Fortune, Satya Nadella Jevons paradox (2025-01-27) — https://fortune.com/2025/01/27/microsoft-ceo-satya-nadella-deepseek-optimism-jevons-paradox/
- InvestmentNews, "Nvidia stock slumps 17% amid DeepSeek shock" (2025-01-27) — https://www.investmentnews.com/equities/nvidia-stock-slumps-17-amid-deepseek-shock-but-rival-shows-cracks/259082
- Wikipedia, "Jevons paradox" — https://en.wikipedia.org/wiki/Jevons_paradox
- SiliconANGLE, Nvidia shares drop on report Meta may buy TPUs from Google (2025-11-25) — https://siliconangle.com/2025/11/25/nvidia-shares-drop-report-meta-may-buy-tpus-google/
- 뉴시스, 2025년 연간 수출입 동향 (2026-01-01) — https://www.newsis.com/view/NISX20260101_0003462013
- 머니투데이방송(MTN), 「수출 절반이 반도체...韓 수출 1조달러 '청신호'」 (2026-10-01) — https://news.mtn.co.kr/news-detail/2026100111035751735
- 뉴시스, 「누적 수출 사상 첫 9000억弗 돌파」 (2026-11-01) — https://newsis.com/view/NISX20261101_0003849625
- 헤럴드경제(다음 뉴스), 「시총 1위 바뀐날, 코스피 종가 최고치 또 갈아치웠다」 (2026-06-22) — https://v.daum.net/v/20260622170019577?f=p
- 연합뉴스(전재), 「669개종목 연중 최저가·코스피 이틀간 11% 폭락…숫자로 본 증시급락」 (2026-11-06) — https://supple.kr/news/cmw4qhoejp4tral9p6xvbmwcm
- SBS Biz, 「'삼전닉스' 시총 2000조 붕괴…역대 가장 빠른 서킷브레이커」 (2026-11-06) — https://biz.sbs.co.kr/amp/article/20000344721
- 24/7 Wall St., "Chip Stocks Just Had Their Second-Worst Day on Record" (2026-11-06) — https://247wallst.com/investing/2026/11/06/chip-stocks-just-had-their-second-worst-day-on-record/
