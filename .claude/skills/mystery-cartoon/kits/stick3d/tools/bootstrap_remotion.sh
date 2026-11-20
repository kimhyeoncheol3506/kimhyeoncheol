#!/usr/bin/env bash
# usage: bash bootstrap_remotion.sh [dir=engine]  -> generic Remotion TypeScript project (NO style code). Pinned versions that work together.
set -e; D="${1:-engine}"; mkdir -p "$D/src" "$D/public"; cd "$D"
[ -f package.json ] || echo '{"name":"engine","private":true,"version":"1.0.0"}' > package.json
npm i --no-audit --no-fund remotion@4.0.250 @remotion/cli@4.0.250 @remotion/paths@4.0.250 @remotion/media-utils@4.0.250 @remotion/layout-utils@4.0.250 @remotion/three@4.0.250 react@18.3.1 react-dom@18.3.1 three@0.170.0 @react-three/fiber@8.17.10 @types/three@0.170.0 @types/react@18 lucide-react zod@3.22.3 @fontsource/inter@5
npm i --no-audit --no-fund -D typescript@5.5.4   # newer TypeScript breaks the Remotion bundler
cat > tsconfig.json <<'T'
{"compilerOptions":{"target":"ES2022","module":"ESNext","moduleResolution":"Bundler","jsx":"react-jsx","strict":true,"skipLibCheck":true,"resolveJsonModule":true,"allowJs":true,"noEmit":true,"esModuleInterop":true},"include":["src"]}
T
cat > remotion.config.ts <<'T'
import { Config } from "@remotion/cli/config";
import fs from "node:fs";
Config.setEntryPoint("./src/index.ts");
// auto-detect a pre-installed headless Chromium (cloud); otherwise Remotion downloads its own
const cands = (() => { try { return fs.readdirSync("/opt/pw-browsers").filter((d) => d.startsWith("chromium_headless_shell")).map((d) => { const b = `/opt/pw-browsers/${d}`; const sub = fs.readdirSync(b).find((x) => x.startsWith("chrome-headless-shell")); return sub ? `${b}/${sub}/chrome-headless-shell` : ""; }); } catch { return []; } })();
const found = cands.find((p) => p && fs.existsSync(p)); if (found) Config.setBrowserExecutable(found);
Config.setVideoImageFormat("jpeg"); Config.setJpegQuality(92);
T
cat > src/index.ts <<'T'
import { registerRoot } from "remotion";
import { Root } from "./Root";
registerRoot(Root);
T
cat > src/Root.tsx <<'T'
import React from "react";
import { Composition } from "remotion";
import { Hello } from "./Hello";
export const Root: React.FC = () => <Composition id="Hello" component={Hello} width={1920} height={1080} fps={30} durationInFrames={60} />;
T
cat > src/Hello.tsx <<'T'
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
export const Hello: React.FC = () => { const f = useCurrentFrame(); return <AbsoluteFill style={{ background: "#111", color: "#fff", fontFamily: "sans-serif", fontSize: 120, alignItems: "center", justifyContent: "center", opacity: interpolate(f, [0, 15], [0, 1], { extrapolateRight: "clamp" }) }}>Engine OK</AbsoluteFill>; };
T
npx tsc -p . && echo "BOOTSTRAP OK in $(pwd)"
