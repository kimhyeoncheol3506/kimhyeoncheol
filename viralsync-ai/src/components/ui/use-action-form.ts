"use client";
import { useRef, useState, useTransition, type FormEvent } from "react";
import { initialState, type ActionState } from "@/lib/action-state";
import { useToast } from "./toast";

/**
 * 서버 액션 폼 훅.
 * - React 19 의 `<form action>` 자동 초기화를 피하기 위해 onSubmit 에서 서버 액션을 직접 호출한다
 *   (검증 오류 시 사용자가 입력한 값이 유지됨).
 * - useActionState 는 라우터 이동 트랜지션과 겹칠 때 결과가 누락되는 경우가 있어 일반 state 로 관리한다.
 * - 성공 메시지는 토스트로 표시한다 (재검증으로 폼이 사라져도 유지). 오류는 폼 안에 표시한다.
 * - 이동이 필요한 액션은 서버에서 redirect() 한다. 클라이언트에서 router.push 하면 액션 응답의
 *   재검증 갱신이 이동 요청을 중단(abort)시키는 경우가 있다. redirect 시 반환값은 없다.
 */
export function useActionForm(action: (prev: ActionState, fd: FormData) => Promise<ActionState>, opts: { resetOnSuccess?: boolean } = {}) {
  const [state, setState] = useState<ActionState>(initialState);
  const [pending, startTransition] = useTransition();
  const formRef = useRef<HTMLFormElement>(null);
  const toast = useToast();

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const submitter = (e.nativeEvent as SubmitEvent).submitter as HTMLElement | null;
    const fd = new FormData(form, submitter);
    startTransition(async () => {
      let result: ActionState | undefined;
      try {
        result = await action(state, fd);
      } catch (err) {
        console.error("[useActionForm]", err);
        result = { ok: false, message: "요청을 처리하지 못했습니다. 네트워크 상태를 확인하고 다시 시도하세요." };
      }
      if (!result) return; // redirect 된 경우
      setState(result);
      if (result.ok && result.message) toast({ tone: "success", message: result.message });
      if (opts.resetOnSuccess && result.ok) form.reset();
    });
  };

  return { state, pending, onSubmit, formRef };
}
