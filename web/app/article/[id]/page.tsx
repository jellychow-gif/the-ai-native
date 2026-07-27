import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getAllItems,
  ANO_DIMENSION_LABELS,
} from "@/lib/db";

/**
 * Long-form article page (v5 LaterCast pivot).
 *
 * The card grid on section pages and the homepage is a discovery layer;
 * this page is where a CHRO actually reads the piece. Renders the
 * 2500-3500 char Chinese narrative produced by scripts/summarize.py,
 * with paragraph breaks preserved and pull-quotes (「」) styled.
 */
export function generateStaticParams() {
  return getAllItems()
    .filter((i) => i.long_form_zh)
    .map((i) => ({ id: String(i.id) }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const n = parseInt(id, 10);
  const item = getAllItems().find((i) => i.id === n);
  if (!item) return { title: "Article not found · The AI Native" };
  return {
    title: `${item.title} · The AI Native`,
    description: item.preview_hook ?? item.what_happened ?? undefined,
  };
}

function formatPublishedDate(iso: string | null): string | null {
  if (!iso) return null;
  const d = new Date(iso);
  if (isNaN(d.getTime())) return null;
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const n = parseInt(id, 10);
  if (isNaN(n)) notFound();

  const item = getAllItems().find((i) => i.id === n);
  if (!item || !item.long_form_zh) notFound();

  const dateLabel = formatPublishedDate(item.published_at);
  const paragraphs = item.long_form_zh.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);

  return (
    <div className="container article-container">
      <header className="article-header">
        <Link href="/" className="article-back">← Home</Link>

        <div className="article-eyebrow">
          {item.ano_dimension && (
            <span className="insight-chip" title={ANO_DIMENSION_LABELS[item.ano_dimension]}>
              {item.ano_dimension}
              <span className="insight-chip-zh">{ANO_DIMENSION_LABELS[item.ano_dimension]}</span>
            </span>
          )}
          {item.sub_tag && <span className="signal-tag">{item.sub_tag}</span>}
        </div>

        <h1 className="article-title">{item.title}</h1>

        <div className="article-meta">
          <span className="article-source">{item.source}</span>
          {dateLabel && (
            <>
              <span>·</span>
              <time dateTime={item.published_at ?? undefined}>{dateLabel}</time>
            </>
          )}
        </div>
      </header>

      <article className="article-body">
        {paragraphs.map((p, i) => {
          // Pull-quote detection: paragraph is a single 「」-wrapped sentence
          const isPullQuote = /^「.+」$/.test(p.replace(/\s/g, ""));
          if (isPullQuote) {
            return (
              <blockquote key={i} className="article-pullquote">
                {p}
              </blockquote>
            );
          }
          // 写在最后 section — bolder treatment
          if (p.startsWith("写在最后") || p.startsWith("**写在最后**")) {
            return (
              <h2 key={i} className="article-h2">写在最后</h2>
            );
          }
          return <p key={i}>{p}</p>;
        })}
      </article>

      <footer className="article-footer">
        <p className="article-source-line">
          原始来源：
          <a href={item.url} target="_blank" rel="noopener noreferrer">
            {item.source} — {item.title} ↗
          </a>
        </p>
      </footer>
    </div>
  );
}
