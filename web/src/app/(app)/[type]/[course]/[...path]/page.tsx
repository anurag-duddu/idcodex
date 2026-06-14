import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { isCourseType, courseTypeLabel } from "@/lib/course-types";
import { getCourseBySlug } from "@/db/queries/courses";
import {
  getCourseNodes,
  resolvePath,
  buildBreadcrumb,
} from "@/db/queries/nodes";
import { Breadcrumb, type Crumb } from "@/components/breadcrumb";
import { NodeBrowser } from "@/components/node-browser";
import { FilePreview } from "@/components/file-preview";

async function resolve(type: string, course: string, path: string[]) {
  if (!isCourseType(type)) return null;
  const detail = await getCourseBySlug(type, course);
  if (!detail) return null;
  const all = await getCourseNodes(detail.course.id);
  const target = resolvePath(all, path);
  if (!target) return null;
  return { detail, all, target };
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ type: string; course: string; path: string[] }>;
}): Promise<Metadata> {
  const { type, course, path } = await params;
  const r = await resolve(type, course, path);
  return { title: r?.target.name ?? "Not found" };
}

export default async function PathPage({
  params,
  searchParams,
}: {
  params: Promise<{ type: string; course: string; path: string[] }>;
  searchParams: Promise<{ view?: string }>;
}) {
  const { type, course, path } = await params;
  const r = await resolve(type, course, path);
  if (!r) notFound();
  const { detail, all, target } = r;

  // Breadcrumb: type → course → …ancestors→ target
  const typeLabel = isCourseType(type) ? courseTypeLabel(type) : type;
  const crumbs: Crumb[] = [
    { href: `/${type}`, label: typeLabel },
    { href: `/${type}/${course}`, label: detail.course.title },
  ];
  const chain = buildBreadcrumb(all, target.id);
  let acc = `/${type}/${course}`;
  chain.forEach((n, i) => {
    acc += `/${n.slug}`;
    crumbs.push({ href: i < chain.length - 1 ? acc : undefined, label: n.name });
  });

  if (target.kind === "folder") {
    const children = all.filter((n) => n.parentId === target.id);
    const { view } = await searchParams;
    return (
      <div className="space-y-8">
        <Breadcrumb items={crumbs} />
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          {target.name}
        </h1>
        <NodeBrowser
          nodes={children}
          basePath={`/${type}/${course}/${path.join("/")}`}
          view={view}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumb items={crumbs} />
      <FilePreview node={target} courseTitle={detail.course.title} />
    </div>
  );
}
