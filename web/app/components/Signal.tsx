import Link from "next/link";
import { type Item, ANO_DIMENSION_LABELS } from "@/lib/db";

/**
 * Signal card — v5 LaterCast-style.
 *
 * Two modes based on whether long-form Chinese narrative is present:
 *
 *   1) Long-form mode (has `long_form_zh`) — compact card:
 *        [ANO chip] [sub_tag]
 *        Title (links to /article/[id])
 *        preview_hook (one-line teaser)
 *        source · date
 *      Reader clicks title/card → full article page.
 *
 *   2) Legacy structured mode (no `long_form_zh`) — the v2 6-field card
 *      is kept as-is for items summarized before the v5 pivot.
 */
export function Signal({ item }: { item: Item }) {
  const dateLabel = formatPublishedDate(item.published_at);
  const hasLongForm = !!item.long_form_zh;
  const hasV2 = !!item.what_happened;

  if (hasLongForm) {
    return (
      <article className="signal signal--card">
        <div className="signal-top-meta">
          {item.ano_dimension && (
            <span className="insight-chip" title={ANO_DIMENSION_LABELS[item.ano_dimension]}>
              {item.ano_dimension}
              <span className="insight-chip-zh">{ANO_DIMENSION_LABELS[item.ano_dimension]}</span>
            </span>
          )}
          {item.sub_tag && <span className="signal-tag">{item.sub_tag}</span>}
        </div>

        <h3 className="signal-title">
          <Link href={`/article/${item.id}`}>{item.title}</Link>
        </h3>

        {item.preview_hook && (
          <p className="signal-hook">{item.preview_hook}</p>
        )}

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
          <span className="signal-meta-dot">·</span>
          <Link className="signal-readmore" href={`/article/${item.id}`}>
            阅读全文 →
          </Link>
        </div>
      </article>
    );
  }

  // Legacy v2 6-field card — kept for items processed before v5.
  return (
    <article className="signal">
      <div className="signal-top-meta">
        {item.ano_dimension && (
          <span className="insight-chip" title={ANO_DIMENSION_LABELS[item.ano_dimension]}>
            {item.ano_dimension}
            <span className="insight-chip-zh">{ANO_DIMENSION_LABELS[item.ano_dimension]}</span>
          </span>
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
          <div className="intel-block">
            <div className="intel-label">What Happened</div>
            <p className="intel-text">{item.what_happened}</p>
          </div>

          <div className="intel-block intel-block--why">
            <div className="intel-label intel-label--accent">Why It Matters</div>
            <p className="intel-text intel-text--why">{item.why_matters}</p>
          </div>

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

          {item.prediction && (
            <div className="intel-prediction">
              <span className="intel-prediction-label">Prediction →</span>
              <span className="intel-prediction-text">{item.prediction}</span>
            </div>
          )}
        </>
      ) : (
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
