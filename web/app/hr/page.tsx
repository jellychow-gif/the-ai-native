import {
  getBySection,
  HR_MODULE_ORDER,
  SECTION_META,
  type HRModule,
  type Item,
} from "@/lib/db";
import { Signal } from "../components/Signal";

export const metadata = {
  title: "HR · The AI Native",
  description: "HR 各模块如何被 AI 重构？",
};

/**
 * HR archive — grouped by sub-module in the editor's priority order:
 * 组织设计 > 薪酬 > 绩效 > 员工体验 > 学发 > 招聘 (PRD §6.1).
 * Items without classification fall into "其他".
 */
export default function HRPage() {
  const meta = SECTION_META.HR;
  const all = getBySection("HR");

  // Group by hr_module
  const byModule = new Map<HRModule | "其他", Item[]>();
  for (const m of HR_MODULE_ORDER) byModule.set(m, []);
  byModule.set("其他", []);

  for (const item of all) {
    const key = (item.hr_module as HRModule) || "其他";
    if (!byModule.has(key)) byModule.set(key, []);
    byModule.get(key)!.push(item);
  }

  // Sort each module by total_score desc (already done at export, but be defensive)
  for (const list of byModule.values()) {
    list.sort((a, b) => b.total_score - a.total_score);
  }

  // Build ordered display list, dropping empty modules
  const displayOrder: (HRModule | "其他")[] = [...HR_MODULE_ORDER, "其他"];
  const moduleSections = displayOrder
    .map((m) => ({ module: m, items: byModule.get(m) ?? [] }))
    .filter((s) => s.items.length > 0);

  return (
    <div className="container section--hr">
      <header className="section-page-header">
        <div className="meta-top">{meta.zh}</div>
        <h1 className="title">{meta.en}</h1>
        <p className="subtitle-zh">{meta.tagline}</p>
        <div className="update-promise">
          {all.length} signals across {moduleSections.length} modules · 按模块优先级排列
        </div>
      </header>

      {/* Module quick-jump chips */}
      <div className="module-nav">
        {moduleSections.map((s) => (
          <a key={s.module} href={`#m-${s.module}`} className="module-chip">
            {s.module}
            <span className="module-chip-count">{s.items.length}</span>
          </a>
        ))}
      </div>

      {moduleSections.map(({ module, items }) => (
        <section key={module} className="hr-module-group">
          <h2 id={`m-${module}`} className="hr-module-title">
            {module}
          </h2>
          {items.map((item) => (
            <Signal key={item.id} item={item} />
          ))}
        </section>
      ))}
    </div>
  );
}
