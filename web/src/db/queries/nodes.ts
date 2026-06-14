import { cache } from "react";
import { and, asc, desc, eq, isNull } from "drizzle-orm";
import { db } from "../client";
import { courses, nodes } from "../schema";

/* ── Pure helpers (no DB) ────────────────────────────────────────── */

type TreeNode = { id: string; parentId: string | null; slug: string };

/**
 * Walk `segments` (slugs) from the course root through the flat `list`,
 * matching each segment to a child of the previous node. Returns the final
 * node, or null if any segment doesn't resolve. Empty `segments` → null.
 */
export function resolvePath<T extends TreeNode>(
  list: T[],
  segments: string[],
): T | null {
  let parentId: string | null = null;
  let current: T | null = null;
  for (const seg of segments) {
    const match = list.find((n) => n.parentId === parentId && n.slug === seg);
    if (!match) return null;
    current = match;
    parentId = match.id;
  }
  return current;
}

/** Ancestor chain root→target (inclusive). Empty if `targetId` not found. */
export function buildBreadcrumb<T extends { id: string; parentId: string | null }>(
  list: T[],
  targetId: string,
): T[] {
  const byId = new Map(list.map((n) => [n.id, n]));
  const chain: T[] = [];
  let cur = byId.get(targetId) ?? null;
  while (cur) {
    chain.unshift(cur);
    cur = cur.parentId ? (byId.get(cur.parentId) ?? null) : null;
  }
  return chain;
}

/* ── DB-backed queries ───────────────────────────────────────────── */

/** All nodes for a course (use for in-memory path resolution + breadcrumb). */
export const getCourseNodes = cache(async (courseId: string) =>
  db
    .select()
    .from(nodes)
    .where(eq(nodes.courseId, courseId))
    .orderBy(asc(nodes.position), asc(nodes.name)),
);

/** Direct children of a folder (parentId null = course root). */
export function getChildren(courseId: string, parentId: string | null) {
  return db
    .select()
    .from(nodes)
    .where(
      and(
        eq(nodes.courseId, courseId),
        parentId === null
          ? isNull(nodes.parentId)
          : eq(nodes.parentId, parentId),
      ),
    )
    .orderBy(asc(nodes.position), asc(nodes.name));
}

/** Most recently added files across all courses (for the home page). */
export function getRecentFiles(limit = 8) {
  return db
    .select({
      id: nodes.id,
      name: nodes.name,
      slug: nodes.slug,
      previewType: nodes.previewType,
      resourceType: nodes.resourceType,
      courseTitle: courses.title,
      courseSlug: courses.slug,
      courseType: courses.type,
      createdAt: nodes.createdAt,
    })
    .from(nodes)
    .innerJoin(courses, eq(nodes.courseId, courses.id))
    .where(eq(nodes.kind, "file"))
    .orderBy(desc(nodes.createdAt))
    .limit(limit);
}

/** A single file node by id, or null. */
export async function getFileNode(id: string) {
  const rows = await db
    .select()
    .from(nodes)
    .where(and(eq(nodes.id, id), eq(nodes.kind, "file")))
    .limit(1);
  return rows[0] ?? null;
}
