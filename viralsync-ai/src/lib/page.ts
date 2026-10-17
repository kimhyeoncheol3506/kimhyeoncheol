import "server-only";
import { notFound } from "next/navigation";
import { NotFoundError } from "@/lib/auth/context";

/** 서비스 NotFoundError → Next notFound() */
export async function orNotFound<T>(p: Promise<T>): Promise<T> {
  try {
    return await p;
  } catch (e) {
    if (e instanceof NotFoundError) notFound();
    throw e;
  }
}

export type SP = Record<string, string | string[] | undefined>;

export function str(sp: SP, key: string): string | undefined {
  const v = sp[key];
  return typeof v === "string" && v.trim() ? v.trim() : undefined;
}

export function pageNum(sp: SP): number {
  const n = Number(str(sp, "page") ?? 1);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 1;
}
