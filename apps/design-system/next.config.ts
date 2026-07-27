/**
 * @file next.config.ts
 * @description Next.js Dev Server Configurations. Includes API rewrites targeting the FastAPI
 * backend controller to prevent cross-origin issues during local runs.
 */

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxies /api/ requests to local FastAPI ingestion server
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
