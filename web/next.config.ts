import type { NextConfig } from "next";

const isExport = process.env.EXPORT === "1";

const nextConfig: NextConfig = isExport
  ? {
      output: "export",
      basePath: process.env.BASE_PATH || "",
      images: { unoptimized: true },
      trailingSlash: true,
    }
  : {};

export default nextConfig;
