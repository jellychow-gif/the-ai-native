import { getCandidates, getIssue, SECTION_META, type Section } from "@/lib/db";
import { Signal } from "./components/Signal";

const SECTION_ORDER: Section[] = ["Organization", "HR", "Industry"];

export default async function Home() {
  const items = getCandidates();
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
        <div className="update-promise">
          每周五早上 8:00 更新 · Updates every Friday at 8 AM
        </div>
      </header>

      {/* 本周观察 — Editor-written segment per PRD §5.5 / §6.1 */}
      <section className="observation">
        <div className="observation-label">本周观察 / This week</div>
        <p className="observation-text">{issue.observation}</p>
      </section>

      {/* Three sections, with this issue's selected signals */}
      {SECTION_ORDER.map((key) => {
        const meta = SECTION_META[key];
        const sectionItems = items.filter((i) => i.section === key);
        return (
          <section key={key} className={`section section--${key.toLowerCase()}`}>
            <header className="section-header">
              <h2 className="section-en">{meta.en}</h2>
              <div className="section-zh">{meta.zh}</div>
            </header>

            {sectionItems.length === 0 ? (
              <div className="empty">
                <p>本期暂无入选内容 / Awaiting next week&rsquo;s signals.</p>
              </div>
            ) : (
              sectionItems.map((item) => <Signal key={item.id} item={item} />)
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
