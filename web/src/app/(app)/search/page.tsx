import type { Metadata } from "next";
import { searchCourses } from "@/db/queries/courses";
import { CourseCard } from "@/components/course-card";

export const metadata: Metadata = { title: "Search" };

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();
  const results = query ? await searchCourses(query) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">Search</h1>
        {query && (
          <p className="mt-1 font-mono text-xs text-id-gray">
            {results.length} result{results.length === 1 ? "" : "s"} for “{query}”
          </p>
        )}
      </div>

      {!query ? (
        <p className="text-sm text-id-gray">
          Type a course name or number in the search bar.
        </p>
      ) : results.length === 0 ? (
        <p className="rounded-lg border border-dashed border-id-border p-10 text-center text-sm text-id-gray">
          No matches for “{query}”.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {results.map((c) => (
            <CourseCard key={c.id} course={c} />
          ))}
        </div>
      )}
    </div>
  );
}
