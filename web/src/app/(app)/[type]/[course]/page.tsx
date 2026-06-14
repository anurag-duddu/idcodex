import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { isCourseType, courseTypeLabel } from "@/lib/course-types";
import { getCourseBySlug } from "@/db/queries/courses";
import { Breadcrumb } from "@/components/breadcrumb";
import { CourseHeader } from "@/components/course-header";
import { NodeBrowser } from "@/components/node-browser";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ type: string; course: string }>;
}): Promise<Metadata> {
  const { type, course } = await params;
  const detail = isCourseType(type) ? await getCourseBySlug(type, course) : null;
  return { title: detail?.course.title ?? "Course" };
}

export default async function CoursePage({
  params,
  searchParams,
}: {
  params: Promise<{ type: string; course: string }>;
  searchParams: Promise<{ view?: string }>;
}) {
  const { type, course } = await params;
  if (!isCourseType(type)) notFound();
  const detail = await getCourseBySlug(type, course);
  if (!detail) notFound();
  const { view } = await searchParams;

  return (
    <div className="space-y-8">
      <Breadcrumb
        items={[
          { href: `/${type}`, label: courseTypeLabel(type) },
          { label: detail.course.title },
        ]}
      />
      <CourseHeader detail={detail} />
      <NodeBrowser
        nodes={detail.rootNodes}
        basePath={`/${type}/${course}`}
        view={view}
      />
    </div>
  );
}
