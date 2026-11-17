const apiTarget = (process.env.API_PROXY_TARGET || (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "https://learnora-backend.vercel.app")).replace(/\/+$/, "");
const nextConfig = {
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "gihfupzvdpyrmynqgukz.supabase.co" },
    ],
  },
  async rewrites() {
    return [{ source: "/api/:path*", destination: apiTarget + "/api/:path*" }];
  },
};
export default nextConfig;
