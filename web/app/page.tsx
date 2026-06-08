import Link from "next/link";
import {
  getCurrentIssue,
  getFeatured,
  getBySection,
  loadPayload,
  SECTION_META,
  type Section,
} from "@/lib/db";
import { Signal } from "./components/Signal";
import { StatStrip } from "./components/StatStrip";
import { TopSignals } from "./components/TopSignals";

const SECTION_ORDER: Section[] = ["Organization", "HR", "Industry"];

/** Data-last-updated stamp for the masthead, sourced from items.json's
 *  `generated_at` (set every time export.py runs — daily via pipeline).
 *  This makes the "Latest update" line semantically truthful: it shows
 *  when the data was last refreshed, not when the browser is visiting. */
function lastUpdateInBeijing(): string {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const isoUtc = loadPayload().generated_at;
  const utc = new Date(isoUtc);
  // Convert UTC → BJT (UTC+8)
  const bjt = new Date(utc.getTime() + 8 * 60 * 60 * 1000);
  return `${months[bjt.getUTCMonth()]} ${bjt.getUTCDate()}, ${bjt.getUTCFullYear()}`;
}

export default async function Home() {
  const currentIssue = getCurrentIssue();
  const todayLabel = lastUpdateInBeijing();

  return (
    <div className="container">
      {/* Masthead — emphasizes "today" not Issue NN. Issue archive
          accessible via the explicit link at bottom + top nav. */}
      <header className="masthead">
        <div className="meta-top">
          Latest update · {todayLabel} BJT
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
        {currentIssue && (
          <Link
            href={`/issues/${currentIssue.number}`}
            className="masthead-issues-link"
          >
            📜 Latest weekly snapshot · Issue {String(currentIssue.number).padStart(2, "0")} · {currentIssue.date_label} →
          </Link>
        )}
      </header>

      {/* Top Signals hero — current freshest 5, refreshed daily by pipeline */}
      <TopSignals />

      {/* Per-section blocks now show CURRENT featured (not issue-bound).
          Refreshed daily as new content gets scored + summarized.
          Issue NN pages still hold permanent weekly snapshots. */}
      {SECTION_ORDER.map((key) => {
        const meta = SECTION_META[key];
        const featured = getFeatured(key);
        const totalInSection = getBySection(key).length;
        const path = `/${key.toLowerCase()}`;

        return (
          <section key={key} className={`section section--${key.toLowerCase()}`}>
            <header className="section-header">
              <h2 className="section-en">{meta.en}</h2>
              <div className="section-zh">{meta.zh}</div>
            </header>

            {featured.length === 0 ? (
              <div className="empty">
                <p>本板块暂无新精选 / Awaiting fresh signals.</p>
              </div>
            ) : (
              featured.map((item) => <Signal key={item.id} item={item} />)
            )}

            {totalInSection > featured.length && (
              <Link href={path} className="section-archive-link">
                查看 {key} 全部 {totalInSection} 条 →
              </Link>
            )}
          </section>
        );
      })}

      <footer className="site-footer">
        <p>
          A daily signal layer for leaders rebuilding their organizations
          around AI. Weekly snapshots archived as Issues.
        </p>
      </footer>
    </div>
  );
}
