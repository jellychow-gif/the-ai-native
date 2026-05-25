import Link from "next/link";
import { getAllIssues } from "@/lib/db";

export const metadata = {
  title: "Issues · The AI Native",
  description:
    "All frozen weekly issues of The AI Native — Organization Observatory.",
};

/**
 * Issues archive — chronological list of every frozen weekly issue.
 * Each issue is permanent (its 9 signals stay bound forever), so this
 * is the canonical place to find Issue 03 / 04 / 05 etc. for sharing.
 */
export default function IssuesArchivePage() {
  const issues = getAllIssues();

  return (
    <div className="container">
      <header className="section-page-header">
        <div className="meta-top">归档 / Issue Archive</div>
        <h1 className="title">Issues</h1>
        <p className="subtitle-zh">
          每周五早 8 点凝固一期·永久 URL 可分享·历史 Issue 不被未来抓取覆盖。
        </p>
        <div className="update-promise">
          {issues.length} {issues.length === 1 ? "issue" : "issues"} frozen
        </div>
      </header>

      {issues.length === 0 ? (
        <div className="empty">
          <p>暂无凝固 Issue / No issues yet.</p>
        </div>
      ) : (
        <ol className="issues-list">
          {issues.map((iss) => (
            <li key={iss.number} className="issues-item">
              <Link href={`/issues/${iss.number}`} className="issues-link">
                <span className="issues-num">
                  Issue {String(iss.number).padStart(2, "0")}
                </span>
                <span className="issues-date">{iss.date_label}</span>
                <span className="issues-count">
                  {iss.item_count} signals
                </span>
              </Link>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
