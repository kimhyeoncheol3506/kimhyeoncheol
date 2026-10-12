// 데스크톱 앱(FinClose.exe 등)에서 실행될 때만 켜지는 기능.
import { useEffect, useState } from "react";
import { api } from "./api";

export type DesktopInfo = { mode: "work" | "practice"; home: string; data_dir: string; practice_files: string; log_file: string; fallback: boolean } | null;

let cached: DesktopInfo | undefined;
const listeners = new Set<(d: DesktopInfo) => void>();

export function useDesktop(): DesktopInfo {
  const [d, setD] = useState<DesktopInfo>(cached ?? null);
  useEffect(() => {
    listeners.add(setD);
    if (cached === undefined) {
      api.get("/api/health").then((h) => { cached = h.desktop ?? null; listeners.forEach((f) => f(cached!)); }).catch(() => undefined);
    }
    return () => { listeners.delete(setD); };
  }, []);
  return d;
}

export function startHeartbeat() {
  const beat = () => api.post("/api/desktop/heartbeat", {}).catch(() => undefined);
  beat();
  return window.setInterval(beat, 20000);
}

export const openFolder = (which: "practice" | "data" | "home") => api.post("/api/desktop/open-folder", { which });
export const quitApp = () => api.post("/api/desktop/shutdown", {});
