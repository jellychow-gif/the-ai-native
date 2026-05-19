import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The AI Native",
  description:
    "Weekly signals on how organizations are being rebuilt around AI.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
