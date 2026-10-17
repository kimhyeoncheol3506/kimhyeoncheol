"use client";
import { useActionForm } from "@/components/ui/use-action-form";
import { login } from "@/app/actions/auth";
import { SubmitButton } from "@/components/ui/submit-button";
import { FormMessage } from "@/components/ui/form-status";

export function LoginForm() {
  const { state, pending, onSubmit, formRef } = useActionForm(login);
  return (
    <form ref={formRef} method="post" onSubmit={onSubmit} className="space-y-4" noValidate>
      <FormMessage state={state} />
      <div>
        <label htmlFor="email" className="label">이메일</label>
        <input id="email" name="email" type="email" autoComplete="username" required className="input" placeholder="you@company.com" />
      </div>
      <div>
        <label htmlFor="password" className="label">비밀번호</label>
        <input id="password" name="password" type="password" autoComplete="current-password" required className="input" />
      </div>
      <SubmitButton pending={pending} className="w-full" pendingText="로그인 중…">로그인</SubmitButton>
    </form>
  );
}
