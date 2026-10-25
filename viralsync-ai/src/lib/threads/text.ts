/** Threads 글자 수: 일반 문자는 1자, 이모지는 UTF-8 바이트 수만큼 센다 (공식 문서 기준). 최대 500 */
export const THREADS_TEXT_LIMIT = 500;

const EMOJI = /\p{Extended_Pictographic}/u;

export function threadsLength(text: string): number {
  let n = 0;
  for (const ch of text) n += EMOJI.test(ch) ? new TextEncoder().encode(ch).length : 1;
  return n;
}

const AD_MARK = /(#광고|#협찬|#유료광고|광고\)|\[광고\]|유료 광고|협찬)/;

/** 광고·협찬 게시물이면 광고 표시가 없을 때 #광고 를 붙인다 */
export function withAdDisclosure(caption: string, isAd: boolean): string {
  const c = caption.trim();
  if (!isAd || AD_MARK.test(c)) return c;
  return c ? `${c}\n\n#광고` : "#광고";
}
