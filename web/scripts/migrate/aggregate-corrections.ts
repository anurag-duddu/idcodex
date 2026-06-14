import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(process.cwd(), "..");
const dir = resolve(ROOT, "data/migrate/batches");

type Flagged = { file_name: string; file_path: string; attachedTitle: string; attachedAuthor: string };
type Result = {
  file_name: string;
  sameDocument: boolean;
  correctTitle: string;
  correctAuthor: string | null;
  correctYear: number | null;
  confidence: string;
  source: string;
  note: string;
};

const corrections: (Result & { file_path: string; attachedTitle: string; attachedAuthor: string })[] = [];

for (let n = 0; n < 6; n++) {
  const f: Flagged[] = JSON.parse(readFileSync(resolve(dir, `flagged-${n}.json`), "utf8"));
  const rPath = resolve(dir, `result-${n}.json`);
  if (!existsSync(rPath)) { console.log(`MISSING result-${n}.json`); continue; }
  const r: Result[] = JSON.parse(readFileSync(rPath, "utf8"));
  for (let i = 0; i < f.length; i++) {
    const res = r[i];
    if (!res) { console.log(`batch ${n} idx ${i}: no result for ${f[i].file_name}`); continue; }
    if (res.sameDocument === false) {
      corrections.push({
        ...res,
        file_path: f[i].file_path,
        attachedTitle: f[i].attachedTitle,
        attachedAuthor: f[i].attachedAuthor,
      });
    }
  }
}

// Build overrides keyed by file_path (stable identity → re-migration safe)
const overrides: Record<string, { title: string; author: string | null; year: number | null; note: string }> = {};
for (const c of corrections) {
  overrides[c.file_path] = {
    title: c.correctTitle,
    author: c.correctAuthor ?? null,
    year: c.correctYear ?? null,
    note: c.note,
  };
}
writeFileSync(resolve(ROOT, "data/migrate/metadata-overrides.json"), JSON.stringify(overrides, null, 2));

console.log(`TOTAL genuine mismatches (sameDocument=false): ${corrections.length}`);
console.log(`confidence: high=${corrections.filter(c=>c.confidence==="high").length} med=${corrections.filter(c=>c.confidence==="medium").length} low=${corrections.filter(c=>c.confidence==="low").length}`);
console.log("\n--- corrections (file → corrected title / author) ---");
for (const c of corrections) {
  console.log(`• ${c.file_name}\n    was: "${c.attachedTitle}" / ${c.attachedAuthor || "—"}\n    now: "${c.correctTitle}" / ${c.correctAuthor || "—"}${c.correctYear?` (${c.correctYear})`:""}  [${c.confidence}]`);
}
