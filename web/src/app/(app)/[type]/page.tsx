import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { isCourseType, courseTypeLabel } from "@/lib/course-types";
import { listCoursesByType } from "@/db/queries/courses";
import { CourseCard } from "@/components/course-card";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ type: string }>;
}): Promise<Metadata> {
  const { type } = await params;
  return {
    title: isCourseType(type) ? `${courseTypeLabel(type)} courses` : "Courses",
  };
}

export default async function TypePage({
  params,
}: {
  params: Promise<{ type: string }>;
}) {
  const { type } = await params;
  if (!isCourseType(type)) notFound();
  const courses = await listCoursesByType(type);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          {courseTypeLabel(type)} courses
        </h1>
        <p className="mt-1 font-mono text-xs text-id-gray">
          {courses.length} course{courses.length === 1 ? "" : "s"}
        </p>
      </div>

      {courses.length === 0 ? (
        <p className="rounded-lg border border-dashed border-id-border p-10 text-center text-sm text-id-gray">
          No courses here yet.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((c) => (
            <CourseCard key={c.id} course={c} />
          ))}
        </div>
      )}
    </div>
  );
}
