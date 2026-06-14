import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(process.cwd(), "..");
const dir = resolve(ROOT, "data/migrate/classify");

type Row = { file_name: string; file_path: string; classification: string; confidence: string; reason: string };

const all: Row[] = [];
for (let i = 0; i < 12; i++) {
  const p = resolve(dir, `result-${i}.json`);
  if (!existsSync(p)) { console.log(`MISSING result-${i}.json`); continue; }
  all.push(...(JSON.parse(readFileSync(p, "utf8")) as Row[]));
}

const counts = { instructional: 0, student: 0, "non-id": 0, other: 0 } as Record<string, number>;
for (const r of all) counts[r.classification] = (counts[r.classification] ?? 0) + 1;

const exclusions = all.filter((r) => r.classification === "student" || r.classification === "non-id");
writeFileSync(
  resolve(ROOT, "data/migrate/exclusions.json"),
  JSON.stringify(exclusions.map((r) => ({ file_path: r.file_path, file_name: r.file_name, classification: r.classification, reason: r.reason })), null, 2),
);

const overrides = JSON.parse(readFileSync(resolve(ROOT, "data/migrate/metadata-overrides.json"), "utf8"));
const exclPaths = new Set(exclusions.map((r) => r.file_path));
const overridePaths = Object.keys(overrides);
const overridesOnKept = overridePaths.filter((p) => !exclPaths.has(p));
const overridesMooted = overridePaths.filter((p) => exclPaths.has(p));

console.log("classified:", all.length, counts);
console.log("low-confidence:", all.filter((r) => r.confidence === "low").length);
console.log(`EXCLUSIONS: ${exclusions.length} (student=${counts.student}, non-id=${counts["non-id"]})`);
console.log(`metadata overrides: ${overridePaths.length} total → ${overridesOnKept.length} apply to KEPT files, ${overridesMooted.length} moot (file excluded)`);
console.log("\n--- NON-ID (exclude) ---");
exclusions.filter((r) => r.classification === "non-id").forEach((r) => console.log(`  ${r.file_name} — ${r.reason}`));
console.log("\n--- STUDENT (exclude) ---");
exclusions.filter((r) => r.classification === "student").forEach((r) => console.log(`  ${r.file_name} — ${r.reason}`));
