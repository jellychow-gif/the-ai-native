import { getIssue } from "@/lib/db";

export const metadata = {
  title: "Observations · The AI Native",
  description: "All weekly observations — the founder's running judgment.",
};

/**
 * Observations archive per PRD §6.1.
 * Phase 1 shows the current issue's observation. Once weekly issues
 * accumulate (Step 7+), this becomes a chronological feed of every
 * "本周观察" segment — the founder's continuous editorial archive.
 */
export default function ObservationsPage() {
  const issue = getIssue();

  return (
    <div className="container">
      <header className="section-page-header">
        <div className="meta-top">观察归档 / Editorial Archive</div>
        <h1 className="title">Observations</h1>
        <p className="subtitle-zh">
          每周一段 150 字的判断输出。匿名，但语气本身即署名。
        </p>
      </header>

      <article className="observation observation-archive-item">
        <div className="observation-label">
          Issue {issue.number} · {issue.date_label}
        </div>
        <p className="observation-text">{issue.observation}</p>
      </article>

      <div className="empty">
        <p>
          更多历史观察将在 Step 7 接入后逐周累积。 / More archived
          observations will accumulate weekly.
        </p>
      </div>
    </div>
  );
}
