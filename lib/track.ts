// GA4 이벤트 (NEXT_PUBLIC_GA_ID 가 있을 때만 실제로 보냄). 개인정보(이름·생일·사진)는 절대 넣지 않는다.
declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
  }
}

export type TrackEvent = "start" | "input_complete" | "result_view" | "share" | "pdf_download";

export function track(event: TrackEvent, params: { flow: "saju" | "match" | "newyear"; method?: string; [k: string]: string | number | boolean | undefined }) {
  try {
    window.gtag?.("event", event, params);
  } catch {
    /* 측정 실패는 무시 */
  }
}
