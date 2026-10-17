import type { Tone } from "@/lib/labels";

const tones: Record<Tone, string> = {
  green: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  blue: "bg-sky-50 text-sky-700 ring-sky-200",
  amber: "bg-amber-50 text-amber-700 ring-amber-200",
  red: "bg-rose-50 text-rose-700 ring-rose-200",
  gray: "bg-gray-100 text-gray-600 ring-gray-200",
};

// 상태 표시용 작은 배지. 예) <Badge label={staffStatus[s.status]} />
export function Badge({ label }: { label: { text: string; tone: Tone } }) {
  return (
    <span className={`inline-flex shrink-0 items-center whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${tones[label.tone]}`}>
      {label.text}
    </span>
  );
}
