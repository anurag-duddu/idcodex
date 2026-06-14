import Link from "next/link";
import { FolderGlyph } from "@/components/file-icon";
import type { CourseListItem } from "@/db/queries/courses";
import { cn } from "@/lib/utils";

const STATUS: Record<string, { label: string; dot: string }> = {
  active: { label: "Active", dot: "bg-emerald-500" },
  inactive: { label: "Inactive", dot: "bg-id-gray" },
  in_development: { label: "In development", dot: "bg-amber-500" },
  merged: { label: "Merged", dot: "bg-id-gray" },
  empty: { label: "Needs content", dot: "bg-id-blue" },
};

export function CourseCard({ course }: { course: CourseListItem }) {
  const href = `/${course.type}/${course.slug}`;
  const status = STATUS[course.status] ?? STATUS.active;
  const needsContent = course.status === "empty" || course.fileCount === 0;

  return (
    <Link
      href={href}
      className="group block rounded-lg border border-id-border bg-white p-4 transition hover:border-ink/30 hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-id-blue"
    >
      <div className="flex items-start justify-between">
        <FolderGlyph size={26} />
        <span className="flex items-center gap-1.5 text-[11px] text-id-gray">
          <span className={cn("size-1.5 rounded-full", status.dot)} />
          {status.label}
        </span>
      </div>

      <div className="mt-3">
        {course.courseNumber && (
          <div className="font-mono text-[11px] tracking-wide text-id-gray">
            {course.courseNumber}
          </div>
        )}
        <h3 className="mt-0.5 font-medium leading-snug text-ink">
          {course.title}
        </h3>
      </div>

      <div className="mt-2 font-mono text-xs text-id-gray">
        {needsContent ? (
          <span className="text-id-blue">＋ Contribute materials</span>
        ) : (
          `${course.fileCount} file${course.fileCount === 1 ? "" : "s"}`
        )}
      </div>

      {/* hover / focus detail */}
      <div className="grid grid-rows-[0fr] transition-all duration-200 group-hover:grid-rows-[1fr] group-focus-visible:grid-rows-[1fr]">
        <div className="overflow-hidden">
          <div className="mt-3 space-y-1 border-t border-id-border/70 pt-3 text-xs text-slate">
            <div>
              {course.credits ? `${course.credits} cr · ` : ""}
              {course.type}
            </div>
            {course.professors.length > 0 && (
              <div className="text-id-gray">{course.professors.join(", ")}</div>
            )}
            {course.overview && (
              <p className="line-clamp-2 text-id-gray">{course.overview}</p>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
