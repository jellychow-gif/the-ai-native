import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // better-sqlite3 is a native Node module — tell Next.js not to bundle it,
  // so the .node binding stays intact at runtime.
  serverExternalPackages: ["better-sqlite3"],
};

export default nextConfig;
