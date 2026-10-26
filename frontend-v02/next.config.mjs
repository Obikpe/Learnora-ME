const apiTarget = (process.env.API_PROXY_TARGET || "https://learnora-backend.vercel.app").replace(/\/+$/, "");

const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiTarget}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
