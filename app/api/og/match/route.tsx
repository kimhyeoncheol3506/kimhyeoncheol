// 궁합 공유 링크용 OG 이미지 (1200×630). 쿼리의 점수 요약만으로 그림을 만든다.
import { ImageResponse } from "next/og";
import { SCORE_LABELS, fromShareQuery, relationLabel } from "@/lib/match/share";

export const runtime = "edge";

/** 이미지에 들어갈 글자만 담긴 한글 폰트를 구글 폰트에서 받아 온다 (실패하면 기본 폰트) */
async function loadFont(text: string, weight: number): Promise<ArrayBuffer | null> {
  try {
    const css = await (
      await fetch(`https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@${weight}&text=${encodeURIComponent(text)}`)
    ).text();
    const url = css.match(/src: url\((.+?)\) format\('(opentype|truetype)'\)/)?.[1];
    if (!url) return null;
    const res = await fetch(url);
    return res.ok ? res.arrayBuffer() : null;
  } catch {
    return null;
  }
}

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;
  const d = fromShareQuery((k) => sp.get(k));
  const names = d ? `${d.names[0]} × ${d.names[1]}` : "그 사람과 나";
  const total = d ? String(d.total) : "?";
  const headline = d ? d.headline : "사주로 보는 궁합 점수";
  const rel = d ? relationLabel(d.relation) : "궁합";
  const all = `${names}${headline}${rel}${SCORE_LABELS.join("")}두 사람의 궁합얼굴과 운명 faceandfate.vercel.app/1000123456789점`;
  const font = await loadFont(all, 700);

  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", paddingBottom: 56, background: "linear-gradient(160deg,#FBF7EF 0%,#F1E6CF 100%)", color: "#2A2017", fontFamily: font ? "Serif" : undefined }}>
        <div style={{ position: "absolute", inset: 24, border: "2px solid rgba(168,130,58,0.45)", borderRadius: 28, display: "flex" }} />
        <div style={{ fontSize: 30, color: "#A8823A", letterSpacing: 4 }}>{rel}</div>
        <div style={{ fontSize: 52, marginTop: 6 }}>{names}</div>
        <div style={{ display: "flex", alignItems: "baseline", marginTop: 6 }}>
          <span style={{ fontSize: 150, color: "#A8823A", lineHeight: 1 }}>{total}</span>
          <span style={{ fontSize: 44, color: "#8A7D6A", marginLeft: 10 }}>/ 100</span>
        </div>
        <div style={{ fontSize: 40, marginTop: 4 }}>{headline}</div>
        {d && (
          <div style={{ display: "flex", gap: 30, marginTop: 18 }}>
            {SCORE_LABELS.map((l, i) => (
              <div key={l} style={{ display: "flex", flexDirection: "column", alignItems: "center", fontSize: 26, color: "#6B5A44" }}>
                <span>{l}</span>
                <span style={{ fontSize: 34, color: "#2A2017" }}>{d.scores[i]}</span>
              </div>
            ))}
          </div>
        )}
        <div style={{ position: "absolute", bottom: 40, fontSize: 22, color: "#8A7D6A" }}>얼굴과 운명 · faceandfate.vercel.app</div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      ...(font ? { fonts: [{ name: "Serif", data: font, weight: 700 as const, style: "normal" as const }] } : {}),
      headers: { "Cache-Control": "public, max-age=86400, s-maxage=604800, immutable" },
    },
  );
}
