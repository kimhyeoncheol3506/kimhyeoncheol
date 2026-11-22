import { Config } from "@remotion/cli/config";
import fs from "node:fs";
Config.setEntryPoint("./src/index.ts");
// auto-detect a pre-installed headless Chromium (cloud); otherwise Remotion downloads its own
const cands = (() => { try { return fs.readdirSync("/opt/pw-browsers").filter((d) => d.startsWith("chromium_headless_shell")).map((d) => { const b = `/opt/pw-browsers/${d}`; const sub = fs.readdirSync(b).find((x) => x.startsWith("chrome-headless-shell")); return sub ? `${b}/${sub}/chrome-headless-shell` : ""; }); } catch { return []; } })();
const found = cands.find((p) => p && fs.existsSync(p)); if (found) Config.setBrowserExecutable(found);
Config.setVideoImageFormat("jpeg"); Config.setJpegQuality(92);
