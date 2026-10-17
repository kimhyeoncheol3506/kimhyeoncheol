// 날짜·금액 등 표시 형식 도우미

// "2026-10-17 09:30" 형태의 현재 시각 (서버/브라우저 시간대 차이로 화면이 깨지지 않도록 문자열로 저장)
export function nowStamp(): string {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

export function today(): string {
  return nowStamp().slice(0, 10);
}

export function won(n: number): string {
  return n.toLocaleString("ko-KR") + "원";
}

// 큰 금액을 짧게: 11,780,000 → "1,178만원"
export function wonShort(n: number): string {
  return n >= 10000 ? Math.round(n / 10000).toLocaleString("ko-KR") + "만원" : won(n);
}

export function newId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}
