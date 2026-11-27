"use client";
import { MotionConfig, motion } from "framer-motion";

// 페이지 전환 시 부드러운 fade + slide. 기기에서 '동작 줄이기'를 켜면 움직임 없이 바로 보여 줌
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <MotionConfig reducedMotion="user">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}>
        {children}
      </motion.div>
    </MotionConfig>
  );
}
