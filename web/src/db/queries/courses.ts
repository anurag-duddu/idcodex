import { cache } from "react";
import { and, asc, count, eq, ilike, inArray, or } from "drizzle-orm";
import { db } from "../client";
import {
  courses,
  coursePeople,
  coursePrograms,
  nodes,
  people,
  programs,
  type Course,
  type CourseTypeValue,
} from "../schema";
import { getChildren } from "./nodes";
import { getProfessorsForCourse } from "./people";

export type CourseListItem = Course & {
  professors: string[];
  fileCount: number;
};

/* ── Pure assembler (unit-tested) ────────────────────────────────── */
export function assembleCourseList<T extends { id: string }>(
  courseRows: T[],
  profRows: { courseId: string; name: string }[],
  countRows: { courseId: string; fileCount: number }[],
): (T & { professors: string[]; fileCount: number })[] {
  const profs = new Map<string, string[]>();
  for (const r of profRows) {
    const list = profs.get(r.courseId) ?? [];
    list.push(r.name);
    profs.set(r.courseId, list);
  }
  const counts = new Map(countRows.map((r) => [r.courseId, r.fileCount]));
  return courseRows.map((c) => ({
    ...c,
    professors: profs.get(c.id) ?? [],
    fileCount: counts.get(c.id) ?? 0,
  }));
}

/* ── DB-backed ───────────────────────────────────────────────────── */

/** Attach professor names + file counts to a set of course rows. */
async function enrichCourses(courseRows: Course[]): Promise<CourseListItem[]> {
  if (courseRows.length === 0) return [];
  const ids = courseRows.map((c) => c.id);

  const profRows = await db
    .select({ courseId: coursePeople.courseId, name: people.name })
    .from(coursePeople)
    .innerJoin(people, eq(coursePeople.personId, people.id))
    .where(inArray(coursePeople.courseId, ids));

  const countRows = await db
    .select({ courseId: nodes.courseId, fileCount: count() })
    .from(nodes)
    .where(and(inArray(nodes.courseId, ids), eq(nodes.kind, "file")))
    .groupBy(nodes.courseId);

  return assembleCourseList(
    courseRows,
    profRows,
    countRows.map((r) => ({ courseId: r.courseId, fileCount: Number(r.fileCount) })),
  );
}

/** All courses of a type, A–Z, each with professor names + file count. */
export async function listCoursesByType(
  type: CourseTypeValue,
): Promise<CourseListItem[]> {
  const courseRows = await db
    .select()
    .from(courses)
    .where(eq(courses.type, type))
    .orderBy(asc(courses.title));
  return enrichCourses(courseRows);
}

/** Basic search: courses whose title or number matches `q` (Slice 1). */
export async function searchCourses(q: string): Promise<CourseListItem[]> {
  const term = `%${q.trim()}%`;
  if (q.trim().length === 0) return [];
  const courseRows = await db
    .select()
    .from(courses)
    .where(or(ilike(courses.title, term), ilike(courses.courseNumber, term)))
    .orderBy(asc(courses.title))
    .limit(50);
  return enrichCourses(courseRows);
}

/** Count of courses per type, for the home page tiles. */
export async function countCoursesByType(): Promise<
  Record<CourseTypeValue, number>
> {
  const rows = await db
    .select({ type: courses.type, n: count() })
    .from(courses)
    .groupBy(courses.type);
  const base: Record<CourseTypeValue, number> = {
    seminar: 0,
    workshop: 0,
    studio: 0,
  };
  for (const r of rows) base[r.type] = Number(r.n);
  return base;
}

export type CourseDetail = {
  course: Course;
  professors: Awaited<ReturnType<typeof getProfessorsForCourse>>;
  programs: { id: string; slug: string; name: string }[];
  rootNodes: Awaited<ReturnType<typeof getChildren>>;
};

/** A course by type + slug, with professors, programs, and root-level nodes. */
export const getCourseBySlug = cache(async function getCourseBySlug(
  type: CourseTypeValue,
  slug: string,
): Promise<CourseDetail | null> {
  const rows = await db
    .select()
    .from(courses)
    .where(and(eq(courses.type, type), eq(courses.slug, slug)))
    .limit(1);
  const course = rows[0];
  if (!course) return null;

  const [professors, programRows, rootNodes] = await Promise.all([
    getProfessorsForCourse(course.id),
    db
      .select({ id: programs.id, slug: programs.slug, name: programs.name })
      .from(coursePrograms)
      .innerJoin(programs, eq(coursePrograms.programId, programs.id))
      .where(eq(coursePrograms.courseId, course.id)),
    getChildren(course.id, null),
  ]);

  return { course, professors, programs: programRows, rootNodes };
});
