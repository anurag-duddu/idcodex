import type { CourseDetail } from "@/db/queries/courses";

function Prose({ label, body }: { label: string; body: string | null }) {
  if (!body) return null;
  return (
    <div>
      <h3 className="font-mono text-xs uppercase tracking-widest text-id-gray">
        {label}
      </h3>
      <p className="mt-1.5 whitespace-pre-line text-sm leading-relaxed text-slate">
        {body}
      </p>
    </div>
  );
}

export function CourseHeader({ detail }: { detail: CourseDetail }) {
  const { course, professors, programs } = detail;

  return (
    <header className="space-y-5">
      <div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-xs text-id-gray">
          {course.courseNumber && <span>{course.courseNumber}</span>}
          <span className="capitalize">{course.type}</span>
          {course.credits && <span>{course.credits} cr</span>}
        </div>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-ink">
          {course.title}
        </h1>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate">
          {professors.length > 0 && (
            <span>{professors.map((p) => p.name).join(", ")}</span>
          )}
          {programs.length > 0 && (
            <span className="text-id-gray">
              {programs.map((p) => p.name).join(" · ")}
            </span>
          )}
        </div>
        {course.formerNames && course.formerNames.length > 0 && (
          <p className="mt-2 text-xs text-id-gray">
            Formerly: {course.formerNames.join("; ")}
            {course.formerCourseNumber ? ` (${course.formerCourseNumber})` : ""}
          </p>
        )}
      </div>

      {(course.overview ||
        course.objectives ||
        course.outcomes ||
        course.outline) && (
        <div className="grid gap-5 rounded-xl border border-id-border bg-white p-5 sm:grid-cols-2">
          <Prose label="Overview" body={course.overview} />
          <Prose label="Objectives" body={course.objectives} />
          <Prose label="Outcomes" body={course.outcomes} />
          <Prose label="Outline" body={course.outline} />
        </div>
      )}
    </header>
  );
}
