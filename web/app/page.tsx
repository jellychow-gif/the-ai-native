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
import { TopSignals } from "./components/TopSignals";

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
        <div className="observatory-line">
          AI Native Organization Observatory
        </div>
        <p className="subtitle-en">
          Tracking how frontier companies redesign talent, coordination, and
          management in the age of intelligent systems.
        </p>
        <p className="subtitle-zh">
          追踪前沿公司如何在智能系统时代重塑人才、协作与管理。
        </p>
        <p className="masthead-support">
          Built for leaders designing organizations where humans and intelligent
          systems work as one operating model.
        </p>
        <StatStrip />
      </header>

      {/* Top Signals hero — PRD v2 §4 (analyst-feed format) */}
      <TopSignals />

      {/* AI 工具速览 — secondary block, surfaces curated tooling */}
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
