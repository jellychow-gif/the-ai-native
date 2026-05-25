"use client";

import { useEffect, useState } from "react";

/**
 * Floating "back to top" button — appears after scrolling past one viewport.
 * Smooth scroll, no library. Subtle entrance.
 *
 * Hidden by default to keep the page clean above the fold; fades in only
 * after the reader has committed to the page (~one screen of scroll).
 */
export function BackToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 600);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handle = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <button
      type="button"
      onClick={handle}
      aria-label="Back to top"
      className={`back-to-top ${visible ? "back-to-top--visible" : ""}`}
    >
      <span className="back-to-top-arrow">↑</span>
      <span className="back-to-top-label">Top</span>
    </button>
  );
}
