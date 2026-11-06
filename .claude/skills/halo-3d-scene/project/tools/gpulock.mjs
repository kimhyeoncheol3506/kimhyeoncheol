// Machine-wide GPU lock: only one headless renderer (Chrome / WebGL) at a time, across the main project and every
// sandbox. Several WebGL renderers competing for the Radeon 780M crashed Windows twice on 2026-11-01 (bugcheck 0x119
// VIDEO_SCHEDULER_INTERNAL_ERROR). acquireGpu() blocks until the lock file is free (locks of dead processes are taken
// over) and returns release(), which also runs on process exit.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const LOCK = process.env.GPU_LOCK || path.join(os.tmpdir(), 'gpu_render.lock');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const alive = pid => { try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; } };
const read = () => { try { return JSON.parse(fs.readFileSync(LOCK, 'utf8')); } catch { return null; } };

// rest after a render of `ms` milliseconds (env GPU_REST x its time, default 0.5): the iGPU is shared with other
// work on this laptop, so long renders leave it idle gaps instead of running at 100% for minutes
export const gpuRest = ms => sleep(Math.min(20000, Math.max(200, ms * (process.env.GPU_REST ? +process.env.GPU_REST : 0.5))));

export async function acquireGpu(label = '') {
  const t0 = Date.now();
  let said = 0;
  for (;;) {
    try {
      fs.writeFileSync(LOCK, JSON.stringify({ pid: process.pid, label, cwd: process.cwd(), t: new Date().toISOString() }), { flag: 'wx' });
      break;
    } catch (e) {
      if (e.code !== 'EEXIST') throw e;
    }
    const o = read();
    if (o && !alive(o.pid)) {
      // stale: re-check it is still the same dead holder before removing it
      const o2 = read();
      if (o2 && o2.pid === o.pid && o2.t === o.t) { try { fs.unlinkSync(LOCK); } catch { /* someone else took it */ } }
      continue;
    }
    const w = Math.round((Date.now() - t0) / 1000);
    if (w >= said) {
      console.log(`[gpu] waiting ${w} s for the GPU lock (held by pid ${o?.pid} ${o?.label || ''} in ${o?.cwd || '?'} since ${o?.t || '?'})`);
      said = said ? said * 2 : 30;
    }
    await sleep(1500);
  }
  if (Date.now() - t0 > 3000) console.log(`[gpu] lock acquired after ${Math.round((Date.now() - t0) / 1000)} s`);
  let held = true;
  const release = () => {
    if (!held) return;
    held = false;
    const o = read();
    if (o && o.pid === process.pid) { try { fs.unlinkSync(LOCK); } catch { /* gone */ } }
  };
  process.on('exit', release);
  for (const s of ['SIGINT', 'SIGTERM', 'SIGBREAK', 'SIGHUP']) process.on(s, () => { release(); process.exit(130); });
  return release;
}
