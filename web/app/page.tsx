import { getCandidates, type Section } from "@/lib/db";

const SECTIONS: { key: Section; en: string; zh: string }[] = [
  { key: "Organization", en: "Organization", zh: "组织 · 认知输入" },
  { key: "HR", en: "HR", zh: "HR · 专业输入" },
  { key: "Industry", en: "Industry", zh: "行业 · 行动输入" },
];

// Phase 1 demo values — Step 7 will derive these from the database / publish state.
const ISSUE_NUMBER = "01";
const ISSUE_DATE = "May 15, 2026";
const WEEKLY_OBSERVATION =
  "[本周观察 — 由发起人撰写，每周四晚审核改写。Step 7 接入后此字段从数据库读取。]";

export default async function Home() {
  const items = await getCandidates();

  return (
    <div className="container">
      {/* Masthead */}
      <header className="masthead">
        <div className="meta-top">
          Issue {ISSUE_NUMBER} · {ISSUE_DATE}
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
        <p className="observation-text">{WEEKLY_OBSERVATION}</p>
      </section>

      {/* Three sections */}
      {SECTIONS.map(({ key, en, zh }) => {
        const sectionItems = items.filter((i) => i.section === key);
        return (
          <section key={key} className="section">
            <header className="section-header">
              <h2 className="section-en">{en}</h2>
              <div className="section-zh">{zh}</div>
            </header>

            {sectionItems.length === 0 ? (
              <div className="empty">
                <p>本期暂无入选内容 / Awaiting next week&rsquo;s signals.</p>
              </div>
            ) : (
              sectionItems.map((item) => (
                <article key={item.id} className="signal">
                  {item.sub_tag && (
                    <div className="signal-tag">{item.sub_tag}</div>
                  )}
                  <h3 className="signal-title">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {item.title}
                    </a>
                  </h3>
                  <div className="signal-source">{item.source}</div>
                  {item.summary && (
                    <p className="signal-summary">{item.summary}</p>
                  )}
                  {item.implication && (
                    <div className="implication">
                      <div className="implication-label">
                        对组织变革的含义
                      </div>
                      <p className="implication-text">{item.implication}</p>
                    </div>
                  )}
                  <a
                    className="readmore"
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Read original →
                  </a>
                </article>
              ))
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
