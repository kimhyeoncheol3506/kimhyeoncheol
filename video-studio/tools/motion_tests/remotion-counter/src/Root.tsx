import React from "react";
import { AbsoluteFill, Composition, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const Counter: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const v = interpolate(f, [10, 90], [0, 4471.6], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: (t) => 1 - Math.pow(1 - t, 3) });
  const pop = spring({ frame: f - 5, fps, config: { damping: 12 } });
  const bar = interpolate(f, [20, 110], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "linear-gradient(160deg,#1b2330,#2a1f3a)", alignItems: "center", justifyContent: "center", fontFamily: "sans-serif" }}>
      <div style={{ color: "#9aa6b5", fontSize: 42, marginBottom: 20 }}>2025년 10월 광의통화 (한국은행)</div>
      <div style={{ color: "#F2C14E", fontSize: 150, fontWeight: 900, transform: `scale(${0.6 + 0.4 * pop})` }}>{v.toLocaleString("ko-KR", { maximumFractionDigits: 0 })}조 원</div>
      <div style={{ width: 1100, height: 22, borderRadius: 11, background: "#33405a", marginTop: 40 }}>
        <div style={{ width: `${bar * 100}%`, height: "100%", borderRadius: 11, background: "#DE5B41" }} />
      </div>
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => <Composition id="Counter" component={Counter} durationInFrames={150} fps={30} width={1920} height={1080} />;
