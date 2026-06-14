import { Lock } from "@phosphor-icons/react/dist/ssr";
import type { Node } from "@/db/schema";
import { CopyLinkButton } from "@/components/copy-link-button";

function Field({
  label,
  value,
}: {
  label: string;
  value?: string | number | null;
}) {
  if (value === null || value === undefined || value === "") return null;
  return (
    <div>
      <dt className="font-mono text-[11px] uppercase tracking-widest text-id-gray">
        {label}
      </dt>
      <dd className="mt-0.5 text-sm text-slate">{value}</dd>
    </div>
  );
}

export function MetadataPanel({
  node,
  courseTitle,
}: {
  node: Node;
  courseTitle?: string;
}) {
  const authorYear = [node.author, node.year].filter(Boolean).join(" · ");
  const sub = [node.resourceType, node.pageCount ? `${node.pageCount} pp` : null]
    .filter(Boolean)
    .join(" · ");

  return (
    <aside className="space-y-4 rounded-lg border border-id-border bg-white p-4 lg:sticky lg:top-20 lg:self-start">
      <div>
        <h2 className="font-medium leading-snug text-ink">{node.name}</h2>
        {sub && (
          <p className="mt-0.5 font-mono text-[11px] text-id-gray">{sub}</p>
        )}
      </div>
      <dl className="space-y-3">
        <Field label="Type" value={node.resourceType} />
        {courseTitle && <Field label="Course" value={courseTitle} />}
        <Field label="Author / Year" value={authorYear || null} />
        <Field label="Description" value={node.description} />
      </dl>
      <div className="flex items-center justify-between border-t border-id-border/70 pt-3">
        <span className="inline-flex items-center gap-1.5 text-xs text-id-gray">
          <Lock size={13} /> View-only
        </span>
        <CopyLinkButton />
      </div>
    </aside>
  );
}
