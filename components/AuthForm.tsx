"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { supabase } from "@/lib/auth/supabase";

/** 이메일 회원가입 / 로그인 폼 (Supabase Auth) */
export default function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") || "/analyze";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [agree, setAgree] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const isSignup = mode === "signup";

  if (!supabase) {
    return (
      <div className="border border-ink p-6">
        <p className="text-lg font-bold">지금은 테스트 모드예요.</p>
        <p className="mt-2 leading-relaxed text-mute">
          회원가입 기능은 운영자가 Supabase를 연결하면 켜집니다. 지금은 로그인 없이 바로 이용할 수 있어요.
        </p>
        <Link href="/analyze" className="btn-primary mt-6 w-full">
          바로 시작하기 →
        </Link>
      </div>
    );
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSignup && !agree) return setMsg({ ok: false, text: "약관과 개인정보처리방침에 동의해 주세요." });
    setBusy(true);
    setMsg(null);
    if (isSignup) {
      const { data, error } = await supabase!.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: `${window.location.origin}/analyze` },
      });
      setBusy(false);
      if (error) return setMsg({ ok: false, text: translate(error.message) });
      if (data.session) return router.replace(next);
      setMsg({ ok: true, text: "가입 확인 메일을 보냈어요. 메일의 링크를 누르면 가입이 완료됩니다." });
    } else {
      const { error } = await supabase!.auth.signInWithPassword({ email, password });
      setBusy(false);
      if (error) return setMsg({ ok: false, text: translate(error.message) });
      router.replace(next);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-6">
      <div>
        <p className="label mb-3">이메일</p>
        <input className="field" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>
      <div>
        <p className="label mb-3">비밀번호 {isSignup && "(6자 이상)"}</p>
        <input
          className="field"
          type="password"
          required
          minLength={6}
          autoComplete={isSignup ? "new-password" : "current-password"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      {isSignup && (
        <label className="flex items-start gap-3 text-sm leading-relaxed">
          <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} className="mt-0.5 h-5 w-5 shrink-0 accent-ink" />
          <span>
            <Link href="/disclaimer" className="underline">면책조항</Link>과 <Link href="/privacy" className="underline">개인정보처리방침</Link>에
            동의합니다. (가입 시 이메일만 저장되며, 사진·생년월일은 저장되지 않습니다)
          </span>
        </label>
      )}
      {msg && (
        <p className={`border-l-4 px-4 py-3 text-sm font-medium ${msg.ok ? "border-ink bg-smoke" : "border-accent bg-accent/5 text-accent"}`}>{msg.text}</p>
      )}
      <button type="submit" disabled={busy} className="btn-primary h-16 w-full text-lg">
        {busy ? "잠시만요…" : isSignup ? "무료 회원가입" : "로그인"}
      </button>
      <p className="text-center text-sm text-mute">
        {isSignup ? "이미 계정이 있나요? " : "처음이신가요? "}
        <Link href={`${isSignup ? "/login" : "/signup"}?next=${encodeURIComponent(next)}`} className="font-bold text-ink underline">
          {isSignup ? "로그인" : "회원가입"}
        </Link>
      </p>
    </form>
  );
}

function translate(m: string) {
  if (/invalid login/i.test(m)) return "이메일 또는 비밀번호가 맞지 않아요.";
  if (/already registered/i.test(m)) return "이미 가입된 이메일이에요. 로그인해 주세요.";
  if (/email not confirmed/i.test(m)) return "메일 인증이 아직이에요. 받은편지함을 확인해 주세요.";
  if (/password/i.test(m)) return "비밀번호는 6자 이상이어야 해요.";
  return m;
}
