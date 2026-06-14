import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

/**
 * Read-only audit: for each matched file, compare the FILENAME (authoritative
 * identity of the file) against the attached Notion Resource title/author that
 * the migration copied onto it. Buckets each file so we know the true scope of
 * metadata mismatches before changing anything.
 */

const ROOT = resolve(process.cwd(), "..");
const map = JSON.parse(readFileSync(resolve(ROOT, "data/file_upload_map.json"), "utf8"));

const STOP = new Set([
  "the", "and", "for", "with", "from", "this", "that", "are", "was",
  "pdf", "eng", "final", "draft", "copy", "version", "ch", "chapter", "part",
]);

function tokens(s: string): string[] {
  return (s || "")
    .toLowerCase()
    .replace(/\.[a-z0-9]{1,5}$/i, "")
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 3 && !STOP.has(t));
}

function jaccard(a: string[], b: string[]): number {
  const A = new Set(a), B = new Set(b);
  if (A.size === 0 || B.size === 0) return 0;
  let inter = 0;
  for (const x of A) if (B.has(x)) inter++;
  return inter / (A.size + B.size - inter);
}

function titleContainment(titleT: string[], fileT: string[]): number {
  if (titleT.length === 0) return 0;
  const F = new Set(fileT);
  let inter = 0;
  for (const t of new Set(titleT)) if (F.has(t)) inter++;
  return inter / new Set(titleT).size;
}

// classify a filename as opaque (code/id, no human-readable title) vs descriptive
function filenameKind(file: string): "opaque" | "descriptive" {
  const base = file.replace(/\.[a-z0-9]{1,5}$/i, "");
  const letters = (base.match(/[a-z]/gi) || []).length;
  const words = tokens(base).length;
  if (/^\d{9,13}$/.test(base)) return "opaque"; // ISBN/code
  if (/journal\.[a-z]+\.\d+/i.test(base)) return "opaque"; // DOI-ish (PLOS etc.)
  if (/^10\.\d{4,}/.test(base)) return "opaque"; // DOI
  if (/^[A-Z0-9]{5,}-PDF-ENG/i.test(base)) return "opaque"; // HBR case
  if (/^[a-z0-9]{6,}$/i.test(base) && words <= 1) return "opaque"; // single token code
  if (letters < 6 || words < 2) return "opaque";
  return "descriptive";
}

const matched = map.matched as {
  page_id: string;
  title: string;
  type: string;
  file_path: string;
  file_name: string;
  match_type: string;
  match_score: number;
}[];

const rows = matched.map((m) => {
  const fileT = tokens(m.file_name);
  const titleT = tokens(m.title);
  const jac = jaccard(fileT, titleT);
  const cont = titleContainment(titleT, fileT);
  const sim = Math.max(jac, cont);
  const kind = filenameKind(m.file_name);
  let verdict: string;
  if (m.match_type === "exact" || m.match_score >= 0.95 || sim >= 0.55) verdict = "ok";
  else if (kind === "descriptive") verdict = "fix-from-filename";
  else verdict = "needs-investigation";
  return {
    page_id: m.page_id,
    file_name: m.file_name,
    file_path: m.file_path,
    attachedTitle: m.title,
    attachedType: m.type,
    match_type: m.match_type,
    match_score: Math.round(m.match_score * 100) / 100,
    sim: Math.round(sim * 100) / 100,
    kind,
    verdict,
  };
});

const by = (k: string) => rows.filter((r) => r.verdict === k);
const summary = {
  total: rows.length,
  ok: by("ok").length,
  fixFromFilename: by("fix-from-filename").length,
  needsInvestigation: by("needs-investigation").length,
  exactMatches: rows.filter((r) => r.match_type === "exact").length,
  scoreBuckets: {
    "1.0": rows.filter((r) => r.match_score >= 0.95).length,
    "0.7-0.95": rows.filter((r) => r.match_score >= 0.7 && r.match_score < 0.95).length,
    "0.5-0.7": rows.filter((r) => r.match_score >= 0.5 && r.match_score < 0.7).length,
    "<0.5": rows.filter((r) => r.match_score < 0.5).length,
  },
};

writeFileSync(
  resolve(ROOT, "data/migrate/metadata-audit.json"),
  JSON.stringify({ generatedAt: new Date().toISOString(), summary, rows }, null, 2),
);

console.log("SUMMARY:", JSON.stringify(summary, null, 2));
console.log("\n--- sample fix-from-filename (descriptive filename ≠ attached title) ---");
by("fix-from-filename").slice(0, 12).forEach((r) =>
  console.log(`  [sim ${r.sim} score ${r.match_score}] ${r.file_name}\n      attached: "${r.attachedTitle}"`),
);
console.log("\n--- sample needs-investigation (opaque filename) ---");
by("needs-investigation").slice(0, 12).forEach((r) =>
  console.log(`  [${r.kind}] ${r.file_name}  attached: "${r.attachedTitle}"`),
);
