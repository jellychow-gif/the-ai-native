import { type Item } from "@/lib/db";

/**
 * Structured-intelligence card per PRD v2 §3.
 *
 * Layout (top → bottom):
 *   [insight class chip]
 *   Title (clickable)
 *   source · date
 *   ───────────────────────
 *   WHAT HAPPENED  (factual)
 *   WHY IT MATTERS (strategic, accent treatment)
 *   ───────────────────────
 *   Grid of 3 implications: Org / Talent / HR Operating
 *   ───────────────────────
 *   PREDICTION (italic, forward-looking)
 *   Read original →
 *
 * Falls back gracefully to the v1 summary+implication shape for items not
 * yet rebriefed (during migration).
 */
export function Signal({ item }: { item: Item }) {
  const dateLabel = formatPublishedDate(item.published_at);
  const hasV2 = !!item.what_happened;

  return (
    <article className="signal">
      <div className="signal-top-meta">
        {item.insight_class && (
          <span className="insight-chip">{item.insight_class}</span>
        )}
        {item.sub_tag && <span className="signal-tag">{item.sub_tag}</span>}
      </div>

      <h3 className="signal-title">
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          {item.title}
        </a>
      </h3>

      <div className="signal-meta">
        <span className="signal-source">{item.source}</span>
        {dateLabel && (
          <>
            <span className="signal-meta-dot">·</span>
            <time className="signal-date" dateTime={item.published_at ?? undefined}>
              {dateLabel}
            </time>
          </>
        )}
      </div>

      {hasV2 ? (
        <>
          {/* What Happened */}
          <div className="intel-block">
            <div className="intel-label">What Happened</div>
            <p className="intel-text">{item.what_happened}</p>
          </div>

          {/* Why It Matters — accent-treated */}
          <div className="intel-block intel-block--why">
            <div className="intel-label intel-label--accent">Why It Matters</div>
            <p className="intel-text intel-text--why">{item.why_matters}</p>
          </div>

          {/* 3-up implications grid */}
          <div className="intel-grid">
            <div className="intel-cell">
              <div className="intel-label">Organizational Implication</div>
              <p className="intel-text intel-text--small">{item.org_implication}</p>
            </div>
            <div className="intel-cell">
              <div className="intel-label">Talent Implication</div>
              <p className="intel-text intel-text--small">{item.talent_implication}</p>
            </div>
            <div className="intel-cell">
              <div className="intel-label">HR Operating Implication</div>
              <p className="intel-text intel-text--small">{item.hr_operating_implication}</p>
            </div>
          </div>

          {/* Prediction */}
          {item.prediction && (
            <div className="intel-prediction">
              <span className="intel-prediction-label">Prediction →</span>
              <span className="intel-prediction-text">{item.prediction}</span>
            </div>
          )}
        </>
      ) : (
        // Legacy v1 fallback for items not yet upgraded
        <>
          {item.summary && <p className="signal-summary">{item.summary}</p>}
          {item.implication && (
            <div className="implication">
              <div className="implication-label">对组织变革的含义</div>
              <p className="implication-text">{item.implication}</p>
            </div>
          )}
        </>
      )}

      <a
        className="readmore"
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
      >
        Read original →
      </a>
    </article>
  );
}

function formatPublishedDate(iso: string | null): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d.getTime())) return null;
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}
