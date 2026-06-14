import "dotenv/config";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

/**
 * Joins the Notion export (resources + their course relations) with
 * file_upload_map.json (resource → LaCie file path) to plan, per course, which
 * files to upload. v1 places files flat under each course (subfolders from
 * LaCie paths are a future enhancement). Pure planning — no R2, no DB.
 */

const ROOT = resolve(process.cwd(), "..");
const exportPath = resolve(ROOT, "data/migrate/export.json");
const mapPath = resolve(ROOT, "data/file_upload_map.json");

type Matched = {
  page_id: string;
  title: string;
  type: string;
  file_path: string;
  file_name: string;
};

function mapResourceType(t: string | null): string {
  const known = ["Paper", "Slide Deck", "Book", "Article", "Tool", "PDF"];
  if (t && known.includes(t)) return t;
  if (t === "Video") return "Other";
  if (t === "Link") return "Tool";
  return "Other";
}

function main() {
  const xp = JSON.parse(readFileSync(exportPath, "utf8"));
  const map = JSON.parse(readFileSync(mapPath, "utf8"));
  const matched: Matched[] = map.matched ?? [];

  // resource notionId -> file
  const fileByResource = new Map<string, Matched>();
  for (const m of matched) fileByResource.set(m.page_id, m);

  const courseById = new Map<string, (typeof xp.courses)[number]>();
  for (const c of xp.courses) courseById.set(c.notionId, c);

  // courseNotionId -> files[]
  const plan = new Map<
    string,
    {
      resourceNotionId: string;
      title: string;
      fileName: string;
      filePath: string;
      resourceType: string;
      author: string | null;
      exists: boolean;
    }[]
  >();

  let placements = 0;
  let resWithCourseNoFile = 0;
  let missingOnDisk = 0;

  for (const r of xp.resources) {
    const file = fileByResource.get(r.notionId);
    if (!file) {
      if (r.courseNotionIds.length) resWithCourseNoFile++;
      continue;
    }
    const exists = existsSync(file.file_path);
    if (!exists) missingOnDisk++;
    for (const cid of r.courseNotionIds) {
      if (!courseById.has(cid)) continue;
      const list = plan.get(cid) ?? [];
      list.push({
        resourceNotionId: r.notionId,
        title: r.title,
        fileName: file.file_name,
        filePath: file.file_path,
        resourceType: mapResourceType(r.type),
        author: r.authors || null,
        exists,
      });
      plan.set(cid, list);
      placements++;
    }
  }

  // Serialize plan keyed by course slug for readability
  const planOut: Record<string, unknown> = {};
  for (const [cid, files] of plan) {
    const c = courseById.get(cid)!;
    planOut[c.slug] = {
      courseName: c.name,
      type: c.type,
      fileCount: files.length,
      files,
    };
  }

  const outPath = resolve(ROOT, "data/migrate/plan.json");
  writeFileSync(
    outPath,
    JSON.stringify(
      { generatedAt: new Date().toISOString(), plan: planOut },
      null,
      2,
    ),
  );

  const coursesWithFiles = plan.size;
  console.log("DONE →", outPath);
  console.log({
    coursesWithFiles,
    totalCourses: xp.courses.length,
    filePlacements: placements,
    resourcesWithCourseButNoFile: resWithCourseNoFile,
    filesMissingOnDisk: missingOnDisk,
    laCieMounted: existsSync("/Volumes/LaCie"),
  });
  // top 5 courses by file count
  const top = Object.entries(planOut)
    .sort((a, b) => (b[1] as { fileCount: number }).fileCount - (a[1] as { fileCount: number }).fileCount)
    .slice(0, 5)
    .map(([slug, v]) => `${slug}: ${(v as { fileCount: number }).fileCount}`);
  console.log("top courses by files:", top);
}

main();
