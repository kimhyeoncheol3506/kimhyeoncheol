# 네이버 예약 업로더 (Aside REPL용, 검증됨 2026-11-05)

먼저 `globalThis.NB = await openTab('https://blog.naver.com/GoBlogWrite.naver'); NB.on('dialog',d=>d.accept().catch(()=>{}));` 로 탭을 만든 뒤 아래를 실행한다.

주의: SmartEditor는 화면 밖 그림을 빈 svg로 지연 표시하므로, 그림 확인은 verifyImgs()처럼 하나씩 화면으로 스크롤해서 http 주소인지 본다. 텍스트 덩어리가 <hr>/<table>/<blockquote>로 끝나면 빈 문단을 붙여야 다음 그림이 들어간다(fillBody에 반영).

```js
globalThis.EL=sel=>NB.frameLocator('#mainFrame').locator(sel);

globalThis.EV=async(fn,arg)=>{ const a=NB.frames(); for(let i=a.length-1;i>=0;i--){ let nm=''; try{nm=a[i].name()}catch{} if(nm!=='mainFrame') continue; try{ if(await a[i].evaluate(()=>!!document.querySelector('.se-documentTitle'))) return await a[i].evaluate(fn,arg);}catch{} } throw new Error('no editor frame'); };

globalThis.IB=async()=>{ const a=NB.frames().filter(f=>{try{return f.name().startsWith('input_buffer')}catch{return false}}); for(let i=a.length-1;i>=0;i--){ try{ if(await a[i].evaluate(()=>document.hasFocus())) return a[i]; }catch{} } return a[a.length-1]; };

globalThis.pasteRaw=async(html)=>{ const ib=await IB(); await ib.evaluate(h=>{const dt=new DataTransfer(); dt.setData('text/html',h); dt.setData('text/plain',h.replace(/<[^>]+>/g,'')); document.activeElement.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));},html); await sleep(1800); };

globalThis.pasteImgHere=async(file)=>{ const b=(await fs.readFile(file)).toString('base64'); const cnt=()=>EV(()=>document.querySelectorAll('.se-component.se-image').length); const n0=await cnt(); const ib=await IB(); await ib.evaluate(([b,name])=>{const bin=atob(b); const u=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i); const dt=new DataTransfer(); dt.items.add(new File([u],name,{type:'image/png'})); document.activeElement.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));},[b,'img'+Date.now()+'.png']); for(let i=0;i<30;i++){ await sleep(700); if((await cnt())>n0){ await sleep(2500); return true; } } return false; };

globalThis.verifyImgs=async()=>{ const n=await EV(()=>document.querySelectorAll('.se-component.se-image').length); let ok=0; for(let k=0;k<n;k++){ await EV(k=>document.querySelectorAll('.se-component.se-image')[k].scrollIntoView({block:'center'}),k); await sleep(1200); if(await EV(k=>document.querySelectorAll('.se-component.se-image img')[k]?.src.startsWith('http'),k)) ok++; } return {n,ok}; };

globalThis.fillBody=async(post)=>{ await EL('.se-component.se-text .se-text-paragraph').last().click(); await sleep(300); const parts=post.html.split(/<p[^>]*>\s*@@IMG(\d+)@@\s*<\/p>/); for(let i=0;i<parts.length;i++){ if(i%2===0){ if(parts[i].replace(/<p>(&nbsp;|\s)*<\/p>/g,'').trim()){ let ch=parts[i]; if(/(<hr[^>]*>|<\/table>|<\/blockquote>)\s*$/i.test(ch)) ch+='<p>&nbsp;</p>'; await pasteRaw(ch); } } else { if(!(await pasteImgHere(post.images[+parts[i]-1]))) return 'img fail '+parts[i]; await sleep(600);} }
 const all=await EV(()=>document.querySelector('.se-components-wrap').innerText.replace(/\s+/g,'')); let pos=-1; for(let i=0;i<parts.length;i+=2){ const t=parts[i].replace(/<[^>]+>/g,'').replace(/&nbsp;/g,'').replace(/&amp;/g,'&').replace(/\s+/g,'').slice(0,25); if(!t) continue; const q=all.indexOf(t); if(q<pos) return 'order wrong '+i; pos=q; } return 'ok'; };

globalThis.openWriter=async()=>{ await NB.goto('https://blog.naver.com/GoBlogWrite.naver').catch(()=>{}); await sleep(6000); for(let i=0;i<6;i++){ try{ await EV(()=>1); break; }catch{ await sleep(2000);} } await sleep(1000); for(let k=0;k<2;k++){ const c=EL('.se-popup-button-cancel'); if(await c.count().catch(()=>0)){ await c.first().click().catch(()=>{}); await sleep(800);} const h=EL('.se-help-panel-close-button'); if(await h.count().catch(()=>0)){ await h.first().click().catch(()=>{}); await sleep(500);} } };

globalThis.loadPost=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));

globalThis.naverSchedule=async(post)=>{ await openWriter();
 await EL('.se-documentTitle .se-text-paragraph').first().click(); await NB.keyboard.insertText(post.title); await sleep(300);
 const fb=await fillBody(post); if(fb!=='ok') return fb;
 const chk=await EV(()=>({imgs:[...document.querySelectorAll('.se-component.se-image')].filter(c=>c.querySelector('img[src^="http"]')).length, len:document.querySelector('.se-components-wrap')?.innerText.length, marker:/@@IMG/.test(document.body.innerText), title:document.querySelector('.se-documentTitle')?.innerText.trim()}));
 const vi=await verifyImgs(); chk.imgs=vi.ok; chk.imgN=vi.n; if(chk.marker||vi.ok!==post.images.length||vi.n!==post.images.length) return {fail:true,chk};
 let s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "발행" \[ref=(\w+)\]/)[1]).click(); for(let w=0;w<10;w++){ await sleep(800); s=await snapshot(NB,{interactive:true}); if(/button "카테고리 목록 버튼"/.test(s.tree)) break; if(w===4){ const bb=s.tree.match(/button "발행" \[ref=(\w+)\]/); if(bb) await NB.locator(bb[1]).click(); } }
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "카테고리 목록 버튼" \[ref=(\w+)\]/)[1]).click(); await sleep(800);
 s=await snapshot(NB,{interactive:true}); const esc=post.category.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); await NB.locator(s.tree.match(new RegExp(`button "${esc}" \\[ref=(\\w+)\\]`))[1]).click(); await sleep(700);
 s=await snapshot(NB,{interactive:true}); const cat=s.tree.match(/button "카테고리 목록 버튼" \[ref=\w+\][^:\n]*: "([^"]*)"/)?.[1]; const nz=x=>(x||'').replace(/[^가-힣A-Za-z]/g,''); if(nz(cat)!==nz(post.category)) return {fail:'cat',cat};
 await NB.locator(s.tree.match(/combobox "태그 입력[^"]*" \[ref=(\w+)\]/)[1]).click(); for(const t of post.tags.map(x=>x.replace(/[^가-힣A-Za-z0-9]/g,'')).filter(Boolean).slice(0,10)){ await NB.keyboard.insertText(t); await sleep(200); await NB.keyboard.press('Enter'); await sleep(400);} 
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/label "예약" \[ref=(\w+)\]/)[1]).click(); await sleep(800);
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/textbox "\d{4}\. \d{2}\. \d{2}" \[ref=(\w+)\]/)[1]).click(); await sleep(700);
 const day=String(+post.date.slice(8,10)); s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(new RegExp(`button "${day}" \\[ref=(\\w+)\\]`))[1]).click().catch(()=>{}); await sleep(600);
 s=await snapshot(NB,{interactive:true}); let cb=[...s.tree.matchAll(/combobox "\d{2}" \[ref=(\w+)\]/g)].map(m=>m[1]); await NB.locator(cb[0]).selectOption(post.time.slice(0,2)); await sleep(400); s=await snapshot(NB,{interactive:true}); cb=[...s.tree.matchAll(/combobox "\d{2}" \[ref=(\w+)\]/g)].map(m=>m[1]); await NB.locator(cb[1]).selectOption(post.time.slice(3,5)); await sleep(500);
 s=await snapshot(NB,{interactive:true}); const vals=[...s.tree.matchAll(/combobox "(\d{2})" \[ref=\w+\]/g)].map(m=>m[1]); const dateNow=s.tree.match(/textbox "(\d{4}\. \d{2}\. \d{2})"/)?.[1]; const tagsNow=(s.tree.match(/heading "태그 편집"[\s\S]*?text: "([^"]*)"/)||[])[1];
 const want=post.date.replace(/-/g,'. '); if(dateNow!==want||vals[0]!==post.time.slice(0,2)||vals[1]!==post.time.slice(3,5)) return {fail:'time',dateNow,vals};
 const res={chk,cat,dateNow,time:vals.join(':'),tagsNow}; if(post.dry) return res;
 const pubs=[...s.tree.matchAll(/button "발행" \[ref=(\w+)\]/g)].map(m=>m[1]); await NB.locator(pubs[pubs.length-1]).click(); await sleep(6000); res.url=NB.url(); return res; };

globalThis.listScheduled=async()=>{ await openWriter(); let s=await snapshot(NB,{interactive:true}); const b=s.tree.match(/button "예약 발행 건" \[ref=(\w+)\]/); if(!b) return []; await NB.locator(b[1]).click(); await sleep(1500); s=await snapshot(NB,{interactive:true}); const items=[...s.tree.matchAll(/button "([^"]+?)\s?(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2})" \[ref=\w+\]/g)].map(m=>({title:m[1].trim(),when:m[2]})); const c=s.tree.match(/button "팝업닫기" \[ref=(\w+)\]/); if(c) await NB.locator(c[1]).click().catch(()=>{}); return items; };

globalThis.openSched=async(title)=>{ await openWriter(); let s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "예약 발행 건" \[ref=(\w+)\]/)[1]).click(); await sleep(1500); s=await snapshot(NB,{interactive:true}); const esc=title.slice(0,12).replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); const m=s.tree.match(new RegExp(`button "${esc}[^"]*" \\[ref=(\\w+)\\]`)); await NB.locator(m[1]).click(); await sleep(7000); const c=EL('.se-popup-button-confirm'); if(await c.count().catch(()=>0)){ await c.first().click().catch(()=>{}); await sleep(3000);} };

globalThis.retimeNaver=async(title,date,time)=>{ await openWriter(); let s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "예약 발행 건" \[ref=(\w+)\]/)[1]).click(); await sleep(1500); s=await snapshot(NB,{interactive:true}); const esc=title.slice(0,15).replace(/[.*+?^${}()|[\]\\]/g,'\\// 사용:'); const m=s.tree.match(new RegExp(`button "${esc}[^"]*" \\[ref=(\\w+)\\]`)); if(!m) return 'not in list'; await NB.locator(m[1]).click(); await sleep(7000); const c=EL('.se-popup-button-confirm'); if(await c.count().catch(()=>0)){ await c.first().click().catch(()=>{}); await sleep(3000);} 
 const t=await EV(()=>document.querySelector('.se-documentTitle')?.innerText.trim()); if(!t||!t.startsWith(title.slice(0,10))) return 'wrong post loaded: '+t;
 s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(/button "발행" \[ref=(\w+)\]/)[1]).click(); await sleep(1500);
 s=await snapshot(NB,{interactive:true}); if(!/radio "예약" \[ref=\w+\] \[hidden\] \[checked\]/.test(s.tree)){ await NB.locator(s.tree.match(/label "예약" \[ref=(\w+)\]/)[1]).click(); await sleep(800); s=await snapshot(NB,{interactive:true}); }
 await NB.locator(s.tree.match(/textbox "\d{4}\. \d{2}\. \d{2}" \[ref=(\w+)\]/)[1]).click(); await sleep(700); const day=String(+date.slice(8,10)); s=await snapshot(NB,{interactive:true}); await NB.locator(s.tree.match(new RegExp(`button "${day}" \\[ref=(\\w+)\\]`))[1]).click().catch(()=>{}); await sleep(600);
 s=await snapshot(NB,{interactive:true}); let cb=[...s.tree.matchAll(/combobox "\d{2}" \[ref=(\w+)\]/g)].map(m=>m[1]); await NB.locator(cb[0]).selectOption(time.slice(0,2)); await sleep(400); s=await snapshot(NB,{interactive:true}); cb=[...s.tree.matchAll(/combobox "\d{2}" \[ref=(\w+)\]/g)].map(m=>m[1]); await NB.locator(cb[1]).selectOption(time.slice(3,5)); await sleep(500);
 s=await snapshot(NB,{interactive:true}); const vals=[...s.tree.matchAll(/combobox "(\d{2})" \[ref=\w+\]/g)].map(m=>m[1]); const dn=s.tree.match(/textbox "(\d{4}\. \d{2}\. \d{2})"/)?.[1]; if(dn!==date.replace(/-/g,'. ')||vals.join(':')!==time) return {fail:true,dn,vals};
 const pubs=[...s.tree.matchAll(/button "발행" \[ref=(\w+)\]/g)].map(m=>m[1]); await NB.locator(pubs[pubs.length-1]).click(); await sleep(5000); return 'ok '+dn+' '+time; };

// 사용: const p=await loadPost('...post1.json'); console.log(JSON.stringify(await naverSchedule(p)));  // dry 확인은 {...p,dry:true}
```
