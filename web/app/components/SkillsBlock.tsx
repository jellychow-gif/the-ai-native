import { getSkills, getFeaturedSkill, type Skill } from "@/lib/db";

/**
 * AI 工具速览 — homepage hero block (replaces 本周观察 from earlier design).
 * Pattern: 1 featured skill (large) + the rest as a grid of small cards.
 */
export function SkillsBlock() {
  const featured = getFeaturedSkill();
  const others = getSkills().filter((s) => s.id !== featured?.id);

  if (!featured && others.length === 0) return null;

  return (
    <section className="skills-block">
      <header className="skills-header">
        <div className="skills-eyebrow">AI 工具速览 / Tooling</div>
        <h2 className="skills-title">值得 dogfood 的 AI+HR 工具与技能</h2>
      </header>

      {featured && <SkillFeatured skill={featured} />}

      {others.length > 0 && (
        <div className="skills-grid">
          {others.map((s) => (
            <SkillMini key={s.id} skill={s} />
          ))}
        </div>
      )}
    </section>
  );
}

function SkillFeatured({ skill }: { skill: Skill }) {
  return (
    <a
      href={skill.url}
      target="_blank"
      rel="noopener noreferrer"
      className="skill-featured"
    >
      <div className="skill-meta">
        <span className="skill-vendor">{skill.vendor}</span>
        <span className="skill-divider">·</span>
        <span className="skill-category">{skill.category}</span>
      </div>
      <h3 className="skill-name">{skill.name}</h3>
      <p className="skill-oneline">{skill.one_line}</p>
      <p className="skill-summary">{skill.summary}</p>
      <span className="skill-cta">Explore the tool →</span>
    </a>
  );
}

function SkillMini({ skill }: { skill: Skill }) {
  return (
    <a
      href={skill.url}
      target="_blank"
      rel="noopener noreferrer"
      className="skill-mini"
    >
      <div className="skill-meta">
        <span className="skill-vendor">{skill.vendor}</span>
        <span className="skill-divider">·</span>
        <span className="skill-category">{skill.category}</span>
      </div>
      <h4 className="skill-mini-name">{skill.name}</h4>
      <p className="skill-mini-oneline">{skill.one_line}</p>
    </a>
  );
}
