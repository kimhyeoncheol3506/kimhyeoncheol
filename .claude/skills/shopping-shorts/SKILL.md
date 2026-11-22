---
name: "shopping-shorts"
description: "쇼핑 쇼츠 원스톱 제작. 사용자가 폰에서 고른 상품(쿠팡 링크, 상품명, 캡처)을 '쇼핑쇼츠 업로딩' 프로젝트 채팅에 보내거나 '쇼핑쇼츠', '쇼핑 쇼츠 만들어줘'라고 하면 실행. 쿠팡에서 상품 확인 → 구매 전환형 대본 → 여의도여자 더빙 → 상품 사진/직접 찍은 영상으로 25~35초 세로 영상 렌더 → 제목·설명(쿠팡 파트너스 고지)·고정댓글까지 만들어 바탕화면 쇼핑쇼츠 폴더에 둔다. 업로드는 하지 않는다."
---

# 쇼핑 쇼츠 원스톱

결과 폴더: `C:\Users\Admin\Desktop\쇼핑쇼츠\<YYYYMMDD>_<상품짧은이름>\`
렌더러: `scripts/render_short.py <폴더>` (표준 라이브러리 + ffmpeg, Aside 파이썬으로 실행)

## 0. 절대 규칙
- **남의 영상(틱톡·샤오홍슈·유튜브 쇼핑 영상)을 내려받아 쓰지 않는다.** 저작권 침해이고, 유튜브 '재사용 콘텐츠'로 수익화가 막힌다. 사용자가 원해도 대신 아래 소재를 쓴다고 설명한다.
- 소재 우선순위
  1. 사용자가 폰으로 찍어 보낸 사진·영상(제일 잘 팔림)
  2. 쿠팡 상품 페이지의 대표 이미지(쿠팡 파트너스 홍보 목적, 원본 그대로·왜곡 없이)
  3. (선택) 대표 이미지로 만든 AI 움직임 클립: Digen Ultra 유료 결과물만(약관 확인됨). 무료 결과물은 워터마크·라이선스 문제로 쓰지 않음
  4. 판매자·브랜드 공식 영상은 **서면 허락을 받은 경우만**
- 쿠팡 페이지는 상품당 **한 번만 열고 스크롤 반복 금지**(봇 차단으로 '페이지 없음'이 뜸). 막히면 다른 탭에서 몇 분 뒤 다시.
- 사실만 말한다. 페이지에 없는 효능·배터리 시간·"최저가 보장"은 쓰지 않는다. 가격은 확인 날짜를 남기고 설명란에 "가격은 변동될 수 있음".
- 쿠팡 파트너스 로그인·비밀번호는 받지 않는다. 링크 생성이 필요하면 사용자가 브라우저에서 직접 로그인하도록 탭을 띄우고 기다린다.
- 업로드하지 않는다. 사용자가 최종 검수 후 직접 올린다.

## 1. 입력 받기
쿠팡 링크 / 상품명 / 캡처 중 무엇이든. 캡처면 상품명·가격을 읽어 쿠팡 검색(`https://www.coupang.com/np/search?q=...`)에서 같은 상품(브랜드·모델명 일치)을 고른다. 애매하면 후보 2~3개를 ask_user_question 으로 묻는다. 사용자가 사진·영상을 같이 보냈으면 attachments 에서 `media/` 로 복사한다.

## 2. 상품 조사 (상품 페이지 1회)
`page.evaluate(()=>document.body.innerText)` 로 상품명, 판매가·정가·할인율, 배송(내일 도착/무료배송), 모델명, 옵션(색상), 스펙 표, 상품평 수, "한 달간 N명 이상 구매" 문구를 뽑는다.
대표 이미지: `img` 중 `thumbnail.coupangcdn.com/.../retail/images` 또는 `vendor_inventory` 주소를 `remote/1000x1000ex` 로 바꿔 받는다(Referer: https://www.coupang.com/). 5~7장, `media/p1.png…`. 받은 뒤 HTML 그리드로 띄워 눈으로 확인(엉뚱한 배너·다른 상품 제외).
결과를 `research.md` 에 적는다(출처 URL, 확인 날짜, 숫자의 출처 문구 그대로).

## 3. 구매 전환형 대본 (25~35초, 7~9장면)
references/script_formula.md 의 공식대로. 장면마다 `say`(말할 문장, 숫자는 한글로: "이만 삼천팔백 원"), `caption`(화면 자막 한두 줄, 줄당 12자 안팎, 핵심어는 `*별표*` 로 노랑 강조, 줄바꿈 `\n`), 필요하면 `badge`(가격 등 큰 노란 박스), `cta`(마지막 장면 빨간 버튼 문구), `sfx`(pop.wav/ding.wav/tick.wav), `zoom`(기본 0.07, 음수면 줌아웃).
`top_title` 은 영상 내내 위에 고정되는 한 줄(예: "출근 전 *10초* 앞머리 살리기").

## 4. project.json
```json
{"product": "...", "source_url": "...", "checked_at": "YYYY-MM-DD",
 "top_title": "...", "bgm_gain": 0.12,
 "scenes": [{"media": "media/p1.png", "voice": "voice/v01.wav", "say": "...", "caption": "...", "sfx": "pop.wav"}]}
```
media 가 영상(mp4/mov)이면 꽉 차게 잘라 쓰고 `clip_start` 로 시작점을 고른다. 사진이면 흐린 배경 위에 제품을 크게 두고 천천히 확대한다.

## 5. 더빙 (여의도여자, Voicebox)
Voicebox(http://127.0.0.1:17493)가 꺼져 있으면 사용자에게 Voicebox 앱을 켜 달라고 한다(쉘이 되면 `explorer.exe "C:\Program Files\Voicebox\voicebox.exe"`).
REPL 에서 장면마다:
```js
const VB='http://127.0.0.1:17493';
const prof=(await (await fetch(VB+'/profiles')).json()).find(p=>p.name==='여의도여자').id;
const j=await (await fetch(VB+'/generate',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({profile_id:prof,text:say,language:'ko',engine:'qwen_custom_voice',seed:7,instruct:'밝고 생기 있는 쇼핑 쇼츠 내레이션. 또렷하고 약간 빠르게, 친구에게 추천하듯 자연스럽게. 숫자와 핵심 단어에 힘을 준다.'})})).json();
// /history/{id} 를 1초마다 읽어 status==='completed' 가 되면 /audio/{id} 를 voice/vNN.wav 로 저장 (한 문장 약 30~60초)
```
REPL 120초 제한 때문에 한 번에 2~3문장씩. 발음이 이상하면 seed 를 바꿔 다시.

## 6. 렌더
- 쉘이 되면: `& "$env:USERPROFILE\.aside\runtime\bin\python.cmd" "<스킬>\scripts\render_short.py" "<폴더>"`
- 쉘이 안 되면: `scripts/만들기.bat` 를 프로젝트 폴더에 복사해 두고 사용자에게 더블클릭을 부탁한다(끝나면 영상이 열림).
- 실패하면 `render_log.txt` 의 마지막 부분을 읽고 고친다.

## 7. 검수
`out/sheet.jpg`(1초 간격 프레임) 를 보고: 자막이 제품을 가리지 않는지, 글자 잘림, 가격 배지, 마지막 CTA, 왼쪽 위 '광고 · 쿠팡 파트너스' 표기. 길이 25~35초.

## 8. 업로드 정보 (`업로드정보.txt`)
- 제목: 40자 안팎, 대상+문제+결과 (예: "출근 전 10초 앞머리 살리는 무선 미니 고데기 #shorts")
- 설명: 첫 줄 한 줄 요약 → 상품명·옵션 → 파트너스 링크(있으면) → 고지문 **"이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."** → "가격은 YYYY-MM-DD 기준이며 변동될 수 있습니다." → 해시태그 3~5개
- 고정 댓글: 링크 + 고지문 한 줄
- 파트너스 링크가 없으면 `[파트너스 링크 넣기]` 자리표시를 남기고 사용자에게 알린다(쿠팡 파트너스 > 링크 생성에서 상품 URL 붙여넣기).

## 9. 보고
완성 영상 경로, 길이, 프레임 시트 이미지, 업로드정보 요약, 확인이 필요한 것(파트너스 링크, 가격 변동, 발음 이상한 장면)을 짧게.
