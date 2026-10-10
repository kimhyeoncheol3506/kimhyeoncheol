import { Suspense } from "react";
import AuthForm from "@/components/AuthForm";

export const metadata = { title: "로그인" };

export default function Page() {
  return (
    <div className="mx-auto grid max-w-page gap-14 px-5 pb-28 pt-14 md:grid-cols-2 md:px-10 md:pt-24">
      <h1 className="text-headline font-black">다시 오셨네요.</h1>
      <div className="w-full max-w-md">
        <Suspense>
          <AuthForm mode="login" />
        </Suspense>
      </div>
    </div>
  );
}
