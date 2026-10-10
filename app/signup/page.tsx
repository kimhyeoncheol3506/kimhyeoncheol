import { Suspense } from "react";
import AuthForm from "@/components/AuthForm";

export const metadata = { title: "회원가입" };

export default function Page() {
  return (
    <div className="mx-auto grid max-w-page gap-14 px-5 pb-28 pt-14 md:grid-cols-2 md:px-10 md:pt-24">
      <h1 className="text-headline font-black">무료로 가입하고<br />운명을 확인하세요.</h1>
      <div className="w-full max-w-md">
        <Suspense>
          <AuthForm mode="signup" />
        </Suspense>
      </div>
    </div>
  );
}
