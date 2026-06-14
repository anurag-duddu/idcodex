import { eq } from "drizzle-orm";
import { db } from "../client";
import { coursePeople, people } from "../schema";

/** Professors (people) linked to a course. */
export function getProfessorsForCourse(courseId: string) {
  return db
    .select({
      id: people.id,
      slug: people.slug,
      name: people.name,
      title: people.title,
      photoKey: people.photoKey,
    })
    .from(coursePeople)
    .innerJoin(people, eq(coursePeople.personId, people.id))
    .where(eq(coursePeople.courseId, courseId));
}
