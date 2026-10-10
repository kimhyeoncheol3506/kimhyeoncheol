"use client";
import { useMemo } from "react";
import { motion } from "framer-motion";
import { MESH_EDGES, MESH_H, MESH_POINTS, MESH_W } from "@/lib/face/meshData";

// 관상에서 보는 핵심 지점 (눈·코·입·턱·이마) — 포인트 컬러로 표시
const KEY_POINTS = [10, 151, 33, 133, 362, 263, 1, 61, 291, 152, 234, 454];

/** 얼굴 메시를 선으로 그린 추상 히어로 그래픽 (외부 이미지 없이 SVG로 렌더) */
export default function HeroArt({ className = "" }: { className?: string }) {
  const path = useMemo(
    () =>
      MESH_EDGES.map(([a, b]) => {
        const p = MESH_POINTS[a];
        const q = MESH_POINTS[b];
        return `M${p[0]} ${p[1]}L${q[0]} ${q[1]}`;
      }).join(""),
    [],
  );
  const pad = 60;

  return (
    <div className={`relative ${className}`} aria-hidden>
      <svg
        viewBox={`${-pad} ${-pad} ${MESH_W + pad * 2} ${MESH_H + pad * 2}`}
        className="h-full w-full"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#fff" stopOpacity="0.55" />
            <stop offset="0.7" stopColor="#fff" stopOpacity="0.22" />
            <stop offset="1" stopColor="#fff" stopOpacity="0.05" />
          </linearGradient>
          <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#E11D48" stopOpacity="0" />
            <stop offset="0.5" stopColor="#E11D48" stopOpacity="0.9" />
            <stop offset="1" stopColor="#E11D48" stopOpacity="0" />
          </linearGradient>
        </defs>

        <motion.path
          d={path}
          fill="none"
          stroke="url(#fade)"
          strokeWidth={1.1}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 2.2, ease: "easeOut" }}
        />

        {MESH_POINTS.map(([x, y, z], i) =>
          i % 3 === 0 ? <circle key={i} cx={x} cy={y} r={1.6} fill="#fff" opacity={0.15 + Math.max(0, z) / 120} /> : null,
        )}

        {/* 스캔 라인 */}
        <motion.rect
          x={-pad}
          width={MESH_W + pad * 2}
          height={140}
          fill="url(#scan)"
          opacity={0.35}
          initial={{ y: -200 }}
          animate={{ y: [-200, MESH_H + 60] }}
          transition={{ duration: 4.5, repeat: Infinity, repeatDelay: 1.2, ease: "easeInOut" }}
          style={{ mixBlendMode: "screen" }}
        />

        {KEY_POINTS.map((i, n) => {
          const [x, y] = MESH_POINTS[i];
          return (
            <motion.g key={i} initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1 + n * 0.08, duration: 0.5 }} style={{ transformOrigin: `${x}px ${y}px` }}>
              <circle cx={x} cy={y} r={14} fill="none" stroke="#E11D48" strokeWidth={1.5} opacity={0.6} />
              <circle cx={x} cy={y} r={4.5} fill="#E11D48" />
            </motion.g>
          );
        })}
      </svg>
    </div>
  );
}
