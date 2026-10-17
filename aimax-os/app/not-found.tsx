import Link from "next/link";

export default function NotFound() {
  return (
    <div className="card mx-auto mt-16 max-w-md text-center">
      <p className="text-4xl">🧭</p>
      <h1 className="mt-3 text-xl font-bold">페이지를 찾을 수 없어요</h1>
      <Link href="/" className="btn-primary mt-5">
        운영자 콘솔로
      </Link>
    </div>
  );
}
