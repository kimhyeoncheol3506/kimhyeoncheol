"use client";
// 앱 전체 데이터 저장소.
// 지금은 브라우저(localStorage)에 저장합니다 → 서버 없이 바로 실행 가능.
// 나중에 Supabase 같은 DB로 옮길 때는 이 파일만 바꾸면 화면 코드는 그대로 둘 수 있습니다.
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { seed } from "./seed";
import { newId, nowStamp } from "./format";
import type { Collections, ErrorReport } from "./types";

const STORAGE_KEY = "aimax-os:v1";

type Key = keyof Collections;
type Item<K extends Key> = Collections[K][number];

interface Store {
  data: Collections;
  add: <K extends Key>(key: K, item: Item<K>) => void;
  update: <K extends Key>(key: K, id: string, patch: Partial<Item<K>>) => void;
  remove: (key: Key, id: string) => void;
  logError: (e: Partial<ErrorReport> & { title: string; message: string }) => void;
  resetAll: () => void;
}

const StoreContext = createContext<Store | null>(null);

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<Collections>(seed);
  const loaded = useRef(false);

  // 처음 한 번: 브라우저에 저장된 데이터 불러오기
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) setData({ ...seed, ...JSON.parse(saved) });
    } catch {
      // 저장 데이터가 깨졌으면 예시 데이터로 시작
    }
    loaded.current = true;
  }, []);

  // 데이터가 바뀔 때마다 저장
  useEffect(() => {
    if (!loaded.current) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      // 저장 공간이 없거나 비공개 창이면 저장만 건너뜀
    }
  }, [data]);

  const add = useCallback(<K extends Key>(key: K, item: Item<K>) => {
    setData((d) => ({ ...d, [key]: [item, ...d[key]] }));
  }, []);

  const update = useCallback(<K extends Key>(key: K, id: string, patch: Partial<Item<K>>) => {
    setData((d) => ({
      ...d,
      [key]: (d[key] as Item<K>[]).map((it) => (it.id === id ? { ...it, ...patch } : it)),
    }));
  }, []);

  const remove = useCallback((key: Key, id: string) => {
    setData((d) => ({ ...d, [key]: (d[key] as { id: string }[]).filter((it) => it.id !== id) }));
  }, []);

  const logError = useCallback<Store["logError"]>((e) => {
    setData((d) => {
      // 같은 오류가 1분 안에 반복되면 한 번만 기록
      const stamp = nowStamp();
      if (d.errors.some((x) => x.message === e.message && x.createdAt === stamp)) return d;
      const report: ErrorReport = {
        id: newId("e"),
        source: "auto",
        page: typeof window !== "undefined" ? window.location.pathname : "",
        severity: "medium",
        status: "open",
        createdAt: stamp,
        feedback: "",
        ...e,
      };
      return { ...d, errors: [report, ...d.errors] };
    });
  }, []);

  const resetAll = useCallback(() => setData(seed), []);

  return (
    <StoreContext.Provider value={{ data, add, update, remove, logError, resetAll }}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStore(): Store {
  const s = useContext(StoreContext);
  if (!s) throw new Error("useStore는 StoreProvider 안에서만 쓸 수 있습니다.");
  return s;
}
