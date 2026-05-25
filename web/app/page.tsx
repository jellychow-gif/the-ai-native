import Link from "next/link";
import {
  getCurrentIssue,
  getIssueItems,
  getBySection,
  getIssue,
  SECTION_META,
  type Section,
  type Item,
} from "@/lib/db";
import { Signal } from "./components/Signal";
import { StatStrip } from "./components/StatStrip";
import { TopSignals } from "./components/TopSignals";

const SECTION_ORDER: Section[] = ["Organization", "HR", "Industry"];

export default async function Home() {
  const issue = getIssue();
  const currentIssue = getCurrentIssue();
  // Items bound to the latest frozen issue (homepage shows current issue only,
  // per Issue 化 design). Section archives still hold the full historical pool.
  const issueItems: Item[] = currentIssue ? getIssueItems(currentIssue.number) : [];

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
        <Link href="/issues" className="masthead-issues-link">
          View all issues →
        </Link>
      </header>

      {/* Top Signals hero — PRD v2 §4 (analyst-feed format). */}
      <TopSignals />

      {/* Three sections showing this issue's frozen picks per section.
          Section archive pages hold the full historical pool. */}
      {SECTION_ORDER.map((key) => {
        const meta = SECTION_META[key];
        const inIssue = issueItems.filter((i) => i.section === key);
        const totalInSection = getBySection(key).length;
        const path = `/${key.toLowerCase()}`;

        return (
          <section key={key} className={`section section--${key.toLowerCase()}`}>
            <header className="section-header">
              <h2 className="section-en">{meta.en}</h2>
              <div className="section-zh">{meta.zh}</div>
            </header>

            {inIssue.length === 0 ? (
              <div className="empty">
                <p>本期暂无入选内容 / Awaiting next week&rsquo;s signals.</p>
              </div>
            ) : (
              inIssue.map((item) => <Signal key={item.id} item={item} />)
            )}

            {totalInSection > inIssue.length && (
              <Link href={path} className="section-archive-link">
                查看 {key} 全部 {totalInSection} 条历史归档 →
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
