import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

/**
 * Prepare batches to classify ALL matched files as instructional / student / non-id.
 * Provides each file's name, LaCie path, best-known title/author (corrected if an
 * override exists), and cheap deterministic hints. Subagents make the final call.
 */
const ROOT = resolve(process.cwd(), "..");
const map = JSON.parse(readFileSync(resolve(ROOT, "data/file_upload_map.json"), "utf8"));
const overrides: Record<string, { title: string; author: string | null }> = JSON.parse(
  readFileSync(resolve(ROOT, "data/migrate/metadata-overrides.json"), "utf8"),
);

// non-ID course-code patterns (word-ish boundaries to avoid false hits)
const NON_ID = /(\bPA[\s_-]?\d{3}\b|\bBUS[\s_-]?\d|\bSCI[\s_-]?\d|\bINTM\b|\bHUM[\s_-]?\d|\bMBA\b|\bMAX\b|\bEMS\b|stuart)/i;
const STUDENT = /(homework|assignment|submission|portfolio|final[\s_-]?present|deliverable|midterm|\bmy[\s_-]|reflection|student\s*work)/i;

const matched = map.matched as { file_name: string; file_path: string; title: string }[];

const records = matched.map((m) => {
  const ov = overrides[m.file_path];
  return {
    file_name: m.file_name,
    file_path: m.file_path,
    title: ov?.title ?? m.title,
    author: ov?.author ?? null,
    nonIdHint: NON_ID.test(`${m.file_name} ${m.file_path}`),
    studentHint: STUDENT.test(`${m.file_name} ${m.file_path}`),
  };
});

const dir = resolve(ROOT, "data/migrate/classify");
mkdirSync(dir, { recursive: true });
const BATCHES = 12;
const size = Math.ceil(records.length / BATCHES);
for (let i = 0; i < BATCHES; i++) {
  const chunk = records.slice(i * size, (i + 1) * size);
  if (chunk.length) writeFileSync(resolve(dir, `batch-${i}.json`), JSON.stringify(chunk, null, 2));
}

console.log(`total files: ${records.length} → ${BATCHES} batches of ~${size}`);
console.log(`deterministic hints → non-ID: ${records.filter(r=>r.nonIdHint).length}, student: ${records.filter(r=>r.studentHint).length}`);
console.log("non-ID hint samples:");
records.filter(r=>r.nonIdHint).slice(0,12).forEach(r=>console.log(`  ${r.file_name}  (${r.file_path.split("/").slice(-3,-1).join("/")})`));
