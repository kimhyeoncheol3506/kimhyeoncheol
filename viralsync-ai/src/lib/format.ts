export function won(n: number | null | undefined): string {
  if (n == null) return "-";
  return `${n.toLocaleString("ko-KR")}원`;
}

export function num(n: number | null | undefined): string {
  if (n == null) return "미측정";
  return n.toLocaleString("ko-KR");
}

export function dateTime(d: Date | string | null | undefined): string {
  if (!d) return "-";
  const x = typeof d === "string" ? new Date(d) : d;
  return x.toLocaleString("ko-KR", { timeZone: "Asia/Seoul", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function dateOnly(d: Date | string | null | undefined): string {
  if (!d) return "-";
  const x = typeof d === "string" ? new Date(d) : d;
  return x.toLocaleDateString("ko-KR", { timeZone: "Asia/Seoul", year: "numeric", month: "2-digit", day: "2-digit" });
}

/** <input type="date"> 값 */
export function dateInput(d: Date | null | undefined): string {
  if (!d) return "";
  return d.toISOString().slice(0, 10);
}

export function splitList(v: string | null | undefined): string[] {
  if (!v) return [];
  return v
    .split(/[,\n]/)
    .map((s) => s.trim())
    .filter(Boolean);
}
