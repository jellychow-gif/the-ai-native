import type { Metadata } from "next";
import { Nav } from "./components/Nav";
import { BackToTop } from "./components/BackToTop";
import "./globals.css";

export const metadata: Metadata = {
  title: "The AI Native · Organization Observatory",
  description:
    "Tracking how frontier companies redesign talent, coordination, and management in the age of intelligent systems.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400&family=Noto+Serif+SC:wght@300;400;500&display=swap"
        />
      </head>
      <body>
        <Nav />
        {children}
        <BackToTop />
      </body>
    </html>
  );
}
