// Download the baked scene data (terrain levels, lights, cloud noise volumes, sky dome, textures; ~0.3 GB) from the
// GitHub release and unpack it into data/.  usage: npm run data   (needs tar, which ships with Windows 10+, macOS
// and Linux)
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';

const SRC = 'https://github.com/Leonxlnx/halo-above-the-clouds/releases/download/v1.0/halo-data.tar.gz';
const tmp = 'halo-data.tar.gz';

console.log('downloading', SRC);
const res = await fetch(SRC);
if (!res.ok) throw new Error(`download failed: HTTP ${res.status}`);
const total = +res.headers.get('content-length') || 0;
let got = 0, shown = 0;
const body = Readable.fromWeb(res.body);
body.on('data', c => {
  got += c.length;
  if (total && got / total - shown >= 0.1) { shown = Math.floor(got / total * 10) / 10; console.log(`  ${Math.round(shown * 100)}%`); }
});
await pipeline(body, fs.createWriteStream(tmp));

const r = spawnSync('tar', ['-xzf', tmp], { stdio: 'inherit' });
fs.unlinkSync(tmp);
if (r.status !== 0) throw new Error('tar failed');
console.log('data/ is ready');
