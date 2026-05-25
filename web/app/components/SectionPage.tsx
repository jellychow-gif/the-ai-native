import { getBySection, SECTION_META, type Section } from "@/lib/db";
import { Signal } from "./Signal";

/**
 * Generic section page — used by /organization, /hr, /industry routes.
 * Lists every published item in the section, newest first.
 */
export function SectionPage({ section }: { section: Section }) {
  const meta = SECTION_META[section];
  const items = getBySection(section);

  return (
    <div className="container">
      <header className="section-page-header">
        <div className="meta-top">{meta.zh}</div>
        <h1 className="title">{meta.en}</h1>
        <p className="subtitle-zh">{meta.tagline}</p>
        <div className="update-promise">
          {items.length} {items.length === 1 ? "signal" : "signals"} 入选历史
        </div>
      </header>

      {items.length === 0 ? (
        <div className="empty">
          <p>本板块暂无入选内容 / No signals yet.</p>
        </div>
      ) : (
        items.map((item) => <Signal key={item.id} item={item} />)
      )}
    </div>
  );
}
