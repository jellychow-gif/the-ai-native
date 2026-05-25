import { getSkills } from "@/lib/db";

export const metadata = {
  title: "Skills · The AI Native",
  description: "全球 AI + HR 工具与技能速览。",
};

/**
 * Skills archive — the editor-maintained catalog of AI+HR tools worth
 * dogfooding. Replaces the earlier /observations route. Data source is
 * data/skills.json (manually curated), bundled into items.json by
 * scripts/export.py.
 */
export default function SkillsPage() {
  const skills = getSkills();

  return (
    <div className="container">
      <header className="section-page-header">
        <div className="meta-top">工具速览 / AI Tooling Catalog</div>
        <h1 className="title">Skills</h1>
        <p className="subtitle-zh">
          编辑精选的 AI 工具、Skill 与 Plugin —— HR 一号位本人 dogfood
          的清单。区别于 Industry 板块的产品新闻流，这里只收**真正用过**的工具。
        </p>
        <div className="update-promise">
          {skills.length} {skills.length === 1 ? "tool" : "tools"} curated by hand
        </div>
      </header>

      {skills.length === 0 ? (
        <div className="empty">
          <p>暂无入选工具 / No skills tracked yet.</p>
        </div>
      ) : (
        <div className="skills-archive-list">
          {skills.map((s) => (
            <a
              key={s.id}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="skill-archive-card"
            >
              <div className="skill-meta">
                <span className="skill-vendor">{s.vendor}</span>
                <span className="skill-divider">·</span>
                <span className="skill-category">{s.category}</span>
              </div>
              <h3 className="skill-archive-name">{s.name}</h3>
              <p className="skill-oneline">{s.one_line}</p>
              <p className="skill-summary">{s.summary}</p>
              <span className="skill-cta">Explore the tool →</span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
