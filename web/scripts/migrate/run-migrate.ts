import "dotenv/config";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { METADATA_OVERRIDES, toArchiveRelative } from "./corrections-data";
import { randomUUID } from "node:crypto";
import { inArray } from "drizzle-orm";
import { db } from "@/db/client";
import {
  programs,
  people,
  courses,
  coursePeople,
  coursePrograms,
  nodes,
} from "@/db/schema";
import { isR2Configured, uploadToR2, existsInR2 } from "@/lib/r2";
import { previewTypeFor } from "@/lib/preview";
import { slugify, uniqueSlug } from "@/lib/slug";

/**
 * Real migration: Notion export + planned LaCie files → Neon + R2.
 * Idempotent on content tables (clears programs/people/courses + cascade;
 * NEVER touches users/auth). Requires R2 keys + LaCie mounted.
 *
 * Run:  npx tsx scripts/migrate/run-migrate.ts --confirm
 */

const ROOT = resolve(process.cwd(), "..");

function mimeByExt(name: string): string {
  const e = name.toLowerCase().split(".").pop() ?? "";
  const m: Record<string, string> = {
    pdf: "application/pdf",
    png: "image/png",
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    gif: "image/gif",
    webp: "image/webp",
    tiff: "image/tiff",
    heic: "image/heic",
    mp4: "video/mp4",
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    doc: "application/msword",
    ppt: "application/vnd.ms-powerpoint",
  };
  return m[e] ?? "application/octet-stream";
}

async function main() {
  if (!process.argv.includes("--confirm")) {
    console.log(
      "Refusing to run without --confirm (this clears content tables). " +
        "Run: npx tsx scripts/migrate/run-migrate.ts --confirm",
    );
    process.exit(1);
  }
  if (!isR2Configured()) {
    console.error("R2 not configured — fill R2_* in the root .env first.");
    process.exit(1);
  }

  const xp = JSON.parse(
    readFileSync(resolve(ROOT, "data/migrate/export.json"), "utf8"),
  );
  const planDoc = JSON.parse(
    readFileSync(resolve(ROOT, "data/migrate/plan.json"), "utf8"),
  );
  const plan: Record<string, { files: PlannedFile[] }> = planDoc.plan;

  // Grounded metadata corrections (title/author/year) keyed by file_path.
  const overrides = METADATA_OVERRIDES;

  // 1) Clear content (NOT users) — courses delete cascades nodes + joins.
  console.log("Clearing content tables (users preserved)…");
  const allCourseIds = (await db.select({ id: courses.id }).from(courses)).map(
    (r) => r.id,
  );
  if (allCourseIds.length) {
    await db.delete(courses).where(inArray(courses.id, allCourseIds));
  }
  await db.delete(people);
  await db.delete(programs);

  // 2) Programs
  const programIdByNotion = new Map<string, string>();
  const progSlugs = new Set<string>();
  for (const p of xp.programs) {
    const [row] = await db
      .insert(programs)
      .values({
        slug: uniqueSlug(slugify(p.name), progSlugs),
        name: p.name,
        description: [p.abbreviation, p.degreeType, p.duration]
          .filter(Boolean)
          .join(" · "),
      })
      .returning();
    programIdByNotion.set(p.notionId, row.id);
  }

  // 3) People
  const personIdByNotion = new Map<string, string>();
  const peopleSlugs = new Set<string>();
  for (const p of xp.people) {
    if (!p.name) continue;
    const [row] = await db
      .insert(people)
      .values({
        slug: uniqueSlug(slugify(p.name), peopleSlugs),
        name: p.name,
        title: p.title || p.role || null,
        bio: p.department || null,
      })
      .returning();
    personIdByNotion.set(p.notionId, row.id);
  }

  // 4) Courses (+ joins)
  const courseIdByNotion = new Map<string, string>();
  for (const c of xp.courses) {
    const [row] = await db
      .insert(courses)
      .values({
        slug: c.slug,
        courseNumber: c.courseNumber,
        title: c.name,
        formerNames: c.formerNames?.length ? c.formerNames : null,
        formerCourseNumber: c.formerCourseNumber,
        type: c.type,
        credits: c.credits != null ? String(c.credits) : null,
        status: c.status,
        overview: c.overview,
        objectives: c.objectives,
        outcomes: c.outcomes,
        outline: c.outline,
        areasOfPractice: c.areasOfPractice?.length ? c.areasOfPractice : null,
        competencies: c.competencies?.length ? c.competencies : null,
      })
      .returning();
    courseIdByNotion.set(c.notionId, row.id);

    for (const pid of c.programNotionIds) {
      const programId = programIdByNotion.get(pid);
      if (programId)
        await db
          .insert(coursePrograms)
          .values({ courseId: row.id, programId })
          .onConflictDoNothing();
    }
    for (const pid of c.professorNotionIds) {
      const personId = personIdByNotion.get(pid);
      if (personId)
        await db
          .insert(coursePeople)
          .values({ courseId: row.id, personId, role: "professor" })
          .onConflictDoNothing();
    }
  }

  // 5) Files → R2 + file nodes (flat under each course)
  const totalFiles = Object.values(plan).reduce(
    (n, e) => n + e.files.filter((f) => f.exists).length,
    0,
  );
  console.log(`Uploading ${totalFiles} files to R2…`);
  let uploaded = 0;
  let skipped = 0;
  for (const [slug, entry] of Object.entries(plan)) {
    const course = xp.courses.find((c: { slug: string }) => c.slug === slug);
    const courseId = course && courseIdByNotion.get(course.notionId);
    if (!courseId) continue;
    const nodeSlugs = new Set<string>();
    let position = 0;
    for (const f of entry.files) {
      if (!f.exists) continue;
      const nodeId = randomUUID();
      const key = `courses/${courseId}/${nodeId}/${f.fileName}`;
      const mime = mimeByExt(f.fileName);
      if (await existsInR2(key)) {
        skipped++;
      } else {
        await uploadToR2(key, readFileSync(f.filePath), mime);
        uploaded++;
      }
      if ((uploaded + skipped) % 25 === 0) {
        console.log(`  …${uploaded + skipped}/${totalFiles} files`);
      }
      const ov = overrides[toArchiveRelative(f.filePath)];
      await db.insert(nodes).values({
        id: nodeId,
        courseId,
        parentId: null,
        kind: "file",
        name: f.fileName,
        slug: uniqueSlug(slugify(f.fileName), nodeSlugs),
        position: position++,
        storageKey: key,
        mimeType: mime,
        previewType: previewTypeFor(mime),
        resourceType: f.resourceType as (typeof nodes.$inferInsert)["resourceType"],
        author: ov?.author ?? f.author,
        year: ov?.year ?? null,
        description: ov?.title ?? (f.title !== f.fileName ? f.title : null),
      });
    }
  }

  console.log("MIGRATION DONE", {
    programs: programIdByNotion.size,
    people: personIdByNotion.size,
    courses: courseIdByNotion.size,
    filesUploaded: uploaded,
    filesSkipped: skipped,
  });
}

type PlannedFile = {
  title: string;
  fileName: string;
  filePath: string;
  resourceType: string;
  author: string | null;
  exists: boolean;
};

main()
  .then(() => process.exit(0))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
