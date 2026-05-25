import Link from "next/link";

/**
 * Top navigation per PRD §6.2: Organization / HR / Industry / Observations.
 * The logo (top-left) links to the homepage.
 */
export function Nav() {
  return (
    <nav className="topnav">
      <Link href="/" className="topnav-brand">
        The AI Native
      </Link>
      <div className="topnav-links">
        <Link href="/organization">Organization</Link>
        <Link href="/hr">HR</Link>
        <Link href="/industry">Industry</Link>
        <Link href="/observations">Observations</Link>
      </div>
    </nav>
  );
}
