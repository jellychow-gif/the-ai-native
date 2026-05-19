/**
 * Build-time SQLite reader for The AI Native.
 *
 * The Python pipeline writes to `<project-root>/data/items.db`.
 * Next.js server components import from here to render pages.
 */
import Database from "better-sqlite3";
import path from "node:path";

export type Section = "Organization" | "HR" | "Industry";

export type Item = {
  id: number;
  url: string;
  title: string;
  source: string;
  source_type: string;
  section: Section | null;
  sub_tag: string | null;
  hook: string | null;
  summary: string | null;
  implication: string | null;
  author: string | null;
  published_at: string | null;
  perspective_score: number | null;
  practice_score: number | null;
  frontier_score: number | null;
  score_reasoning: string | null;
  total_score: number;
};

const MIN_SCORE = 9; // PRD §5.3 threshold

function dbPath(): string {
  // `next dev` runs with cwd = `web/`. The db file is one level up.
  return path.resolve(process.cwd(), "..", "data", "items.db");
}

/** Items that have passed the score threshold AND have a summary. */
export function getCandidates(): Item[] {
  const db = new Database(dbPath(), { readonly: true, fileMustExist: true });
  try {
    return db
      .prepare(
        `
        SELECT
          id, url, title, source, source_type, section,
          sub_tag, hook, summary, implication,
          author, published_at,
          perspective_score, practice_score, frontier_score, score_reasoning,
          COALESCE(perspective_score, 0)
            + COALESCE(practice_score, 0)
            + COALESCE(frontier_score, 0) AS total_score
        FROM items
        WHERE perspective_score IS NOT NULL
          AND (perspective_score + practice_score + frontier_score) >= ?
          AND summary IS NOT NULL
        ORDER BY total_score DESC, id DESC
        `
      )
      .all(MIN_SCORE) as Item[];
  } finally {
    db.close();
  }
}
