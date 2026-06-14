import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(process.cwd(), "..");
const audit = JSON.parse(readFileSync(resolve(ROOT, "data/migrate/metadata-audit.json"), "utf8"));
const xp = JSON.parse(readFileSync(resolve(ROOT, "data/migrate/export.json"), "utf8"));

const authorByPage = new Map<string, string>();
for (const r of xp.resources) authorByPage.set(r.notionId, r.authors || "");

type Row = {
  page_id: string;
  file_name: string;
  file_path: string;
  attachedTitle: string;
  attachedType: string;
  match_score: number;
  sim: number;
  kind: string;
  verdict: string;
};

const enrich = (r: Row) => ({
  file_name: r.file_name,
  file_path: r.file_path,
  attachedTitle: r.attachedTitle,
  attachedAuthor: authorByPage.get(r.page_id) || "",
  attachedType: r.attachedType,
  match_score: r.match_score,
  sim: r.sim,
  filenameKind: r.kind,
  fileExists: existsSync(r.file_path),
});

const flagged = (audit.rows as Row[]).filter((r) => r.verdict !== "ok").map(enrich);
const ok = (audit.rows as Row[]).filter((r) => r.verdict === "ok");

const dir = resolve(ROOT, "data/migrate/batches");
mkdirSync(dir, { recursive: true });

const N = 6;
const size = Math.ceil(flagged.length / N);
for (let i = 0; i < N; i++) {
  const chunk = flagged.slice(i * size, (i + 1) * size);
  writeFileSync(resolve(dir, `flagged-${i}.json`), JSON.stringify(chunk, null, 2));
}

// control sample of the "ok" set: every Nth row, ~40 items
const step = Math.max(1, Math.floor(ok.length / 40));
const sample = ok.filter((_, i) => i % step === 0).slice(0, 40).map(enrich);
writeFileSync(resolve(dir, "ok-sample.json"), JSON.stringify(sample, null, 2));

console.log(`flagged: ${flagged.length} → ${N} batches of ~${size}`);
console.log(`ok control sample: ${sample.length}`);
const cross = flagged.find((f) => /cross/i.test(f.file_name));
console.log("Cross file present in flagged?", cross ? `YES → "${cross.attachedTitle}" / ${cross.attachedAuthor}` : "no");
console.log("missing-on-disk in flagged:", flagged.filter((f) => !f.fileExists).length);
