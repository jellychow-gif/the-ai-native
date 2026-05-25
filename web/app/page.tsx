import Link from "next/link";
import {
  getFeatured,
  getIssue,
  getBySection,
  SECTION_META,
  type Section,
} from "@/lib/db";
import { Signal } from "./components/Signal";
import { SkillsBlock } from "./components/SkillsBlock";
import { StatStrip } from "./components/StatStrip";

const SECTION_ORDER: Section[] = ["Organization", "HR", "Industry"];

export default async function Home() {
  const issue = getIssue();

  return (
    <div className="container">
      {/* Masthead */}
      <header className="masthead">
        <div className="meta-top">
          Issue {issue.number} · {issue.date_label}
        </div>
        <h1 className="title">The AI Native</h1>
        <p className="subtitle-en">
          Weekly signals on how organizations are being rebuilt around AI.
        </p>
        <p className="subtitle-zh">每周筛选全球 AI 原生组织的前沿信号。</p>
        <StatStrip />
      </header>

      {/* AI 工具速览 — replaces the editorial observation block */}
      <SkillsBlock />

      {/* Three sections, featured signals only — full archive on section pages */}
      {SECTION_ORDER.map((key) => {
        const meta = SECTION_META[key];
        const featured = getFeatured(key);
        const totalInSection = getBySection(key).length;
        const archiveCount = totalInSection - featured.length;
        const path = `/${key.toLowerCase()}`;

        return (
          <section key={key} className={`section section--${key.toLowerCase()}`}>
            <header className="section-header">
              <h2 className="section-en">{meta.en}</h2>
              <div className="section-zh">{meta.zh}</div>
            </header>

            {featured.length === 0 ? (
              <div className="empty">
                <p>本期暂无入选内容 / Awaiting next week&rsquo;s signals.</p>
              </div>
            ) : (
              featured.map((item) => <Signal key={item.id} item={item} />)
            )}

            {archiveCount > 0 && (
              <Link href={path} className="section-archive-link">
                查看 {key} 全部 {totalInSection} 条 →
              </Link>
            )}
          </section>
        );
      })}

      <footer className="site-footer">
        <p>
          A weekly signal layer for leaders rebuilding their organizations
          around AI.
        </p>
      </footer>
    </div>
  );
}
