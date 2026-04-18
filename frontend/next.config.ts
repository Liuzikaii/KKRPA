import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  // Allow images from any source in desktop mode
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
