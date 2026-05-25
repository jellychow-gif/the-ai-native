import { type Item } from "@/lib/db";

/**
 * Single signal card — same layout used on homepage and section pages.
 * Per PRD §7.1, the "对组织变革的含义" block is visually distinguished
 * (left accent border) so judgment reads as separate from information.
 */
export function Signal({ item }: { item: Item }) {
  return (
    <article className="signal">
      {item.sub_tag && <div className="signal-tag">{item.sub_tag}</div>}
      <h3 className="signal-title">
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          {item.title}
        </a>
      </h3>
      <div className="signal-source">{item.source}</div>
      {item.summary && <p className="signal-summary">{item.summary}</p>}
      {item.implication && (
        <div className="implication">
          <div className="implication-label">对组织变革的含义</div>
          <p className="implication-text">{item.implication}</p>
        </div>
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
