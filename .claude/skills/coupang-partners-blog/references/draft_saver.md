# 쿠팡 글 헬퍼 (Aside REPL, 검증 2026-11-17)

먼저 `..\..\naver-scheduled-autoupload\references\uploader.md`의 NB 탭 생성 + EL, EV, IB, pasteRaw, pasteImgHere, verifyImgs, fillBody, openWriter를 정의한다. 파트너스 탭은 `globalThis.CP = await openTab('https://partners.coupang.com/')`.

```js
// 상품 검색 (상위 8개, R:true = 로켓 배지)
globalThis.psearch2=async(q)=>{ await CP.goto('https://partners.coupang.com/#affiliate/ws/link/0/'+encodeURIComponent(q)); await sleep(3000);
 return await CP.evaluate(()=>[...document.querySelectorAll('.product-item')].slice(0,8).map((e,i)=>i+': '+e.querySelector('.product-description')?.textContent.trim()+' | '+(e.querySelector('.sale-price')?.textContent||'')+' | R:'+!!e.querySelector('img[alt=badge]'))); };

// 링크 생성: name = 카드 제목 앞부분 (부분일치)
globalThis.mklink2=async(q,name)=>{ await CP.goto('https://partners.coupang.com/#affiliate/ws/link/0/'+encodeURIComponent(q)); await sleep(3000);
 const it=CP.locator('.product-item').filter({hasText:name}).first(); const full=(await it.locator('.product-description').textContent()).trim(); const price=await it.locator('.sale-price').textContent();
 await it.hover(); await it.locator('.btn-generate-link').click({force:true});
 for(let i=0;i<12;i++){ await sleep(800); const t=await CP.evaluate(()=>{const m=document.body.innerText.match(/https:\/\/link\.coupang\.com\/a\/\w+/);return m&&m[0]}); if(t){ const title=decodeURIComponent((CP.url().match(/product%5Btitle%5D=([^&]+)/)||[])[1]||''); return {name:title||full,price,url:t}; } }
 return {name,err:'nolink'}; };

// 카드 렌더 (about:blank에 document.write → #c 스크린샷). setContent 없음.
globalThis.renderCards=async(d,cards)=>{ const pg2=await openTab('about:blank'); for(const [n,h] of cards){ await pg2.evaluate(x=>{document.open();document.write(x);document.close();},h); await sleep(400); await fs.writeFile(d+`\\${n}.png`, await pg2.locator('#c').screenshot({type:'png'})); } await closeTab(pg2); };
globalThis.coverHtml=(tag,title,sub,chips)=>`<html><body style="margin:0"><div id=c style="width:900px;height:900px;background:#f2f6f5;font-family:'Malgun Gothic';display:flex;flex-direction:column;justify-content:center;align-items:center;"><div style="background:#1f7a5c;color:#fff;font-size:30px;padding:10px 26px;border-radius:30px;font-weight:700">${tag}</div><div style="font-size:76px;font-weight:900;color:#17352b;margin-top:40px;text-align:center;line-height:1.25">${title}</div><div style="font-size:36px;color:#333;margin-top:30px">${sub}</div><div style="display:flex;gap:18px;margin-top:50px">${chips.map(x=>`<div style="background:#ffd84d;font-size:34px;font-weight:800;padding:18px 26px;border-radius:16px">${x}</div>`).join('')}</div><div style="font-size:24px;color:#777;margin-top:50px">이 포스팅은 쿠팡 파트너스 활동의 일환으로 수수료를 제공받습니다</div></div></body></html>`;
globalThis.tableHtml=(title,sub,head,rows)=>`<html><body style="margin:0"><div id=c style="width:900px;padding:50px 40px;background:#fff;font-family:'Malgun Gothic'"><div style="font-size:44px;font-weight:900;color:#17352b;margin-bottom:10px">${title}</div><div style="font-size:22px;color:#888;margin-bottom:26px">${sub}</div><table style="width:100%;border-collapse:collapse;font-size:25px"><tr style="background:#1f7a5c;color:#fff">${head.map(h=>`<th style="padding:14px">${h}</th>`).join('')}</tr>${rows.map((r,i)=>`<tr style="background:${i%2?'#f2f6f5':'#fff'}">${r.map((c,j)=>`<td style="padding:16px 10px;border-bottom:1px solid #ddd;${j==0?'font-weight:800;':''}">${c}</td>`).join('')}</tr>`).join('')}</table></div></body></html>`;

// post = {title, category, tags[10], body:[['p',text],['h',text],['quote',text],['img','card1.png'],['link','표시문구',linkIndex]]}
globalThis.toHtml=(p,d,LL)=>{ const e=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;'); let h=`<p><b><span style="color:#d0021b;font-size:19px">이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</span></b></p><p>&nbsp;</p>`; const im=[]; for(const [t,a,b] of p.body){ if(t==='p') h+=a.split('\n').map(x=>`<p>${e(x)}</p>`).join('')+'<p>&nbsp;</p>'; else if(t==='h') h+=`<p><b><span style="font-size:22px">${e(a)}</span></b></p>`; else if(t==='quote') h+=`<blockquote>${a.split('\n').map(x=>`<p>${e(x)}</p>`).join('')}</blockquote>`; else if(t==='link') h+=`<p>▶ <a href="${LL[b].url}">${e(a)}</a></p>`; else if(t==='img'){ im.push(d+'\\'+a); h+=`<p>@@IMG${im.length}@@</p>`; } } return {...p,html:h,images:im}; };

// 임시저장 (카테고리·태그를 발행창에서 넣고 닫은 뒤 저장 → 임시저장에 유지됨)
globalThis.saveDraft=async(p)=>{ await openWriter();
 await EL('.se-documentTitle .se-text-paragraph').first().click(); await NB.keyboard.insertText(p.title); await sleep(300);
 const fb=await fillBody(p); if(fb!=='ok') return fb; const vi=await verifyImgs(); const nl=await EV(()=>(document.querySelector('.se-components-wrap').innerHTML.match(/link\.coupang\.com/g)||[]).length);
 let s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "발행" \[ref=(\w+)\]/)[1]).click();
 for(let w=0;w<10;w++){ await sleep(800); s=await snapshot(NB,{interactive:true}); if(/button "카테고리 목록 버튼"/.test(s.tree)) break; if(w===4){const bb=s.tree.match(/button "발행" \[ref=(\w+)\]/); if(bb) await NB.locator(bb[1]).click();} }
 await NB.locator(s.tree.match(/button "카테고리 목록 버튼" \[ref=(\w+)\]/)[1]).click(); await sleep(800);
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(new RegExp(`button "${p.category}" \\[ref=(\\w+)\\]`))[1]).click(); await sleep(700);
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/combobox "태그 입력[^"]*" \[ref=(\w+)\]/)[1]).click();
 for(const t of p.tags){ await NB.keyboard.insertText(t); await sleep(200); await NB.keyboard.press('Enter'); await sleep(350);}
 s=await snapshot(NB,{interactive:true}); const cat=s.tree.match(/카테고리 목록 버튼" \[ref=\w+\][^:\n]*: "([^"]*)"/)?.[1]; const tg=(s.tree.match(/heading "태그 편집"[\s\S]*?text: "([^"]*)"/)||[])[1];
 await NB.locator(s.tree.match(/button "발행 설정 닫기" \[ref=(\w+)\]/)[1]).click(); await sleep(600);
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "저장" \[ref=(\w+)\]/)[1]).click(); await sleep(3000);
 s=await snapshot(NB,{interactive:true}); return {vi,nl,cat,tg,drafts:s.tree.match(/임시저장된 글 보기, (\d+)개/)?.[1]}; };
```

메모: SmartEditor는 `<a href>`를 `span.se-link[data-href]`로 바꾼다. 링크 확인은 innerHTML에서 link.coupang.com 개수로.
