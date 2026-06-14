import "dotenv/config";
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

/**
 * Dev seed: a tiny dataset so the UI renders before the real migration.
 * File nodes point at public sample URLs (the /api/file route proxies absolute
 * URLs in dev). Idempotent: wipes only the slugs it owns, then re-inserts.
 */
const SAMPLE = {
  pdf: "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf",
  image: "https://placehold.co/1200x800/png?text=ID+Codex+Sample",
  video:
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
};

const COURSE_SLUGS = [
  "systems-and-systems-theory",
  "introduction-to-observing-users",
  "implementing-innovation",
];
const PROGRAM_SLUGS = ["mdes"];
const PEOPLE_SLUGS = ["j-faculty", "a-faculty"];

async function main() {
  // Idempotent cleanup (course delete cascades nodes + joins)
  await db.delete(courses).where(inArray(courses.slug, COURSE_SLUGS));
  await db.delete(people).where(inArray(people.slug, PEOPLE_SLUGS));
  await db.delete(programs).where(inArray(programs.slug, PROGRAM_SLUGS));

  const [mdes] = await db
    .insert(programs)
    .values({
      slug: "mdes",
      name: "Master of Design (MDes)",
      description: "The core MDes program at the Institute of Design.",
    })
    .returning();

  const [profJ, profA] = await db
    .insert(people)
    .values([
      { slug: "j-faculty", name: "J. Faculty", title: "Professor" },
      { slug: "a-faculty", name: "A. Faculty", title: "Adjunct Professor" },
    ])
    .returning();

  const [studio, workshop, seminar] = await db
    .insert(courses)
    .values([
      {
        slug: "systems-and-systems-theory",
        courseNumber: "IDN 571",
        title: "Systems & Systems Theory in Design",
        type: "studio",
        credits: "4.0",
        status: "active",
        formerNames: ["Introduction to Systems Theory"],
        overview:
          "Frameworks for thinking about complex systems in design — boundaries, feedback, leverage points, and stakeholder ecologies.",
        objectives:
          "Develop fluency with systems mapping and the vocabulary of systems theory.",
        outcomes:
          "Students can model a complex problem space and identify leverage points for intervention.",
        outline: "1. Systems basics\n2. Mapping\n3. Feedback & dynamics\n4. Intervention",
        areasOfPractice: ["Systems Strategy & Innovation"],
        competencies: ["Systems Thinking"],
      },
      {
        slug: "introduction-to-observing-users",
        courseNumber: "IDN 504",
        title: "Introduction to Observing Users",
        type: "workshop",
        credits: "3.0",
        status: "active",
        overview:
          "Field methods for observing people and synthesizing what you see into insight.",
        competencies: ["Insight Development", "Human Advocacy"],
      },
      {
        slug: "implementing-innovation",
        courseNumber: "ID 540",
        title: "Implementing Innovation",
        type: "seminar",
        credits: "1.5",
        status: "empty",
        overview:
          "Turning validated concepts into adopted change inside organizations.",
      },
    ])
    .returning();

  await db.insert(coursePeople).values([
    { courseId: studio.id, personId: profJ.id, role: "professor" },
    { courseId: workshop.id, personId: profA.id, role: "professor" },
  ]);

  await db.insert(coursePrograms).values([
    { courseId: studio.id, programId: mdes.id },
    { courseId: workshop.id, programId: mdes.id },
    { courseId: seminar.id, programId: mdes.id },
  ]);

  // Folder tree for the studio course
  const [readings, lectures] = await db
    .insert(nodes)
    .values([
      {
        courseId: studio.id,
        parentId: null,
        kind: "folder",
        name: "Readings",
        slug: "readings",
        position: 0,
      },
      {
        courseId: studio.id,
        parentId: null,
        kind: "folder",
        name: "Lectures",
        slug: "lectures",
        position: 1,
      },
    ])
    .returning();

  await db.insert(nodes).values([
    {
      courseId: studio.id,
      parentId: null,
      kind: "file",
      name: "Course Syllabus.pdf",
      slug: "course-syllabus",
      position: 2,
      storageKey: SAMPLE.pdf,
      mimeType: "application/pdf",
      previewType: "pdf",
      resourceType: "PDF",
      description: "Course syllabus and schedule.",
    },
    {
      courseId: studio.id,
      parentId: readings.id,
      kind: "file",
      name: "Cognition in the Wild.pdf",
      slug: "cognition-in-the-wild",
      position: 0,
      storageKey: SAMPLE.pdf,
      mimeType: "application/pdf",
      previewType: "pdf",
      resourceType: "Paper",
      author: "E. Hutchins",
      year: 1995,
      description: "Distributed cognition across people, artifacts, and environment.",
    },
    {
      courseId: studio.id,
      parentId: readings.id,
      kind: "file",
      name: "Systems Map.png",
      slug: "systems-map",
      position: 1,
      storageKey: SAMPLE.image,
      mimeType: "image/png",
      previewType: "image",
      resourceType: "Other",
      description: "Example systems map.",
    },
    {
      courseId: studio.id,
      parentId: lectures.id,
      kind: "file",
      name: "Week 1 Lecture.mp4",
      slug: "week-1-lecture",
      position: 0,
      storageKey: SAMPLE.video,
      mimeType: "video/mp4",
      previewType: "video",
      resourceType: "Other",
      description: "Recorded lecture — week 1.",
    },
  ]);

  console.log(
    "Seeded: 1 program, 2 people, 3 courses (studio/workshop/seminar-empty), 6 nodes.",
  );
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
