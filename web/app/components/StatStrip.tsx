import { getStats } from "@/lib/db";

/**
 * Tiny stats line under the masthead — signals scale + cadence at a glance.
 * Visual minimum: no boxes, no icons; just typography spaced by middle dots.
 */
export function StatStrip() {
  const s = getStats();
  return (
    <div className="stat-strip">
      <span>{s.sources} sources</span>
      <span className="stat-dot">·</span>
      <span>{s.items} signals selected</span>
      <span className="stat-dot">·</span>
      <span>{s.skills} tools tracked</span>
      <span className="stat-dot">·</span>
      <span>Updated weekly</span>
    </div>
  );
}
