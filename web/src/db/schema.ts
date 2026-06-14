import {
  pgTable,
  pgEnum,
  uuid,
  text,
  integer,
  bigint,
  numeric,
  timestamp,
  primaryKey,
  index,
  type AnyPgColumn,
} from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

/* ── Enums ───────────────────────────────────────────────────────── */
export const courseType = pgEnum("course_type", [
  "seminar",
  "workshop",
  "studio",
]);
export const courseStatus = pgEnum("course_status", [
  "active",
  "inactive",
  "in_development",
  "merged",
  "empty",
]);
export const nodeKind = pgEnum("node_kind", ["folder", "file"]);
export const previewType = pgEnum("preview_type", [
  "pdf",
  "image",
  "video",
  "office",
  "none",
]);
export const resourceType = pgEnum("resource_type", [
  "Paper",
  "Slide Deck",
  "Book",
  "Article",
  "Tool",
  "PDF",
  "Other",
]);
export const nodeStatus = pgEnum("node_status", ["published", "pending"]);
export const userRole = pgEnum("user_role", ["viewer", "admin"]);
export const userStatus = pgEnum("user_status", ["active", "pending"]);

/* ── Tables ──────────────────────────────────────────────────────── */
export const programs = pgTable("programs", {
  id: uuid("id").primaryKey().defaultRandom(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),
  description: text("description"),
});

export const people = pgTable("people", {
  id: uuid("id").primaryKey().defaultRandom(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),
  title: text("title"),
  photoKey: text("photo_key"),
  bio: text("bio"),
});

export const courses = pgTable("courses", {
  id: uuid("id").primaryKey().defaultRandom(),
  slug: text("slug").notNull().unique(),
  courseNumber: text("course_number"),
  title: text("title").notNull(),
  formerNames: text("former_names").array(),
  formerCourseNumber: text("former_course_number"),
  type: courseType("type").notNull(),
  credits: numeric("credits", { precision: 3, scale: 1 }),
  status: courseStatus("status").notNull().default("active"),
  overview: text("overview"),
  objectives: text("objectives"),
  outcomes: text("outcomes"),
  outline: text("outline"),
  areasOfPractice: text("areas_of_practice").array(),
  competencies: text("competencies").array(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
});

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  role: userRole("role").notNull().default("viewer"),
  status: userStatus("status").notNull().default("active"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
});

export const nodes = pgTable("nodes", {
  id: uuid("id").primaryKey().defaultRandom(),
  courseId: uuid("course_id")
    .notNull()
    .references(() => courses.id, { onDelete: "cascade" }),
  parentId: uuid("parent_id").references((): AnyPgColumn => nodes.id, {
    onDelete: "cascade",
  }),
  kind: nodeKind("kind").notNull(),
  name: text("name").notNull(),
  slug: text("slug").notNull(),
  position: integer("position").notNull().default(0),
  // file-only fields
  storageKey: text("storage_key"),
  mimeType: text("mime_type"),
  sizeBytes: bigint("size_bytes", { mode: "number" }),
  pageCount: integer("page_count"),
  previewType: previewType("preview_type"),
  resourceType: resourceType("resource_type"),
  author: text("author"),
  year: integer("year"),
  sourceLink: text("source_link"),
  description: text("description"),
  status: nodeStatus("status").notNull().default("published"),
  addedBy: uuid("added_by").references(() => users.id, { onDelete: "set null" }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
}, (t) => [index("nodes_course_parent_idx").on(t.courseId, t.parentId)]);

/* ── Join tables ─────────────────────────────────────────────────── */
export const coursePeople = pgTable(
  "course_people",
  {
    courseId: uuid("course_id")
      .notNull()
      .references(() => courses.id, { onDelete: "cascade" }),
    personId: uuid("person_id")
      .notNull()
      .references(() => people.id, { onDelete: "cascade" }),
    role: text("role").default("professor"),
  },
  (t) => [primaryKey({ columns: [t.courseId, t.personId] })],
);

export const coursePrograms = pgTable(
  "course_programs",
  {
    courseId: uuid("course_id")
      .notNull()
      .references(() => courses.id, { onDelete: "cascade" }),
    programId: uuid("program_id")
      .notNull()
      .references(() => programs.id, { onDelete: "cascade" }),
  },
  (t) => [primaryKey({ columns: [t.courseId, t.programId] })],
);

/* ── Relations ───────────────────────────────────────────────────── */
export const coursesRelations = relations(courses, ({ many }) => ({
  nodes: many(nodes),
  coursePeople: many(coursePeople),
  coursePrograms: many(coursePrograms),
}));

export const peopleRelations = relations(people, ({ many }) => ({
  coursePeople: many(coursePeople),
}));

export const programsRelations = relations(programs, ({ many }) => ({
  coursePrograms: many(coursePrograms),
}));

export const nodesRelations = relations(nodes, ({ one, many }) => ({
  course: one(courses, {
    fields: [nodes.courseId],
    references: [courses.id],
  }),
  parent: one(nodes, {
    fields: [nodes.parentId],
    references: [nodes.id],
    relationName: "node_parent",
  }),
  children: many(nodes, { relationName: "node_parent" }),
}));

export const coursePeopleRelations = relations(coursePeople, ({ one }) => ({
  course: one(courses, {
    fields: [coursePeople.courseId],
    references: [courses.id],
  }),
  person: one(people, {
    fields: [coursePeople.personId],
    references: [people.id],
  }),
}));

export const courseProgramsRelations = relations(coursePrograms, ({ one }) => ({
  course: one(courses, {
    fields: [coursePrograms.courseId],
    references: [courses.id],
  }),
  program: one(programs, {
    fields: [coursePrograms.programId],
    references: [programs.id],
  }),
}));

/* ── Inferred types ──────────────────────────────────────────────── */
export type Course = typeof courses.$inferSelect;
export type Person = typeof people.$inferSelect;
export type Program = typeof programs.$inferSelect;
export type Node = typeof nodes.$inferSelect;
export type User = typeof users.$inferSelect;
export type CourseTypeValue = (typeof courseType.enumValues)[number];
export type PreviewTypeValue = (typeof previewType.enumValues)[number];
