// 조선 사당 분위기의 운명첩(命相帖) PDF 템플릿.
// 서버(/api/pdf)와 브라우저(인쇄 대체 경로)에서 같은 HTML을 씁니다.
/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ResultPayload } from "../reading/types";

const HANJA_NUM: string[] = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三", "十四"];
const SECTION_HANJA: Record<string, string> = {
  personality: "性情", elements: "五行", career: "財祿", love: "因緣", health: "康寧",
  life: "大運", future: "歲運", months: "月運", luck: "吉祥", caution: "謹愼",
};
const PILLAR_HANJA: Record<string, string> = { hour: "時柱", day: "日柱", month: "月柱", year: "年柱" };
const EL_HANJA: Record<string, string> = { 목: "木", 화: "火", 토: "土", 금: "金", 수: "水" };
const STEMS = "甲乙丙丁戊己庚辛壬癸";
const BRANCHES = "子丑寅卯辰巳午未申酉戌亥";
const MONTH_HANJA = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"];

const esc = (s: unknown) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const yearGanzhi = (y: number) => STEMS[(((y - 4) % 10) + 10) % 10] + BRANCHES[(((y - 4) % 12) + 12) % 12];

// 구름 문양 (모서리 장식)
const cloud = (cls: string) => `<svg class="cloud ${cls}" viewBox="0 0 120 120"><g fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
<path d="M8 112 C8 70 30 50 58 50 C58 34 72 24 86 30 C96 18 116 24 112 42"/>
<path d="M30 112 C30 84 46 70 66 72 C70 60 82 56 92 62"/>
<path d="M86 30 C80 40 86 50 96 48"/><path d="M58 50 C56 60 64 66 72 62"/>
<circle cx="102" cy="40" r="5"/></g></svg>`;

// 낙관(붉은 도장)
const seal = (text: string, size = 26) => `<div class="seal" style="width:${size}mm;height:${size}mm"><span>${text}</span></div>`;

// 위패 모양 사주 기둥
const tablet = (p: any) => {
  if (p.unknown) {
    return `<div class="tablet"><div class="tab-head">${PILLAR_HANJA[p.key]}</div><div class="tab-body unknown"><span>未</span><span>詳</span></div><div class="tab-foot">시간 모름</div></div>`;
  }
  return `<div class="tablet ${p.key === "day" ? "me" : ""}"><div class="tab-head">${PILLAR_HANJA[p.key]}</div>
  <div class="tab-body"><span>${p.stem}</span><span>${p.branch}</span></div>
  <div class="tab-foot">${p.stemKo}${p.branchKo}${p.key === "day" ? " · 나" : ""}</div></div>`;
};

// 기본 글꼴: Google Fonts (서버·브라우저 모두에서 불러옴)
export const GOOGLE_FONTS =
  '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' +
  '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Brush+Script&family=Nanum+Myeongjo:wght@400;700;800&family=Noto+Serif+KR:wght@700;900&family=Song+Myung&display=block">';

export function renderReport(r: ResultPayload, opts: { name?: string; fontHead?: string; autoPrint?: boolean } = {}) {
  const { saju, reading, face, common } = r;
  const now = new Date(r.createdAt || Date.now());
  const issued = `${yearGanzhi(now.getFullYear())}年 ${MONTH_HANJA[now.getMonth()]}月 吉日`;
  const name = opts.name || r.name || "귀하";

  // 본문을 "블록" 단위로 평평하게 만든 뒤, 브라우저에서 쪽마다 채워 넣는다
  const blocks: string[] = [];
  const head = (i: number, title: string, sub: string) =>
    `<header class="ch blk"><div class="num">${HANJA_NUM[i]}</div><div><h2>${esc(title)}</h2><div class="sub">${sub}</div></div></header>`;
  reading.sections.forEach((s, i) => {
    if (i > 0) blocks.push(`<div class="chapter-gap"></div>`);
    blocks.push(head(i, s.title, SECTION_HANJA[s.id] ?? ""));
    if (["life", "months", "luck"].includes(s.id)) {
      const lines = s.id === "luck" ? s.body : s.body.slice(1);
      if (s.id !== "luck") blocks.push(`<p class="para lead blk">${esc(s.body[0])}</p>`);
      lines.forEach((line, j) => {
        const [k, ...rest] = line.split(/ — |: /);
        blocks.push(`<div class="row blk ${j === 0 ? "first" : ""}"><div class="th">${esc(k)}</div><div class="td">${esc(rest.join(" — "))}</div></div>`);
      });
    } else {
      s.body.forEach((t) => blocks.push(`<p class="para blk">${esc(t)}</p>`));
    }
  });
  if (face) {
    blocks.push(`<div class="chapter-gap"></div>`);
    blocks.push(head(reading.sections.length, "관상 부위별 풀이", "觀相"));
    const f = face.features;
    const item = (x: { part: string; observation: string; meaning: string }) => `<div class="fitem"><div class="fpart">${esc(x.part)}</div><div class="fobs">${esc(x.observation)}</div><p>${esc(x.meaning)}</p></div>`;
    for (let i = 0; i < f.length; i += 2) blocks.push(`<div class="fpair blk">${item(f[i])}${f[i + 1] ? item(f[i + 1]) : ""}</div>`);
  }
  blocks.push(`<div class="scroll blk"><h3>당부의 말씀</h3><ul>${reading.advice.map((a: string) => `<li>${esc(a)}</li>`).join("")}</ul></div>`);
  blocks.push(`<div class="closing blk">${seal("謹書", 18)}<p>본 운명첩은 오락 및 참고용이며, 의학적·법적·재정적 조언이 아닙니다.<br>중요한 결정은 전문가와 상담하세요.${reading.source === "ai" ? " 풀이는 AI가 작성했습니다." : ""}</p></div>`);

  return `<!doctype html><html lang="ko"><head><meta charset="utf-8">${opts.fontHead ?? GOOGLE_FONTS}<title>命相帖</title>
<style>
@page { size: A4; margin: 0; }
:root { --paper:#EDE2C9; --ink:#2A2017; --wood:#3A2316; --red:#9E2A21; --green:#2F5B4E; --blue:#24406A; --ochre:#B08A3E; --soft:#6B5A44; }
* { box-sizing: border-box; }
html, body { margin:0; padding:0; }
body { font-family: "Nanum Myeongjo", "Noto Serif KR", serif; color: var(--ink); font-size: 12.6pt; line-height: 1.85; word-break: keep-all; -webkit-print-color-adjust: exact; print-color-adjust: exact; }

/* 쪽 단위 레이아웃: 한지 + 나무 틀 + 단청 띠 */
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; break-after: page; background: var(--paper) url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAACgCAYAAACLz2ctAAAiaElEQVR42sV9uXYku66s7Jzn0buf8Cx9xXPlX1f/718nay8KwhAAWWqtddbZ3a3KYpJAIBAEwY+PwM/312cV+MxE/nwl/70n/92Q31u/vz4P5nld8t/zx8fHx//+///3P6//cd8pjGt0vMNNx+acgyM43+f31+cg/NtmPT+d03SunWPope9A3ouujTiJ1oLQiUgNifnd9fvrs04msXo9/zURmnF9f33e31+fJzeZlnH9elFh0lJDZhZ0e431++tzjC4eYpjP/KzBz1+MUw50Tem7lgCa76/PxWvYP4zxhR7AFw3WBCR/bl1ewKCaF0UocgLP8f7+gLwjggovNDE+vyJzL6Ei+B3aGGfijDca5SIR8q0/31+fVzK4ATFG8vna+Pf55enoyxOEmAQEviwnoQjtNRQr7L0QJhoy6Tx+f302HFolc3imDvags2aop/QsaTxPZGt+/fITaiptkQkvaREDsTiTZIx0op7vPBAUdizUgiCwsQibMe4+QZX+++tzshDK4UgjGqkcc1JrkeKhVi3zd7sUHbhxfX99Ti/UWDU+EXiBTloAg2i3qDEmL30/nl09z9gSL66YiYoiSmtwoM6DEppBpYgsGMD9GPMsGOGRu4bMd+4cGHkiWSi8RbM8gzNuzwTSBKN9ef731+eZvhxBqptDAc24pMUgoaFFEZwiIpOBn4jBP+98IWvCONNphb7AGt4aPfj++uxQo0toV6spImG+8iDMQQZeJdxhN0LThqIDfWHikZMh0+yIgVmTRJGGOEiNhD/PGDQUIlzVm1AtIJXoODCwxsg4xvHkAb34PkQr6gDZoDfCyPJR8EeTKDK0rRnkQRehEj2gyZ2B8fRS+GYW9ST0ZX0WH1ESGgH1KgPV++A8d+Y/PoO/Pt78AxD2+THgTiPnOdln1OhfY8sxqKgspHDQzfouIvq3FOFTw1M4eJcLGIwjb5S0Tl4DcoqtW+BzLUXTJ3S3udnfk42uABq+xO+OhPbNE1o974/obsB8H57no4lE+llGH/1PC2QQtCHz10khZ8l58Qj3STx5DqDHTZ4xWmHbE44N4n8n6HhbemgO3fDyR+/Wn5HJ3zn2kJ0ta5ORbLfNzmfMyGIkSUTv5YdKOO1QfuTJ2qR3khZQ4q8EKTzJE6of1l6pKHHsJuoAv5CRs0ynbjWg3pTDMRnppaMv+BjLZkgCp0PUPRy/uxjSE2oYZlh/xOzDk+ESh75QY7MA6PXOHm4Mp+npQ42FOxmiSQ3mMiD+srhSWtwAoEYTEWJBVI5w2dHaojKcd3d+3xlce9OQBNDqiWHu0LyC0Fs5X2LzalM5GRcabhjCXGnoTDfk6URaoflBqqhEVAFy2Bzlik9yN1k8MTU2icM9zn6jThwtS0M1pb7gs1tGD1tLZeYAD0MTk+1dE4yQdy1BsMCD25GSvpsI72N0viwD2jMWstc4Sa6hODK2xhtWopnfgyKnZ34SWedgkqOJLPQQyaoJLaoTajRbzoZkq2SMh4CKR8gIpQySGNPyiNfDu0KpZDgvJ0EXKoJiAa3y5gz2++tzIKH+8CBdYjiHkZmO9HeZbdLT4v7cWpeSWIjUd9AEYQIne0bkD2vzn4YGT4bMfa/BUS7u+QKZXqJOZCRqh4EirZK8NOh3JUnAEokADE8+Gc2zkaIFIz7vSVJbqQ4vIeHjGXfiYQvZyrm8ckBAdlkQxPr++rw1ZIwKooC8ASVqIKcrRlVyKYb07pJTpzbEGONieidTy7f/wUQMpBhi1NA3PeOQ6FCbtuDG91+BMe8WN6TvAoyjinzXH6xPkyHrnJF/Qwe1FBUgfz//+scT32tyiwfliZPfjs+1Gs1hBPEalYlyHDDRZRdm3XbOGcPynqVJeWQHY0JPAR2HoPjr2U9ec5OnhH8hhQ2aJjkAOuuOhNNkG/Msra8yjlpTeqaMvxaRnSxG/4YBQx5iaFfTm9GvsRIrNPNWEoaaSCVNSYNAgEWjD4omaxnY7RlsDXo1evBocZ54O7kwoEzOKcggS6LL7QJ3rKPzkmvwJGk7vOEvQbIVlM48me9ozQNB6OUlw3mzatZJcs9xfn99DogmRzx+9sgsTAbWGVl4m8Ft2ghpRkPcw522xJjGwBhHUA4bLOrjQVbGuf8dT1fE0waULvrcxURDIudkCar8KpIEi3PT/c+Jqc65IojEoWd60k1x8Jt+Nzl09UNk9oR8LwcnVT2j4BQnJftagrBwVa4Ix3i8/TLI8vhXjsOFYqECZQJrDXcl3PbGvLaejDr35NvDNQ8iMA/W8xMRereSUHoIDFYLyECuEp7xhMvW8/3JC0yKwfRAtciSI58we8pzNJQxaDkzjno7n3lFQmHCibccECD20inJ2sx89yqG0meCKtTohKzpev63JOFjlryHgenu0ZQqid8RpNmV8BXhWJsX+ZAEjVCUEzzFNiVRyiN5ecvoimThVlb8AwAkDvcs8BwNlyRr6ryDDKf1BSSiovVqtpSzRHVOx3eepQwQ0CghaQqicUQuOIkXL4KX7pGE4lVO/xi+5zDRmYTulSHAnCyzZDhWH0VFI1s9GaTsE+68aiH4XUYpUIgWUTq0pJXrE5jG8NEIwZWiF02I3pbs53p2KyJ7tguQjY/cojANmTaFP3WoQTMhafJQAaE4YIvOU6Yh19pYrWrqDyVV3lB4VmrVZmYRD+mFmfBkKe6Voo1ZlcATggzKux0ANz4iKBrlcsZ5maJZtlARPdKCWrjqiHC21TnoS9MFMzXFSTJoIBz2SXhvn8SmNQyws0LnE/azDv2Q+U7HuQqo1no6lqYyiGX8QhJ5emkUSWTjwjfDmVrpBci/DZZBISTXUWE7ejxe6TqlFtYSJxgi49EQkSKII/KMURkl0fWGhKrsDtCpndJXFUFkF4E1DGLzho2oIT8TaYXvJiH7t0DyKyssWYflyU7ExVUHK8h9ODTKDZyXC3WKZKxoFr0lO0kbOi4EytPm4puEgF7iS8LNjGRO9ERWWqn9BvniABZp9xindBSylAyjSGfdOzQ/xh5WNNsWbUcQjBcHEl5WlgXwt87BEw9uXGkb4RKGGNH53inoOqWTFfzMKTkYAQHvWE5o8kosmJCiN4/3D/R3IqTeOITUIUIp02HrIvKNRyJCa/AuJUHwboWNjgqcyzq+gCROUpP5LAQ3zpd6N8svBK6RDXDmMwe32NbhF6FBdm8lFR5EA0q1bisZYMZdJQs/U0UgSvYFvttoTeA1B8nqfEX41EwnM3Ig5tH6OiSz9OiNKDKiom/mFQsNwAFbI8nYkO8AErwdMUrizDXyDjly2qvu0TuxlUeQzUCMhmsgJHhs45BaKoFznqBc0AnZ3R5NGtJTZWlpmkJXOg6tqCRkyVlghLEE+9ohtfTpXAvnrn/20gYLL7Xu8+vD7YqTb/AshabhrSCCjKDuViGhVTJiixZEDARMAudUIkHBg8zLFci8NykyRT15CFYqn1wIsOSEd2aUCs/svYtPFioyP4uQuR4MPYrsh9eBz/S5jkDpCNfP8QPhL2RS/uTUfmKE0pbZ5CwpR1qWrcYxgRVFVRK+FzQ5kRIEJQuuyPakp5uqtTOzOtZpFijRjg5mL2nxUalCOMtwESSdgslR6+VSxhytxCGmp4Rq+PiHP6WOrNJ745g8YU3mdGOcYxPkoBmiIUDT7Y1khJuicZ2PttYRSWWwjN7b3sHIwOuM3ZvNizLOhe4d/ZettRmYxAtFtNojr0nzT5C5YVSIDtaxPDyKEXVrBPoF8v66hKWKciwjiTi5MBe89uEAfmf0GMEjabXk7zwdu7YSV3h56BcidWnbcLWFJMIe5yF5GpDq7wbidEIodbeHA0Pru85GsD2iCd2YwQzz9KKYJ3MGEoo6mHDdv5zV0x3e8mhn94EbETTphCccYkcPu0eNkdHlGjKRA/NvvVdjI6KzqLNZN46W5o1albhj+7FO38vTOXVEhE6P1EDgOV2A3tjfPUEZZQwY2CAtCNjPb/ImW4gj5p6VBgo+kN2cOde5mS3Gn+d+koSg8hiXo3C0kQxBqXApkoU/memmvV/a1f/76/Ni0HfU3of599O6SizNJD2GU6i6Z353Bu2iB/SgNINOVsa10KtLATi+yRYNjFxpCBZ0y9GDDMzdxB4trUMm+fH6TXMQjyaXeZ1a7/0+qiIo/75qjgLJZxYhtV7ACKUDMZzBS4IZXlRLYdUi9Wmn99cN7KVCYAlj0QwibZmMZOiUi5XIgN/enCh38nIvqHOUgS0lMjxg0YcIcigy0PwUK/Sv3QSS2NxoaGT2gNHCkNpDfaRbn1De7irfYq7YvLxekqbunmwUvSNDEKPnQNi0eu71GY40Je91EJlpeBN4tAJnraxkiFCaBdEByZ54DRkdl0Eq2lPvNKBb4V1c2LylFrYeVGPCbhNBReXk1yVwOVSWGBM+NYW50ge8H+2KAMZdcBVJ3mZmDUflOXCnLI+Q23+86YeRONacBSGC+UIXnNnR6QUh9XLsDKxMqJuslnXS2Mk7TEoIrhgeuJAxrNRYcgpVi98LLPEYpHVHcMN/pE0VcwoqnSF2UEL6SML+Ae7HdiTpWgPRBOlROCQGWluc7Pvrc7aMRelgMQCIadYIfghIcBqCZBtNGIDto/XjH/xIVcqeaMDofDfCmySnQnih5yA5qFCIRzEebXNHkc7IB3rPZKSedSGIYrRamx3f7fld7+4DfPdHsAi0SY33WcA5B/WSpGUK3CzQEYRaaThPnLFjpJ45MAcHGn1yEeTgwi/jRUMUoYBw3wA8r+NC91+o/4GQCncYY5KA+nXKLvfuXjJPt1VgmyLpo3zMsMcmXquF2T7xxOsPFutEEw3HwSkrkRm8jhD5fSbBWnIMUsm2r0JrYR2jQKhK+6PlidReF8mCksxxIV5yGGg1arqVtphSJ3qHYD0xiLGhxpTDUx9ud2uhP+HaVWFHnkBNdQaddFXWcVXeb/yxzmm/YiR7TOC1Tq+mEq63j/Rm7tJml5bxG4vZRbNmLqMUQt6GIIFQQ7khYxDkoQnQP12tlCPRKYLMP9av1KFkoQz/5v6NqxRJ925L3fIjZHcDd3ZYOLl3AklL7+BsM8lgZ6dj3caf52QOl0zjWhKkayLIKoX/H+8oeOuR8IdVEWUHqzvUMxmD8+VnCyWSCaqZShGYoxoZ+6/70RjnmT1ZuHFUQaowWRJnnjV0Td59MajH8SSKi4cnOzP5S3HcW4PVOYI0ifd1pRTxkh3ypdvHkYlVJjKHE47W83IMQYhKFyKNPOt4SuNL/h8uSkgkqQFOjsDqiJkTJxMuNxshGLl9p/4o/PMg9PlORxCMYHe02DgELp5ToVwVeMaWqUR0aAzfLG9J9hBPKXkxJnYHD47nlqjPHKp5+7xQp1Ay20Gbj4hMIpR0HdZ8cW2WGUq1S+/zrJFnfQdXRFFe4gYmZYkYTrKANVc9U6KQM9dgGZ42euSjqJMYe+1XFJmtJuxoj+qciyhFFBdax56E5J7cyzyLtXr65NHCRob/7F7Pyg2TwEGeSloYR1i9FMXgZozeKnrYEcQkiLhzSQlJIHpJLLdawjFR7iZS240uTmUs2CJ5lyEsz7nGAiIJWleHZrEbeX6t8EtEItpLymGaBCWs2a3pjd75cEhIledLJpBcT0rWVAko59H8OiGJuTMMalHKjvYHpQdDqL+YhbXOBI/g722exMhxs1KXdoXg+KJSUnUZtOXScgXzLhHGKzohBM8eVCrk0ZOjt14n8R4gJDYM2qdc6XLendxpBscddI8S/Iy5vXLbywFGN7PqiNYdy2rF/4fGdwj7jJ5jlI1Bwjcgo6TzMUfOSDNS0wzeWNkDhnS8Yf4RSjEhtYIsuiqHdbYkaegQ0mk878qciPONRt4Z/Gl08NwucyxzjmMFvu9WuKLKUZUGAw3jHKcWIiaSAe+Eyx0SzzGM8wQm4Ee7X4Xg37lG/c4CyafkqCVz6Tk6cL0j1BrSzolk1+k7CaX4l5ZwJLsg7Yd3QizjYb6sMzK/QUOPZLCeTqgDErYZtFuJSHt6DTda2Bq4H2SPZKylvp8xuiEcoQjJrnMns6C3pvcPtxnP2ZREItWmGqJJnl7xldPTPEjsaE5ZWS3thDB60QwYBJVFK5TwaJYRg2fJr9TlKgml6Kn81RmmT4kjPfC/k0XdAucnmoTztmiyA6r/ZgKhccF39Oh+UR8h4brAZxyoE6l0hNkfXCUPy0VJqUiBGHpXAkmjn2V47qkZE3OG4rZCqRDGZuJY/TtUCGBLbaXjCx5QgjRLtJt8S8TUSZNzMnoyz0ZovdHPAcizC+NHt5r6HHmI+31gd6F5kp3Gi3iIiuFJJp+E9QoZJXBge0L4RsKBtLo7th+eR94o6P2XhpQkFI0Fv/cgoX1PFvFOHGznxuMoeRpKjpsBlirC8ZIqpMMMDQovaZKJmyyDdcoQhxYePBc5WwkKHZ+2Ye80sDswnlp53o58XhDa/9t5MLL4NTKn3BkeOBNOxWV6U7eyK3A6Q8WBGDqgJVaG5GJ5XhvR14xD4kMGiqxa5pjT6heo8+wTJIL6bCd2Yma6zBaczJedBZk3gfiNyaia3Fo+6WQcUJp0enRMox3uoFCJDlzomTkAVXtCUnK2ZhSSnSPA4yfLcZ1bnJOyG3J6pKys5OBNfGMjyFxHQryRkTaKltajZLxgkuWpku4fzjh6+arnFlDOeBSj60mW30cnKcLdOjAEL4yHVAUW9gyELyh8WwaTnpuOOBn9LrAAoHVKKy0QGQYkvFoX0UhNmuiVrVuhzeyZdtlMT8SjBvzyzIdUm2hkGVTkqtE3IbmrrW3wPrw5+LmbkbkuzvCC797mJIzeB1s9RFYBPXpHQuIqOUocoQ0gkvv+NmkHpYCwvoBbgj2XmLzjEkogKrSq4RnVvr0libz2FhnDOpzJQqghuXL00SpEraNbW7Qk//vrc2QyP6TnzG69u8NpBkNmaYiON1mKRYS7gXx80TysInu0LapdSdogEyY6jvspnOIGFiqnFcXqlZEEuSG9XHABuOOtJASNEB6nUu9mzV3OnSIumGSklCMh9PRaVoTLbAIpbSXCC77sr8XQOjUp41mjk+jt+gCKyLPwboOFZuCzW28G7zjSkL9rhWZtjsbcg5JgnITLtaWQDNTmKpIxH7SAVDM+VIwtsCaVlg176ENOqxRgo6EGImNYhhmotJDoTR3Nll6NuXN0LYWPHIXkogENN452bjetWpEWELmrLeHeDSctAafp2hfVoShPZJSOrO1l8MjLUjW4MjliH5f48gSqD4F4jzlIZZ09YQTNoSSKk2c3yh7skIvMyrsOhgw1J7x4T26cH8jvXFzyB0SB24uMiZLQW84NXPd2uCaNOVySU7rTKRvftyFsdhJn4zp9RqQkkIvSA+quNmcRikQQMPdg1wokVBf6Ps6dm9nFYx+D6YVMbfNKKcEu7ycQvnqJ/CehoyIIUuySHdqnL6r5WY6kdSMw0GlXUG1/osH1/fVZM+c+doaazV5eyl3VujK1eFUC5QfyBQL32R2GdYJyQRtY0J15N67b0+B45ujknVVGO5Lai6xCnx+2hTKzdbpq64e0l3uMuRIc5wjxJoIeZnsMDpqBiZuZsLu/UPjloR//+IeUMLVGN9CFXvRC0NJszh5BUWsPnjHERmtQICQj0fFVGjEfngljr9zSbgF6uMoVQTKGZy7Blxs13VB4p83Isi803BUoxZ/QBcw8sno7wcGdB+RIEvD5hAedFgHm6xJjogQcqNK9NTogHJKZmQWuSiUTSIeoV0OkP0TyjuP6nOTySE09w+e5qMVGy1/vnEzw5ZA7DglxQmk3yMFoP8KI/JFM2pogttlCBLgzZYvKLwx3gm4IzbyGogHmaQWjzK48v83WzoxCziEh5ZMmv2i6U9qOIgnxldXmtoQk4ZRCqBx0CBl4jToLIyB3JEMNlTJJd/xFEy+BNx4K/59I8tGaxF+w4otMuvqFwiD2RProUBGUbNZXxjh7NIxJl04L0WGwilyJQLwgc1ygNGtyZMB7RKUIjKmRUJRdE09pudZalptYJY3vUWSM6nAIMj6cpmX43y4tqLPc/Qq+x2wkHlN0bhjJpSbSyx09biBtw5pzwfUCdiYIi+dzVurO1dUl206HgYYLMF7oEE6C2leODulNBlAuzdCT3tBqK8/zvQ5voD175ID1CAA59oyJniQU5nZbyMb5Hp28xMMbJVychY3qcKDxAUonC/MepW7DHL1i+euatSQX2D2fDYWQXO6CJjx0c1645Xv08K2H5NfOIoet9Bw8PPUS+GKPvFOBua7QZDNgyA3zdxOqT9U5gzKqoXuGh0VKtVaiC4rUgLsI542hNMLPFkH6QQT9k6I3ecYKbJtZV2tYZ3w2QRKaPtAXQBDwWejNu0PB7LnuGYuFFs62wl0Yq3GvxpBrdNK+ONcASYkyrcKhbyYMW0bUZXYKGzyGBdQrXlAaDQqRnRQyQJF6C4qpZhuJqCEZjnlwnCeXQyqJlXQ9xQZUn0QcCjpXXOw7g4v1tk75SVhZIhOXe97U871p+I/2zROkLPSE4OFFsHckWVpWLEWy/5znHS39C2fOjZDRXuDRx5NBjjZB6bQtWmsg60jkq8WiNN75fXaAGnoIDJS7GiNjrdMQKL2vJj09EWDJWc//xplb2vQswkoW905E0/avtsosVAf2jyuYq7xpvMGE7GaMZpQMkxoQ2U7dkO8CadCBvsCvSwOtVrRWhqzt/0khp4S8w6DdISUy0uXNgrTTWQmRdA2qQxHIvY7WfUPlU5hxAzesD7QK6UGyLro2kRe8EJ7yhJDOG34Z4ylhkJYEMTwZ4lUQzQ4v8uXwaqNqZUDCtHROh1lzr1DdMRy9dU1aRqfQ7o2efKChEszElyQaQLd8kjC2EjQ3z8owMlGXUpd3IAvDp/ucPCBtYBAaF9rnl9kSujz6jtLosWbowE3/zTiHOhDDmJlN9oNohINFI4yFo6HsBPWxA3kHyfif+dlRjVQoFr2Q7J/5c23QuDYxyAEGlNJEW9jvtbQlVGCOtB4bEmqwWaEMuSW85HYk0uEUNO63tJpjsmBvF9opMdIxa4IYr5iFv28sPsKQ8A0Ie+5G2MwEjtaiConSJHAnU3/MlKHmJGHYlWMU6tokss5uzRH3QwpD6lLWPXvJ+zMJqwdBueY7YGiytpgu7tYmoyDBcxJwFBKkO2NuK6+G58muBYOpBONcOUNUwvTAPPuSPsPYyvpjLClf8vJExyLm3ndhGSESnjovuZfGod2RgSZkDKe8payWSB+7gZIdZ7DEYIodxmeevSdzxIFAW4y+GPulg8WXCrat2DW0cGaJNbjjcBIvn5jv7Z2J2pKgRIeAgnSRIJOFn5zBSJ9J+PAWNUbvIlYJMiH9/xrCg+YMBCuh97Ulwhb4zFkLxwkabWTrbjEMr9YuiQZO1N0GKPwq+3pQa8rh2BJ9gI3Q2VjGatswIp/nBh9tyo2gGiN53BINKF1wGzio3hlJVBVQGWDpppCTDtwNmoRqzKacImxBDc9+4sa9ILr9pf05CWmD4AAz83ejx2idYm+lLeozJxMJj6cQskeFOkwEhdDrUrfIWRBjA2JktuS4K3KbIvnCE4bTgz8TKEIOOW0q0s1x7pK+QvrhIfDDRQhli6BlDYT7HZxwbjx/e0dFNnkvratWpUWlh1f2iJGinF4rQH01PxxSDsid0Ndg+KmKaTUyrEgtK/g9i8Fx5oDDnYGFzq03rAV0N9uHWImB0D4DrS1ckfYhxeel1GkwEmYiPWEO6Y44xzMWKSMH7gzeCqLRYGSlbfq+aLb/ukTbSR8GhRoNnGogtVYjSdNUwiHNsEn2TnuSTfVWaAQqUtpc4o4kWp4LrtFQn8zLyoXDtPcM0rpEQCWPkQ4aX3XSm+OhC5UmGRWR15Qs6cgNdSjpfRdKGxLRjISSxNDUCujE8Carupo+h9NOE962EknnsBIv4d2OCAhplMBLeyBa8CDdGTFab3ii0oNQENpLvf1KhNB3Nb20+k87ziZfzobiTYLAK3GOHGce6P/T29+BiPdb4eB6KHMG8upSGhj4RL5H27hXbwZKO6eS0LMYZ5wvJTNcFMQ/c8OM1tmV6cN3ET490zFoHSPS2w40hESakivJ2wFk4hWRye63ogPDg/70XmEpEfFWDKPJjUd7zKUgxEAPzpCMz3aafqehK4KYaS2g4302SVzscxYrRy96k0E2hbP19S+7mFrzz9QTdtHnfn99VtH9XHLGpuL4MyzrMKEMRYouci+ZRFY9qCPU8FVAKdioZHlTFN1eXb2kiKAYFJq4zDnqwYNa//WaJo7J3aq0RRDdNDqylbJq7XqNJo0m72BIcuQuXu+BdfSUWskq55rIGdCukoeLOcZye4yb2R4dGGMckWhDjJ2etjyo4awZL9lxXlhaPlGKPFfJ4xKSj0x+L51/QRzsQdsB+J7po/AP2W5cjXHWORyVJC+j1LoY5dIfni/N6WLqQSTCH/bIYkqXUltXgnlCGkG33cuXmTv4ZgeioRFkpvTIu2a08632jsr8jrD+9/31uRLYnV9bQX9IvOdMzbFnOGEbGQPwe+gZlcUbcrnqHysSOHXDGeTUfYKwh9dZIRCiRkcHBRLPBugK6mkC5LmQJbd5ZPcGR5pKyTFgIvij+aVljAm6cZrn/k6EqaQBBsg+cuXDEBhjzepHDj5jHDZfBYmml1CBIerTxx/+kOKA3qJKUWTk3pGZ/yH4DruXTzVGKZDVw7kXauYQoXMixhHp3IokISPzzuZF2co5j83Dg5jFRTN4VlRWzn/8d18wspbSJUGO8R1i9EvbdgmZrPeWILTbQPeHiGFePVaqlUhE6rDCtnWqjW7NcYbHbL0N6HxxESPh570VAa1rGrqMhR2VsPdrx0HRibR2YpM0YQY6TZzHCaXmE6BzDoao6zlbU5G5slraVhrCaWMnxrlSGcWKgOkhKxRgXOVfyS/fCYkdDR5QRcNh2qIBEGVPRZqB+tNYN2EKCDmR7/IkTLVzPgZDO9tfxpUrhRmJSMM4bg/eLzIzDrkrSRLf5JLbBWHi9xmQHlbJuIJ87rVoJ0MflsTAV1q5C5wgazjEE5KSNpqIaG026LwwSUWN8DCmXpEe+oIuRpTQmKFff1uAYp11lWCY25LhCjjRjpwKelz/incCEacHCfsAZO9VJDH00A2l6rsHdNyeGP5a7AgEEN6QPs6NFsIYQ7ojxF7hY1I4r6O80IOUr5N4adGocHdvY6FS4P1PNEvXkJo4RKjDFy2pSbWm81WooIQTznAGBsU2wYCOf9FPOifpikaLx+hXMsezV54iBgAdPfCi4rP2J6ICGJRiYh0G3NlA2+x67sbthf+uBK7Y/YVxPQ4yWHTD2Yq38sgdEZ7tfFekn98MSDEt+czNGO9qUTZLtrhIGj4UmoQm8JmbEUb76PM4z1VOgmk1ijVYBbMAx0OhA+6IoT8Cfk+Qd0EBI6BwHEDiUod69iT7hd4D4Cs9S6L18ZPQUmgTIt2Duxqca2IM+fIgu5UweTRGwRHGhN40jnGNSORKgGVhDLcTCnWjBcYLOgdZIcWTznuSB2VLaS2V5ZJDTmZNo3RdWYlJFmSrHoleju+YGO1uRKOUkp2PYSrHSACHMOFIplq0EaJljF6Dj1RKAxn/kISZ1nlz6EzmeLAStYJ0aHoiVesJ/a/+hI9+PANVN0eJwSJFmq2m7CeT+aMTlLGf2NAJYbaj/uTAU26dInmnWwmxkwfFDCpwekMoiQodkyvMUhRDgOL/AGwSwNvkyj03AAAAAElFTkSuQmCC") repeat; background-size: 40mm 40mm; }

.frame { position: absolute; inset: 7mm; border: 3.2mm solid var(--wood); }
.frame::before { content:""; position:absolute; inset: 1.4mm; border: 0.9mm solid var(--red); outline: 0.5mm solid var(--ochre); outline-offset: 0.9mm; }
.frame::after { content:""; position:absolute; inset: 3.6mm; border: 0.6mm solid var(--green); }
.cloud { position: absolute; width: 16mm; height: 16mm; color: var(--ochre); opacity: .9; }
.c-tl { top: 14mm; left: 14mm; transform: scaleY(-1); }
.c-tr { top: 14mm; right: 14mm; transform: scale(-1,-1); }
.c-bl { bottom: 14mm; left: 14mm; }
.c-br { bottom: 14mm; right: 14mm; transform: scaleX(-1); }
.pbody { position: absolute; top: 28mm; bottom: 30mm; left: 26mm; right: 26mm; }
.folio { position: absolute; bottom: 17.5mm; left: 0; right: 0; text-align: center; font-family: "Song Myung"; font-size: 10.5pt; color: var(--soft); letter-spacing: .3em; }
#flow { position: absolute; left: -9999mm; width: 158mm; }
/* 표지 */
.cover { position: absolute; inset: 0; }
.cover .titlebox { position: absolute; right: 28mm; top: 28mm; writing-mode: vertical-rl; border: 1.2mm double var(--wood); background: #F4ECD8; padding: 9mm 5mm; box-shadow: 0 0 0 1.5mm var(--paper), 0 0 0 2.2mm var(--ochre); }
.cover .t1 { font-family: "Noto Serif KR"; font-weight: 900; font-size: 44pt; letter-spacing: .25em; line-height: 1; }
.cover .t2 { font-family: "Nanum Brush Script"; font-size: 24pt; margin-right: 4mm; color: var(--soft); line-height: 1; }
.cover .center { position: absolute; left: 24mm; right: 80mm; top: 70mm; text-align: center; }
.cover .incense { width: 60mm; height: 70mm; color: var(--soft); opacity: .55; }
.cover .whom { font-family: "Nanum Brush Script"; font-size: 40pt; margin-top: 4mm; }
.cover .whom small { font-size: 18pt; }
.cover .issued { margin-top: 3mm; font-family: "Song Myung"; letter-spacing: .3em; color: var(--soft); font-size: 13pt; }
.cover .seal { position: absolute; left: 30mm; bottom: 32mm; }
.cover .motto { position: absolute; left: 62mm; bottom: 36mm; font-family: "Song Myung"; font-size: 12pt; color: var(--soft); line-height: 1.7; }
.seal { background: var(--red); color: #F3E3C8; display: flex; align-items: center; justify-content: center; border-radius: 1.5mm; transform: rotate(-3deg); box-shadow: inset 0 0 0 1mm #F3E3C8, inset 0 0 0 1.6mm var(--red); }
.seal span { font-family: "Noto Serif KR"; font-weight: 900; font-size: 15pt; writing-mode: vertical-rl; letter-spacing: .1em; line-height: 1.05; }

/* 명식 */
.myeongsik { }
.kicker { font-family: "Song Myung"; letter-spacing: .35em; color: var(--red); font-size: 12pt; text-align: center; }
h1 { font-family: "Nanum Brush Script"; font-weight: 400; font-size: 40pt; line-height: 1.15; text-align: center; margin: 2mm 0 0; }
.summary { text-align: center; color: var(--soft); margin: 3mm 4mm 0; font-size: 12pt; }
.keywords { text-align:center; margin-top: 4mm; }
.keywords span { display:inline-block; border: 0.4mm solid var(--red); color: var(--red); padding: 0.6mm 3mm; margin: 0 1mm; font-size: 11pt; font-weight: 700; }
.altar { margin: 9mm auto 0; display: flex; justify-content: center; gap: 6mm; padding: 6mm 0 7mm; border-top: 1mm solid var(--wood); border-bottom: 2.4mm solid var(--wood); background: linear-gradient(#E6D7B6, #EDE2C9); }
.tablet { width: 27mm; text-align: center; }
.tab-head { font-family: "Noto Serif KR"; font-weight: 700; font-size: 10.5pt; color: var(--soft); letter-spacing: .2em; margin-bottom: 2mm; }
.tab-body { height: 58mm; background: linear-gradient(90deg, #4A2E1E, #6A4630 45%, #4A2E1E); border-radius: 13mm 13mm 1mm 1mm; border: 0.8mm solid #2A190F; display:flex; flex-direction: column; align-items:center; justify-content:center; gap: 3mm; box-shadow: inset 0 0 0 1.5mm rgba(176,138,62,.55); }
.tab-body span { font-family: "Noto Serif KR"; font-weight: 900; font-size: 25pt; color: #F1DDAA; line-height: 1; }
.tab-body.unknown span { color: rgba(241,221,170,.45); }
.tablet.me .tab-body { background: linear-gradient(90deg, #7A1E17, #A3352A 45%, #7A1E17); }
.tab-foot { margin-top: 2mm; font-size: 11pt; color: var(--soft); }
.ohaeng { display:flex; justify-content:center; gap: 5mm; margin-top: 8mm; }
.oh { width: 24mm; text-align:center; }
.oh .h { font-family:"Noto Serif KR"; font-weight:900; font-size: 18pt; }
.oh .bar { height: 26mm; display:flex; flex-direction: column-reverse; gap: 1mm; margin: 2mm auto 0; width: 9mm; }
.oh .bar i { display:block; height: 4.2mm; background: var(--wood); border-radius: .6mm; }
.oh.yong .bar i { background: var(--red); }
.oh .n { font-size: 11pt; color: var(--soft); }
.legend { text-align:center; font-size: 10pt; color: var(--soft); margin-top: 3mm; }

/* 본문 장 */
.blk { break-inside: avoid; }
.chapter-gap { height: 7mm; }
header.ch { display:flex; align-items:center; gap: 4mm; border-bottom: 0.5mm solid var(--wood); padding-bottom: 2mm; margin-bottom: 4mm; break-after: avoid; }
.num { width: 13mm; height: 13mm; border-radius: 50%; background: var(--red); color: #F3E3C8; display:flex; align-items:center; justify-content:center; font-family:"Noto Serif KR"; font-weight: 900; font-size: 13pt; flex-shrink:0; box-shadow: inset 0 0 0 .7mm #F3E3C8; }
header.ch h2 { font-family: "Nanum Brush Script"; font-weight: 400; font-size: 30pt; margin: 0; line-height: 1; }
header.ch .sub { font-family: "Song Myung"; color: var(--soft); letter-spacing: .4em; font-size: 11pt; margin-top: 1mm; }
.para { margin: 0 0 2.6mm; text-indent: 0.8em; }
.para.lead { text-indent: 0; color: var(--soft); }
.row { display:flex; border-bottom: 0.2mm solid rgba(58,35,22,.25); }
.row.first { border-top: 0.5mm solid var(--wood); }
.row .th { width: 36mm; text-align: left; font-family: "Song Myung"; font-weight: 400; color: var(--red); padding: 1.6mm 3mm; border-bottom: 0.2mm solid rgba(58,35,22,.25); border-right: 0.2mm solid rgba(58,35,22,.25); white-space: nowrap; flex-shrink:0; }
.row .td { padding: 1.6mm 3mm; }

.fpair { display:grid; grid-template-columns: 1fr 1fr; gap: 0 6mm; margin-bottom: 3.5mm; }
.fitem { break-inside: avoid; border-left: 0.8mm solid var(--ochre); padding-left: 3mm; }
.fpart { font-family:"Song Myung"; color: var(--red); font-size: 11pt; }
.fobs { font-weight: 800; }
.fitem p { margin: 0.5mm 0 0; font-size: 11.6pt; line-height: 1.7; }

/* 당부 두루마리 */
.scroll { break-inside: avoid; margin-top: 6mm; border: 1mm solid var(--wood); background: #F4ECD8; padding: 7mm 9mm; position: relative; }
.scroll::before, .scroll::after { content:""; position:absolute; left:-3mm; right:-3mm; height: 3mm; background: var(--wood); border-radius: 2mm; }
.scroll::before { top: -3mm; } .scroll::after { bottom: -3mm; }
.scroll h3 { font-family:"Nanum Brush Script"; font-weight:400; font-size: 30pt; text-align:center; margin: 0 0 3mm; color: var(--red); }
.scroll li { margin-bottom: 2mm; }
.closing { break-inside: avoid; text-align:center; margin-top: 12mm; }
.closing .seal { margin: 0 auto 4mm; }
.closing p { font-size: 10pt; color: var(--soft); line-height: 1.7; margin: 0 10mm; }
</style></head><body>
<template id="deco"><div class="frame"></div>${cloud("c-tl")}${cloud("c-tr")}${cloud("c-bl")}${cloud("c-br")}</template>

<div class="page" data-deco><div class="cover">
  <div class="titlebox"><span class="t1">命相帖</span><span class="t2">사주와 관상이 함께 쓴 운명첩</span></div>
  <div class="center">
    <svg class="incense" viewBox="0 0 120 140"><g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
      <path d="M60 96 C50 82 70 72 60 58 C50 44 72 36 62 20 C58 12 64 6 68 4"/>
      <path d="M54 96 C44 86 58 76 50 64 C44 54 54 46 50 36"/>
      <path d="M66 96 C76 86 64 78 72 66 C78 56 70 50 74 40"/></g>
      <g fill="currentColor"><rect x="44" y="96" width="32" height="5" rx="1"/><path d="M38 101 h44 l-6 22 h-32 z"/><rect x="46" y="123" width="6" height="8"/><rect x="68" y="123" width="6" height="8"/></g></svg>
    <div class="whom">${esc(name)} <small>앞</small></div>
    <div class="issued">${issued}</div>
  </div>
  ${seal("命運", 24)}
  <div class="motto">하늘이 정한 바탕 위에<br>사람이 걸어갈 길을 적어 올립니다.</div>
</div></div>

<div class="page" data-deco><div class="pbody"><div class="myeongsik">
  <div class="kicker">四柱命式</div>
  <h1>${esc(reading.headline)}</h1>
  <div class="keywords">${common.map((c: any) => `<span>${esc(c.label)}</span>`).join("")}</div>
  <p class="summary">${esc(reading.summary)}</p>
  <div class="altar">${["hour", "day", "month", "year"].map((k) => tablet(saju.pillars.find((p: any) => p.key === k))).join("")}</div>
  <div class="ohaeng">${Object.entries(saju.fiveElements)
    .map(([e, n]: [string, number]) => `<div class="oh ${(saju.yongsin as string[]).includes(e) ? "yong" : ""}"><div class="h">${EL_HANJA[e]}</div><div class="bar">${"<i></i>".repeat(n)}</div><div class="n">${e} ${n}</div></div>`)
    .join("")}</div>
  <div class="legend">붉은 칸은 나를 돕는 기운 · 왼쪽 위패부터 時 · 日 · 月 · 年</div>
</div></div></div>

<div id="flow">${blocks.join("")}</div>

<script>
// 블록을 A4 쪽에 차례로 채워 넣기
(async () => {
  await document.fonts.ready;
  const NUM = ["一","二","三","四","五","六","七","八","九","十"];
  const folio = (n) => n <= 10 ? NUM[n-1] : n < 20 ? "十" + NUM[n-11] : "二十" + (NUM[n-21] || "");
  const flow = document.getElementById("flow");
  let body = null, count = 2;
  const newPage = () => {
    const pg = document.createElement("div");
    pg.className = "page"; pg.setAttribute("data-deco", "");
    body = document.createElement("div"); body.className = "pbody";
    pg.appendChild(body); document.body.insertBefore(pg, flow); count++;
    const f = document.createElement("div"); f.className = "folio"; f.textContent = "― " + folio(count) + " ―"; pg.appendChild(f);
  };
  newPage();
  for (const el of Array.from(flow.children)) {
    if (el.classList.contains("chapter-gap") && body.children.length === 0) continue;
    body.appendChild(el);
    if (body.scrollHeight > body.clientHeight + 1) {
      body.removeChild(el);
      // 장 제목이 쪽 끝에 홀로 남지 않게
      const carry = [];
      const kids = Array.from(body.children);
      const n = kids.length;
      // 장 제목(+그 아래 한 줄)이 쪽 끝에 홀로 남지 않게 다음 쪽으로 함께 넘긴다
      if (n && kids[n-1].tagName === "HEADER") carry.push(kids[n-1]);
      else if (n > 1 && kids[n-2].tagName === "HEADER") carry.push(kids[n-2], kids[n-1]);
      carry.forEach((c) => body.removeChild(c));
      newPage();
      carry.forEach((c) => body.appendChild(c));
      if (!el.classList.contains("chapter-gap")) body.appendChild(el);
    }
  }
  const deco = document.getElementById("deco").innerHTML;
  document.querySelectorAll(".page[data-deco]").forEach((pg) => pg.insertAdjacentHTML("afterbegin", deco));
  flow.remove();
  document.body.setAttribute("data-ready", "1");
  ${opts.autoPrint ? "setTimeout(() => window.print(), 300);" : ""}
})();
</script>
</body></html>`;
}
