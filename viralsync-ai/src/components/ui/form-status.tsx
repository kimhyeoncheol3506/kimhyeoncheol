"use client";
import type { ActionState } from "@/lib/action-state";
import { Alert } from "./misc";

/** 폼 오류 표시. 성공 메시지는 useActionForm 이 토스트로 표시한다. */
export function FormMessage({ state }: { state: ActionState }) {
  if (!state.message || state.ok) return null;
  return <Alert tone="error">{state.message}</Alert>;
}
