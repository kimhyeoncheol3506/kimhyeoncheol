// Short-term loudness envelope of audio files (4 s buckets) as a compact text graph.
// usage: node tools/loudness.mjs <file.mp3> [...]
import { spawnSync } from 'node:child_process';
for (const f of process.argv.slice(2)) {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-v', 'verbose', '-i', f, '-af', 'ebur128=framelog=verbose', '-f', 'null', '-'], { encoding: 'utf8', maxBuffer: 1 << 28 });
  const buckets = new Map();
  for (const line of r.stderr.split('\n')) {
    const m = line.match(/t:\s*([\d.]+).*?S:\s*(-?[\d.]+)/);
    if (!m) continue;
    const b = Math.floor(+m[1] / (+process.env.BUCKET || 4));
    if (!buckets.has(b)) buckets.set(b, []);
    buckets.get(b).push(+m[2]);
  }
  const vals = [...buckets.entries()].sort((a, b) => a[0] - b[0]).map(([b, v]) => v.reduce((s, x) => s + x, 0) / v.length);
  const chars = ' .:-=+*#%@';
  const line = vals.map(v => chars[Math.max(0, Math.min(9, Math.round((v + 40) / 3)))]).join('');
  const I = r.stderr.match(/I:\s*(-?[\d.]+) LUFS/);
  console.log(f.split(/[\\/]/).pop().padEnd(26), (I ? I[1] : '?').padStart(6), 'LUFS |' + line + '|');
}
