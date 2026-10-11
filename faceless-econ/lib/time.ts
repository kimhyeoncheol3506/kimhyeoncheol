// 시간 유틸: 저장은 UTC ISO, 표시는 한국 표준시(KST, UTC+9)

const KST_FMT = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export function kst(iso: string | number | null | undefined): string {
  if (iso == null) return "확인 불가";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "확인 불가";
  return `${KST_FMT.format(d)} KST`;
}

export function kstDate(iso: string | number): string {
  return new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", year: "numeric", month: "2-digit", day: "2-digit" }).format(
    new Date(iso),
  );
}

/** ISO 8601 기간(PT1H2M3S, P1DT2H) → 초 */
export function parseIsoDuration(d: string | null | undefined): number | null {
  if (!d) return null;
  const m = d.match(/^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$/);
  if (!m) return null;
  const [, day, h, mi, s] = m;
  return (Number(day ?? 0) * 86400) + (Number(h ?? 0) * 3600) + (Number(mi ?? 0) * 60) + Number(s ?? 0);
}

export function fmtDuration(sec: number | null): string {
  if (sec == null) return "수집 불가";
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  return h > 0 ? `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}` : `${m}:${String(s).padStart(2, "0")}`;
}

export function fmtAge(hours: number | null): string {
  if (hours == null) return "확인 불가";
  if (hours < 48) return `${hours.toFixed(1)}시간`;
  return `${(hours / 24).toFixed(1)}일`;
}
