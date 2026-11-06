// Contact sheet of a frame folder. usage: node tools/sheet.mjs <dir> <out.png> [cols=8] [tileW=320]
import sharp from 'sharp';
import fs from 'node:fs';
const [, , dir, outFile, colsS = '8', twS = '320'] = process.argv;
const files = fs.readdirSync(dir).filter(f => /\.(png|jpg)$/.test(f)).sort();
const cols = +colsS, tw = +twS, th = Math.round(tw * 9 / 16);
const rows = Math.ceil(files.length / cols);
const comp = [];
for (let i = 0; i < files.length; i++) {
  const buf = await sharp(`${dir}/${files[i]}`).resize(tw, th).png().toBuffer();
  comp.push({ input: buf, left: (i % cols) * tw, top: Math.floor(i / cols) * th });
}
await sharp({ create: { width: cols * tw, height: rows * th, channels: 3, background: '#000' } }).composite(comp).png().toFile(outFile);
console.log(files.length, 'tiles');
