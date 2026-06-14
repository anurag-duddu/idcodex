import "dotenv/config";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { queryDatabase, getBlocks, props, blockText } from "./notion";
import { slugify, uniqueSlug } from "@/lib/slug";

const DB = {
  programs: "e1e9407b-1556-432b-b9ef-7e277144f7bf",
  people: "757efdde-70e7-4dbc-8801-29ac2fdcbea9",
  courses: "f6d577cb-5358-468c-9981-2ede7a140638",
  resources: "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be",
};

const SECTION: Record<string, "overview" | "objectives" | "outcomes" | "outline"> =
  {
    overview: "overview",
    "learning objectives": "objectives",
    objectives: "objectives",
    "learning outcomes": "outcomes",
    outcomes: "outcomes",
    "course outline": "outline",
    outline: "outline",
  };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function parseBody(blocks: any[]) {
  const s = { overview: "", objectives: "", outcomes: "", outline: "" };
  let cur: keyof typeof s | null = null;
  for (const b of blocks) {
    if (typeof b.type === "string" && b.type.startsWith("heading")) {
      cur = SECTION[blockText(b).toLowerCase().trim()] ?? null;
      continue;
    }
    const txt = blockText(b);
    if (cur && txt) {
      const line = b.type?.includes("list_item") ? `• ${txt}` : txt;
      s[cur] += (s[cur] ? "\n" : "") + line;
    }
  }
  return {
    overview: s.overview || null,
    objectives: s.objectives || null,
    outcomes: s.outcomes || null,
    outline: s.outline || null,
  };
}

function mapType(v: string | null): "studio" | "workshop" | "seminar" {
  const t = (v ?? "").toLowerCase();
  if (t.includes("studio")) return "studio";
  if (t.includes("workshop")) return "workshop";
  return "seminar";
}

function mapStatus(v: string | null): string {
  const t = (v ?? "").toLowerCase().replace(/\s+/g, "_");
  return ["active", "inactive", "in_development", "merged", "empty"].includes(t)
    ? t
    : "active";
}

function splitList(v: string): string[] {
  return v
    .split(/[;\n]+/)
    .map((x) => x.trim())
    .filter(Boolean);
}

async function main() {
  const typeCounts: Record<string, number> = {};

  console.log("Fetching programs/people/resources…");
  const [programPages, peoplePages, resourcePages, coursePages] =
    await Promise.all([
      queryDatabase(DB.programs),
      queryDatabase(DB.people),
      queryDatabase(DB.resources),
      queryDatabase(DB.courses),
    ]);

  const programs = programPages.map((p) => ({
    notionId: p.id,
    name: props.title(p, "Name"),
    abbreviation: props.text(p, "Abbreviation"),
    degreeType: props.select(p, "Degree Type"),
    format: props.select(p, "Format"),
    duration: props.text(p, "Duration"),
    creditsRequired: props.number(p, "Credits Required"),
    status: props.select(p, "Status"),
  }));

  const people = peoplePages.map((p) => ({
    notionId: p.id,
    name: props.title(p, "Name"),
    title: props.text(p, "Title"),
    department: props.text(p, "Department"),
    role: props.select(p, "Role"),
    email: props.email(p, "Email"),
    website: props.url(p, "Website"),
    linkedin: props.url(p, "LinkedIn"),
    status: props.select(p, "Status"),
  }));

  const resources = resourcePages.map((p) => ({
    notionId: p.id,
    title: props.title(p, "Title"),
    type: props.select(p, "Type"),
    authors: props.text(p, "Author(s)"),
    link: props.url(p, "Link"),
    tags: props.multi(p, "Tags"),
    courseNotionIds: props.relationIds(p, "Courses"),
  }));

  console.log(`Fetching bodies for ${coursePages.length} courses…`);
  const usedSlugs = new Set<string>();
  const courses = [];
  for (let i = 0; i < coursePages.length; i++) {
    const p = coursePages[i];
    const name = props.title(p, "Name");
    const rawType = props.select(p, "Type");
    typeCounts[rawType ?? "(none)"] = (typeCounts[rawType ?? "(none)"] ?? 0) + 1;
    const blocks = await getBlocks(p.id);
    const body = parseBody(blocks);
    const formerNamesText = props.text(p, "Former Names");
    courses.push({
      notionId: p.id,
      name,
      slug: uniqueSlug(slugify(name), usedSlugs),
      courseNumber: props.text(p, "Course Number") || null,
      formerCourseNumber: props.text(p, "Former Course Number") || null,
      formerNames: formerNamesText ? splitList(formerNamesText) : [],
      type: mapType(rawType),
      credits: props.number(p, "Credits"),
      status: mapStatus(props.select(p, "Status")),
      category: props.select(p, "Category"),
      session: props.select(p, "Session"),
      areasOfPractice: props.multi(p, "Area of Practice"),
      competencies: props.multi(p, "Competencies"),
      programNotionIds: props.relationIds(p, "Programs"),
      professorNotionIds: props.relationIds(p, "Professors"),
      ...body,
    });
    if ((i + 1) % 25 === 0) console.log(`  …${i + 1}/${coursePages.length}`);
  }

  const outDir = resolve(process.cwd(), "../data/migrate");
  mkdirSync(outDir, { recursive: true });
  const out = {
    generatedAt: new Date().toISOString(),
    counts: {
      programs: programs.length,
      people: people.length,
      courses: courses.length,
      resources: resources.length,
    },
    programs,
    people,
    courses,
    resources,
  };
  writeFileSync(resolve(outDir, "export.json"), JSON.stringify(out, null, 2));

  console.log("\nDONE →", resolve(outDir, "export.json"));
  console.log("counts:", out.counts);
  console.log("course Type values seen:", typeCounts);
  const withBody = courses.filter((c) => c.overview).length;
  console.log(`courses with an Overview parsed: ${withBody}/${courses.length}`);
  const resWithCourse = resources.filter((r) => r.courseNotionIds.length).length;
  console.log(
    `resources linked to >=1 course: ${resWithCourse}/${resources.length}`,
  );
}

main()
  .then(() => process.exit(0))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
