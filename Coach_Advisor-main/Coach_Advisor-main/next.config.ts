import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/refactoring',
        destination: '/refactoring',
      },
    ];
  },
};

export default nextConfig;