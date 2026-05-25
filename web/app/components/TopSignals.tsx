import { getTopSignals } from "@/lib/db";

/**
 * Homepage hero per PRD v2 §4 — compact top-N signals digest.
 *
 * Each row: numbered + insight class + title + 1-line Why-It-Matters +
 * Talent Shift + Prediction.  Reads as an analyst's morning briefing.
 *
 * Skipped silently if no items carry v2 intelligence yet.
 */
export function TopSignals() {
  const top = getTopSignals(5);
  if (top.length === 0) return null;

  return (
    <section className="topsignals">
      <header className="topsignals-header">
        <div className="skills-eyebrow">Top Signals · This Week</div>
        <h2 className="topsignals-title">
          5 things every AI-native operator should know this week
        </h2>
      </header>

      <ol className="topsignals-list">
        {top.map((item, idx) => (
          <li key={item.id} className="topsignals-item">
            <span className="topsignals-num">
              {String(idx + 1).padStart(2, "0")}
            </span>

            <div className="topsignals-body">
              <div className="topsignals-meta">
                {item.insight_class && (
                  <span className="insight-chip">{item.insight_class}</span>
                )}
                <span className="topsignals-source">{item.source}</span>
              </div>

              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="topsignals-title-link"
              >
                {item.title}
              </a>

              {item.why_matters && (
                <p className="topsignals-why">{item.why_matters}</p>
              )}

              <dl className="topsignals-mini">
                {item.talent_implication && (
                  <>
                    <dt>Talent Shift</dt>
                    <dd>{item.talent_implication}</dd>
                  </>
                )}
                {item.prediction && (
                  <>
                    <dt>Prediction</dt>
                    <dd className="topsignals-pred">{item.prediction}</dd>
                  </>
                )}
              </dl>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
