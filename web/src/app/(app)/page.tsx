import Link from "next/link";
import { ArrowRight } from "@phosphor-icons/react/dist/ssr";
import { countCoursesByType } from "@/db/queries/courses";
import { getRecentFiles } from "@/db/queries/nodes";
import { COURSE_TYPES } from "@/lib/course-types";
import { FileGlyph } from "@/components/file-icon";

export default async function HomePage() {
  const [counts, recent] = await Promise.all([
    countCoursesByType(),
    getRecentFiles(8),
  ]);

  return (
    <div className="space-y-14">
      {/* Hero */}
      <section className="max-w-2xl pt-4">
        <p className="font-mono text-xs uppercase tracking-widest text-id-gray">
          Institute of Design · Knowledge Archive
        </p>
        <h1 className="mt-3 text-4xl font-semibold leading-tight tracking-tight text-ink sm:text-5xl">
          Every course.
          <br />
          Every reading.
          <span className="text-id-blue"> Kept.</span>
        </h1>
        <p className="mt-4 text-base leading-relaxed text-slate">
          A shared, view-only archive of ID course materials — organized by
          course, browsable like a drive, open to ID students and alumni.
        </p>
      </section>

      {/* Type tiles */}
      <section>
        <div className="grid gap-px overflow-hidden rounded-xl border border-id-border bg-id-border sm:grid-cols-3">
          {COURSE_TYPES.map((t) => (
            <Link
              key={t.value}
              href={`/${t.value}`}
              className="group flex flex-col justify-between bg-white p-6 transition-colors hover:bg-mist/50"
            >
              <div className="flex items-baseline justify-between">
                <h2 className="text-lg font-semibold text-ink">{t.label}</h2>
                <span className="font-mono text-xs text-id-gray">{t.credits}</span>
              </div>
              <p className="mt-1 text-sm text-slate">{t.blurb}</p>
              <div className="mt-6 flex items-center justify-between">
                <span className="font-mono text-2xl font-semibold text-ink">
                  {counts[t.value]}
                  <span className="ml-1 text-xs font-normal text-id-gray">
                    courses
                  </span>
                </span>
                <ArrowRight
                  size={18}
                  className="text-id-gray transition-transform group-hover:translate-x-1 group-hover:text-id-blue"
                />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Recently added */}
      {recent.length > 0 && (
        <section>
          <h2 className="mb-4 font-mono text-xs uppercase tracking-widest text-id-gray">
            Recently added
          </h2>
          <ul className="divide-y divide-id-border/70 rounded-lg border border-id-border">
            {recent.map((f) => (
              <li key={f.id}>
                <Link
                  href={`/${f.courseType}/${f.courseSlug}`}
                  data-testid="recent-file"
                  className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-mist/40"
                >
                  <FileGlyph preview={f.previewType} size={18} />
                  <span className="min-w-0 flex-1 truncate text-sm text-ink">
                    {f.name}
                  </span>
                  <span className="hidden truncate text-xs text-id-gray sm:block">
                    {f.courseTitle}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
