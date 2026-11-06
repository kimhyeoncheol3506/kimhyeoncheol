import sharp from 'sharp';
const [, , out, scale, ...files] = process.argv;
const imgs = await Promise.all(files.map(async f => { const m = await sharp(f).metadata(); return { f, w: Math.round(m.width * +scale), h: Math.round(m.height * +scale) }; }));
const W = Math.max(...imgs.map(i => i.w)), H = imgs.reduce((s, i) => s + i.h, 0);
let y = 0; const comp = [];
for (const i of imgs) { comp.push({ input: await sharp(i.f).resize(i.w, i.h).png().toBuffer(), left: 0, top: y }); y += i.h; }
await sharp({ create: { width: W, height: H, channels: 3, background: '#000' } }).composite(comp).png().toFile(out);
