// lunar-javascript 는 타입 정의가 없어 필요한 부분만 선언합니다.
declare module "lunar-javascript" {
  /* eslint-disable @typescript-eslint/no-explicit-any */
  export const Solar: {
    fromYmdHms(y: number, m: number, d: number, h: number, mi: number, s: number): any;
    fromYmd(y: number, m: number, d: number): any;
  };
  export const Lunar: {
    fromYmdHms(y: number, m: number, d: number, h: number, mi: number, s: number): any;
  };
}
