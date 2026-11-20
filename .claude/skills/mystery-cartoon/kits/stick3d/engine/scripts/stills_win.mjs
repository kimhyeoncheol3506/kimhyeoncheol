// usage: node stills.mjs <engineDir> <compId> <outDir> <scale> <frame,frame,...>
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs"; import path from "node:path";
const [eng, id, out, scale, list] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(eng, "src/index.ts"), webpackOverride: (c) => c });
const pw = null;
const gl = "angle";
const composition = await selectComposition({ serveUrl, id, browserExecutable: pw, chromiumOptions: { gl } });
for (const fr of list.split(",").map(Number)) {
  await renderStill({ serveUrl, composition, frame: fr, output: path.join(out, `f${String(fr).padStart(4, "0")}.png`), scale: Number(scale), browserExecutable: pw, chromiumOptions: { gl } });
  console.log("still", fr);
}
