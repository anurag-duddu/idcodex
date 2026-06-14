// Minimal Notion REST client (fetch-based) for the one-time migration export.
const KEY = process.env.NOTION_API_KEY;
const NV = "2022-06-28";
const BASE = "https://api.notion.com/v1";

function headers() {
  if (!KEY) throw new Error("NOTION_API_KEY not set");
  return {
    Authorization: `Bearer ${KEY}`,
    "Notion-Version": NV,
    "Content-Type": "application/json",
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Json = any;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** fetch with 429 backoff (Notion rate-limits ~3 req/s). */
async function napi(url: string, init?: RequestInit): Promise<Json> {
  for (let attempt = 0; attempt < 6; attempt++) {
    const res = await fetch(url, init);
    if (res.status === 429) {
      const wait = Number(res.headers.get("retry-after") ?? "1") * 1000 || 1000;
      await sleep(wait);
      continue;
    }
    if (!res.ok) throw new Error(`Notion ${url}: ${res.status} ${await res.text()}`);
    return res.json();
  }
  throw new Error(`Notion ${url}: rate-limited after retries`);
}

/** All pages of a database (handles pagination). */
export async function queryDatabase(databaseId: string): Promise<Json[]> {
  const out: Json[] = [];
  let cursor: string | undefined;
  do {
    const data = await napi(`${BASE}/databases/${databaseId}/query`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(
        cursor ? { start_cursor: cursor, page_size: 100 } : { page_size: 100 },
      ),
    });
    out.push(...data.results);
    cursor = data.has_more ? data.next_cursor : undefined;
  } while (cursor);
  return out;
}

/** Top-level block children of a page (handles pagination). */
export async function getBlocks(pageId: string): Promise<Json[]> {
  const out: Json[] = [];
  let cursor: string | undefined;
  do {
    const url = new URL(`${BASE}/blocks/${pageId}/children`);
    url.searchParams.set("page_size", "100");
    if (cursor) url.searchParams.set("start_cursor", cursor);
    const data = await napi(url.toString(), { headers: headers() });
    out.push(...data.results);
    cursor = data.has_more ? data.next_cursor : undefined;
  } while (cursor);
  return out;
}

/* ── Property extractors ─────────────────────────────────────────── */
const rich = (arr: Json[] | undefined): string =>
  (arr ?? []).map((t) => t.plain_text).join("").trim();

export const props = {
  title: (p: Json, name: string): string => rich(p.properties?.[name]?.title),
  text: (p: Json, name: string): string => rich(p.properties?.[name]?.rich_text),
  number: (p: Json, name: string): number | null =>
    p.properties?.[name]?.number ?? null,
  select: (p: Json, name: string): string | null =>
    p.properties?.[name]?.select?.name ?? null,
  multi: (p: Json, name: string): string[] =>
    (p.properties?.[name]?.multi_select ?? []).map((s: Json) => s.name),
  url: (p: Json, name: string): string | null => p.properties?.[name]?.url ?? null,
  email: (p: Json, name: string): string | null =>
    p.properties?.[name]?.email ?? null,
  relationIds: (p: Json, name: string): string[] =>
    (p.properties?.[name]?.relation ?? []).map((r: Json) => r.id),
  files: (p: Json, name: string): { name: string; url: string }[] =>
    (p.properties?.[name]?.files ?? []).map((f: Json) => ({
      name: f.name,
      url: f.type === "external" ? f.external?.url : f.file?.url,
    })),
};

/** Plain text of a block (paragraph/heading/list item). */
export function blockText(b: Json): string {
  const t = b.type;
  const node = b[t];
  if (node?.rich_text) return rich(node.rich_text);
  return "";
}
