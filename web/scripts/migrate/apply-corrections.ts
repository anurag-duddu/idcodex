import "dotenv/config";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { eq } from "drizzle-orm";
import { S3Client, DeleteObjectCommand } from "@aws-sdk/client-s3";
import { db } from "@/db/client";
import { courses, nodes } from "@/db/schema";

/**
 * Targeted remediation of the CURRENT db + R2 (no full re-migration):
 *  - delete nodes (and their R2 objects) for excluded files (student / non-id)
 *  - update title(description)/author/year for kept files with corrections
 * Maps each db node back to its source file_path via plan.json.
 *
 * Run: npx tsx scripts/migrate/apply-corrections.ts          (dry run)
 *      npx tsx scripts/migrate/apply-corrections.ts --confirm (execute)
 */
const ROOT = resolve(process.cwd(), "..");
const CONFIRM = process.argv.includes("--confirm");

const exclusions = new Set<string>(
  (JSON.parse(readFileSync(resolve(ROOT, "data/migrate/exclusions.json"), "utf8")) as { file_path: string }[]).map((e) => e.file_path),
);
const overrides: Record<string, { title: string; author: string | null; year: number | null }> = JSON.parse(
  readFileSync(resolve(ROOT, "data/migrate/metadata-overrides.json"), "utf8"),
);
const planDoc = JSON.parse(readFileSync(resolve(ROOT, "data/migrate/plan.json"), "utf8"));

// (courseSlug -> fileName -> [{filePath, title}])
const bridge = new Map<string, Map<string, { filePath: string; title: string }[]>>();
for (const [slug, entry] of Object.entries<{ files: { fileName: string; filePath: string; title: string }[] }>(planDoc.plan)) {
  const m = new Map<string, { filePath: string; title: string }[]>();
  for (const f of entry.files) {
    const arr = m.get(f.fileName) ?? [];
    arr.push({ filePath: f.filePath, title: f.title });
    m.set(f.fileName, arr);
  }
  bridge.set(slug, m);
}

const s3 = new S3Client({
  region: "auto",
  endpoint: process.env.R2_ENDPOINT ?? `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: { accessKeyId: process.env.R2_ACCESS_KEY_ID!, secretAccessKey: process.env.R2_SECRET_ACCESS_KEY! },
});

async function main() {
  const rows = await db
    .select({
      id: nodes.id,
      name: nodes.name,
      description: nodes.description,
      storageKey: nodes.storageKey,
      slug: courses.slug,
    })
    .from(nodes)
    .innerJoin(courses, eq(nodes.courseId, courses.id))
    .where(eq(nodes.kind, "file"));

  const toDelete: { id: string; key: string; name: string }[] = [];
  const toUpdate: { id: string; name: string; title: string; author: string | null; year: number | null }[] = [];
  let unmapped = 0;

  for (const r of rows) {
    const cands = bridge.get(r.slug)?.get(r.name);
    if (!cands || cands.length === 0) { unmapped++; continue; }
    let chosen = cands[0];
    if (cands.length > 1) {
      chosen = cands.find((c) => c.title === r.description || (c.title === r.name && r.description === null)) ?? cands[0];
    }
    const fp = chosen.filePath;
    if (exclusions.has(fp)) {
      toDelete.push({ id: r.id, key: r.storageKey!, name: r.name });
    } else if (overrides[fp]) {
      const o = overrides[fp];
      toUpdate.push({ id: r.id, name: r.name, title: o.title, author: o.author, year: o.year });
    }
  }

  console.log(`file nodes: ${rows.length} | unmapped: ${unmapped}`);
  console.log(`TO DELETE (excluded): ${toDelete.length} nodes`);
  console.log(`TO UPDATE (corrections): ${toUpdate.length} nodes`);
  if (!CONFIRM) {
    console.log("\n[dry run] sample deletes:", toDelete.slice(0, 5).map((d) => d.name));
    console.log("[dry run] sample updates:", toUpdate.slice(0, 5).map((u) => `${u.name} → "${u.title}"`));
    console.log("\nRe-run with --confirm to execute.");
    return;
  }

  let r2deleted = 0;
  for (const d of toDelete) {
    try { await s3.send(new DeleteObjectCommand({ Bucket: process.env.R2_BUCKET!, Key: d.key })); r2deleted++; } catch (e) { console.error("R2 del failed", d.key, (e as Error).name); }
    await db.delete(nodes).where(eq(nodes.id, d.id));
  }
  for (const u of toUpdate) {
    await db.update(nodes).set({ description: u.title, author: u.author, year: u.year }).where(eq(nodes.id, u.id));
  }
  console.log(`DONE — deleted ${toDelete.length} nodes (${r2deleted} R2 objects), updated ${toUpdate.length} nodes.`);
}

main().then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); });
