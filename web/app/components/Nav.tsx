"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/**
 * Top navigation per PRD §6.2. Four primary destinations + brand wordmark.
 *
 * Each link carries its section accent as an underline marker — default
 * is a short faded hint, hover expands to full-color, active page locks
 * to full underline + bolder text. Editorial routes (/skills) use the
 * primary text color to signal "editor's hand" vs auto-aggregated sections.
 */
const ITEMS = [
  { href: "/organization", label: "Organization", accent: "var(--accent-organization)" },
  { href: "/hr",           label: "HR",           accent: "var(--accent-hr)" },
  { href: "/industry",     label: "Industry",     accent: "var(--accent-industry)" },
  { href: "/skills",       label: "Skills",       accent: "var(--text-primary)" },
];

export function Nav() {
  const pathname = usePathname() ?? "";

  return (
    <nav className="topnav">
      <Link href="/" className="topnav-brand">
        The AI Native
      </Link>
      <div className="topnav-links">
        {ITEMS.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={
                "topnav-link" + (isActive ? " topnav-link--active" : "")
              }
              style={{ ["--link-accent" as string]: item.accent }}
            >
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
