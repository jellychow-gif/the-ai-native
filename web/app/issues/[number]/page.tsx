import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getAllIssues,
  getIssueByNumber,
  getIssueItems,
  SECTION_META,
  type Section,
} from "@/lib/db";
import { Signal } from "../../components/Signal";

const SECTION_ORDER: Section[] = ["Organization", "HR", "Industry"];

export function generateStaticParams() {
  return getAllIssues().map((iss) => ({ number: String(iss.number) }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ number: string }>;
}) {
  const { number } = await params;
  const n = parseInt(number, 10);
  const issue = getIssueByNumber(n);
  if (!issue) return { title: "Issue not found · The AI Native" };
  return {
    title: `Issue ${String(issue.number).padStart(2, "0")} · The AI Native`,
    description: `${issue.item_count} signals frozen on ${issue.date_label}`,
  };
}

/**
 * Permanent per-issue page — Issue 0X URLs that never mutate.
 * This is the canonical "share this issue" surface (PRD §1.2 second goal).
 */
export default async function IssuePage({
  params,
}: {
  params: Promise<{ number: string }>;
}) {
  const { number } = await params;
  const n = parseInt(number, 10);
  if (isNaN(n)) notFound();

  const issue = getIssueByNumber(n);
  if (!issue) notFound();

  const items = getIssueItems(n);

  return (
    <div className="container">
      <header className="section-page-header">
        <div className="meta-top">
          Issue {String(issue.number).padStart(2, "0")} · {issue.date_label}
        </div>
        <h1 className="title">Issue {String(issue.number).padStart(2, "0")}</h1>
        <p className="subtitle-zh">
          {issue.item_count} signals · frozen {issue.frozen_at.slice(0, 10)} · permanent URL
        </p>
        <Link href="/issues" className="masthead-issues-link">
          ← All issues
        </Link>
      </header>

      {SECTION_ORDER.map((key) => {
        const inSection = items.filter((i) => i.section === key);
        if (inSection.length === 0) return null;
        const meta = SECTION_META[key];
        return (
          <section key={key} className={`section section--${key.toLowerCase()}`}>
            <header className="section-header">
              <h2 className="section-en">{meta.en}</h2>
              <div className="section-zh">{meta.zh}</div>
            </header>
            {inSection.map((item) => (
              <Signal key={item.id} item={item} />
            ))}
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
