import type { NextConfig } from "next";

// Proxy /api và /audio về backend FastAPI (mặc định cổng 8000) khi chạy dev,
// nhờ đó frontend chỉ dùng đường dẫn tương đối. Đổi backend qua biến BACKEND_URL.
const backend = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
      { source: "/audio/:path*", destination: `${backend}/audio/:path*` },
    ];
  },
};

export default nextConfig;
