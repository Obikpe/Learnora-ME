import { ImageResponse } from "next/og";

export const runtime = "edge";
export const contentType = "image/png";
export const size = { width: 1200, height: 630 };

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = (searchParams.get("title") || "Learn. Practise. Build. Prove.").slice(0, 110);
  const kind = (searchParams.get("kind") || "Learnora ME").slice(0, 70);

  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", padding: "72px", background: "#0b1017", color: "#f5f2e9", fontFamily: "Arial" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "18px", color: "#e9c96d", fontSize: 27, letterSpacing: "5px", fontWeight: 700 }}>
          <div style={{ width: 46, height: 46, border: "2px solid #e9c96d", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 25 }}>L</div>
          LEARNORA ME
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: "1000px" }}>
          <div style={{ color: "#e9c96d", fontSize: 22, letterSpacing: "4px", textTransform: "uppercase" }}>{kind}</div>
          <div style={{ fontSize: 66, lineHeight: 1.12, fontWeight: 700, letterSpacing: "-2px" }}>{title}</div>
          <div style={{ width: 120, height: 5, background: "#e9c96d", borderRadius: 4 }} />
          <div style={{ color: "#aeb8c5", fontSize: 27 }}>Learn skills. Practise with purpose. Build work you can show.</div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", color: "#84909f", fontSize: 19 }}>
          <span>Learn. Practise. Build. Prove.</span><span>learnora-me-v02.vercel.app</span>
        </div>
      </div>
    ),
    { ...size }
  );
}
