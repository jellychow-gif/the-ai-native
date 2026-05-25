import {
  getBySection,
  SECTION_META,
  industryPriority,
  HR_TECH_SOURCES,
  type Section,
} from "@/lib/db";
import { Signal } from "./Signal";

/**
 * Generic section page — used by /organization, /hr, /industry routes.
 *
 * For Industry: items are sub-grouped (HR Tech vendors first, then other
 * SaaS / AI infra) per editor's "HR Tech 在前" rule.
 */
export function SectionPage({ section }: { section: Section }) {
  const meta = SECTION_META[section];
  const items = getBySection(section);

  // Industry: split into HR Tech (priority 1) and Other SaaS (priority 2)
  if (section === "Industry") {
    const hrTechItems = items.filter((i) => HR_TECH_SOURCES.has(i.source));
    const otherItems = items.filter((i) => !HR_TECH_SOURCES.has(i.source));

    return (
      <div className={`container section--${section.toLowerCase()}`}>
        <header className="section-page-header">
          <div className="meta-top">{meta.zh}</div>
          <h1 className="title">{meta.en}</h1>
          <p className="subtitle-zh">{meta.tagline}</p>
          <div className="update-promise">
            {items.length} signals · {hrTechItems.length} HR Tech ·{" "}
            {otherItems.length} 通用 SaaS / AI
          </div>
        </header>

        {hrTechItems.length > 0 && (
          <section className="industry-subsection">
            <h2 className="industry-subhead">HR Tech 公司</h2>
            {hrTechItems.map((item) => (
              <Signal key={item.id} item={item} />
            ))}
          </section>
        )}

        {otherItems.length > 0 && (
          <section className="industry-subsection">
            <h2 className="industry-subhead">通用 SaaS / AI 基础设施</h2>
            {otherItems.map((item) => (
              <Signal key={item.id} item={item} />
            ))}
          </section>
        )}

        {items.length === 0 && (
          <div className="empty">
            <p>本板块暂无入选内容 / No signals yet.</p>
          </div>
        )}
      </div>
    );
  }

  // Default: Organization and HR
  return (
    <div className={`container section--${section.toLowerCase()}`}>
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
